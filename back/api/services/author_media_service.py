import os, json, re, requests
from django.conf import settings
from openai import OpenAI


def _strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        lines = t.splitlines()
        # Drop leading ``` or ```json
        if lines:
            lines = lines[1:]
        # Drop trailing ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return t


def _extract_first_json_object(text: str) -> str | None:
    """Best-effort extraction of the first top-level JSON object from arbitrary text."""
    t = _strip_code_fences(text)
    start = t.find("{")
    if start == -1:
        return None

    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(t)):
        ch = t[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return t[start : i + 1].strip()
    return None


def _parse_author_info_payload(raw_text: str) -> dict:
    """Parse model output into {author_info: str, author_works: list} with fallbacks."""
    candidate = _strip_code_fences(raw_text)
    try:
        data = json.loads(candidate)
    except Exception:
        extracted = _extract_first_json_object(raw_text)
        if not extracted:
            return {"author_info": "", "author_works": []}
        try:
            data = json.loads(extracted)
        except Exception:
            return {"author_info": "", "author_works": []}

    # Normalize common shapes.
    if isinstance(data, dict) and "author_info" in data and "author_works" in data:
        author_info = data.get("author_info")
        if isinstance(author_info, dict):
            # Best-effort extraction if the model returned a structured object.
            author_info = author_info.get("biography") or author_info.get("summary") or ""
        elif author_info is None:
            author_info = ""

        return {
            "author_info": author_info,
            "author_works": (data.get("author_works") or []),
        }

    # Some models might wrap.
    if isinstance(data, dict) and "author" in data and isinstance(data.get("author"), dict):
        inner = data["author"]
        return {
            "author_info": (inner.get("author_info") or inner.get("summary") or ""),
            "author_works": (inner.get("author_works") or inner.get("works") or []),
        }

    return {"author_info": "", "author_works": []}


def _looks_like_openai_key(value: str | None) -> bool:
    if not value:
        return False
    return value.startswith('sk-')


def _get_openai_client() -> OpenAI | None:
    model = getattr(settings, 'OPENAI_MODEL', None) or os.getenv('OPENAI_MODEL') or 'gpt-5-mini'
    openai_api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
    gms_key = getattr(settings, 'GMS_KEY', None) or os.getenv('GMS_KEY')
    base_url = getattr(settings, 'OPENAI_BASE_URL', None) or os.getenv('OPENAI_BASE_URL')

    DEFAULT_GMS_BASE_URL = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1'

    if not base_url:
        if gms_key:
            base_url = DEFAULT_GMS_BASE_URL
        elif openai_api_key and not _looks_like_openai_key(openai_api_key):
            base_url = DEFAULT_GMS_BASE_URL

    if base_url == DEFAULT_GMS_BASE_URL:
        api_key = gms_key or openai_api_key
    else:
        api_key = openai_api_key or gms_key

    if not api_key:
        return None

    # Store model on the client instance for convenience.
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    client._livria_model = model  # type: ignore[attr-defined]
    return client

def get_wikipedia_author_image(full_name: str) -> str:
    name = re.sub(r'\s*\(.*?\)', '', full_name).strip()
    url = "https://ko.wikipedia.org/w/api.php"
    params = {
        "action":"query","format":"json","prop":"pageimages",
        "titles":name,"piprop":"original","origin":"*",
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        pages = r.json().get("query", {}).get("pages", {})
        for p in pages.values():
            if "original" in p:
                return p["original"]["source"]
    except:
        pass
    return settings.STATIC_URL + "images/default_author.png"

def get_author_info(full_name: str) -> dict:
    name = re.sub(r'\s*\(.*?\)', '', full_name).strip()
    client = _get_openai_client()
    if client is None:
        return {"author_info": "", "author_works": []}

    model = getattr(client, '_livria_model', 'gpt-5-mini')
    system  = (
        "너는 작가 정보를 생성하는 API다. 반드시 JSON 오브젝트만 출력한다. "
        "추가 설명, 마크다운, 코드펜스, 머리말/꼬리말 없이 JSON만 출력한다.\n"
        "반드시 아래 스키마/키만 사용한다(다른 키 금지):\n"
        "{\"author_info\": string, \"author_works\": string[]}\n"
        "author_info는 2~4문장, 300자 이내의 한국어 요약 문자열이다.\n"
        "author_works는 대표작 3~6개 한국어 제목 문자열 배열이다."
    )
    messages = [
        {"role":"system", "content": system},
        {"role":"user",   "content": name},
    ]
    # NOTE: On gpt-5-mini via GMS, chat.completions often returns empty message.content.
    # Use the Responses API instead.
    resp = client.responses.create(
        model=model,
        input=messages,
        max_output_tokens=450,
        reasoning={"effort": "minimal"},
        text={"verbosity": "low"},
    )

    raw = (getattr(resp, "output_text", "") or "").strip()
    parsed = _parse_author_info_payload(raw)

    if bool(os.getenv("AUTHOR_ENRICH_DEBUG")) and not (parsed.get("author_info") or "").strip():
        # Keep logs short to avoid leaking content/secrets.
        print("[author_enrich] parse_empty; raw_preview=", raw[:200].replace("\n", " "))

    return parsed
