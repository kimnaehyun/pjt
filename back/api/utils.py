import os


def _get_upstage_client():
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional dependency 'openai'. Install it to enable embeddings: pip install openai"
        ) from exc

    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("UPSTAGE_API_KEY is not set; cannot create Upstage embedding client")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1",
    )

def get_upstage_embedding(text: str) -> list[float]:
    """
    주어진 텍스트에 대해 Upstage API로 임베딩을 생성하여 반환합니다.

    Args:
        text (str): 임베딩을 생성할 문자열.

    Returns:
        list[float]: 생성된 임베딩 벡터.
    """
    client = _get_upstage_client()
    response = client.embeddings.create(
        input=text,
        model="embedding-query"
    )
    # 응답 데이터 구조: {'data': [{'embedding': [...]}], ...}
    return response.data[0].embedding
