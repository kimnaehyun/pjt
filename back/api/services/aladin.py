import requests
from django.conf import settings


def _clamp_max_results(value: int) -> int:
    """Aladin API MaxResults is typically capped at 50."""
    try:
        value_int = int(value)
    except Exception:
        return 50
    return max(1, min(50, value_int))


def _resolve_aladin_base_url(query_type: str) -> str:
    """Resolve correct Aladin endpoint for the given query type.

    - ItemList API is used for bestseller/new/blogbest-style lists.
    - ItemSearch API is used for keyword search.

    Many setups accidentally configure ALADIN_BASE_URL to ItemSearch.aspx.
    In that case, we transparently switch to ItemList.aspx for list QueryTypes.
    """
    configured = (getattr(settings, 'ALADIN_BASE_URL', None) or '').strip()

    # Default to ItemList (safer for our use-cases).
    default_item_list = 'https://www.aladin.co.kr/ttb/api/ItemList.aspx'
    default_item_search = 'https://www.aladin.co.kr/ttb/api/ItemSearch.aspx'

    list_query_types = {
        'Bestseller',
        'ItemNewAll',
        'BlogBest',
        # Other ItemList QueryTypes can be added here if needed.
    }

    if not configured:
        return default_item_list if query_type in list_query_types else default_item_search

    # If configured to ItemSearch but we need ItemList, swap.
    if query_type in list_query_types and configured.endswith('ItemSearch.aspx'):
        return configured.replace('ItemSearch.aspx', 'ItemList.aspx')

    return configured

def fetch_aladin_books(query_type: str, max_results: int = 50, start: int = 1, **extra):
    params = {
        'ttbkey':        settings.ALADIN_API_KEY,
        'QueryType':     query_type,
        'MaxResults':    _clamp_max_results(max_results),
        # NOTE: Aladin `start` is a page number (1..N), not an item offset.
        'start':         max(1, int(start)),
        'Cover':         'Big',
        'Output':        'JS',
        'Version':       '20131101',
        'SearchTarget':  'Book',
    }
    params.update(extra)
    base_url = _resolve_aladin_base_url(query_type)
    resp = requests.get(base_url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get('errorCode') not in (None, '0'):
        raise RuntimeError(f"Aladin API error {data['errorCode']}: {data.get('errorMessage')}")
    return data.get('item', [])


def _fetch_all(query_type: str, total: int = 50, per_page: int = 50, **extra):
    """Fetch up to `total` items across pages."""
    total = max(1, int(total))
    per_page = _clamp_max_results(per_page)
    pages = (total + per_page - 1) // per_page

    agg = []
    for page in range(1, pages + 1):
        items = fetch_aladin_books(query_type, max_results=per_page, start=page, **extra)
        if not items:
            break
        agg.extend(items)

    # De-duplicate by ISBN and trim to requested total.
    seen = set()
    unique = []
    for b in agg:
        isbn = b.get('isbn')
        if not isbn:
            continue
        if isbn in seen:
            continue
        seen.add(isbn)
        unique.append(b)
        if len(unique) >= total:
            break
    return unique

def fetch_best_sellers_all(total: int = 50, per_page: int = 50):
    return _fetch_all('Bestseller', total=total, per_page=per_page)

def fetch_new_items_all(total: int = 50, per_page: int = 50):
    return _fetch_all('ItemNewAll', total=total, per_page=per_page)

def fetch_editor_picks_all(total: int = 50, per_page: int = 50):
    return _fetch_all('BlogBest', total=total, per_page=per_page)