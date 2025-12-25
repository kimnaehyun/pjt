from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Book, Author, Category, Genre, Review
from .serializers import (
    BookSerializer,
    SimilarBookSerializer,
    AuthorSerializer,
    CategorySerializer,
    SimpleCategorySerializer,
    GenreSerializer,
    SimpleGenreSerializer,
    ReviewSerializer,
)
from django.conf import settings
import re
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import hashlib
import random
from django.core.cache import cache


def _looks_like_openai_key(value: str | None) -> bool:
    if not value:
        return False
    # Common OpenAI key prefixes
    return value.startswith('sk-')

# ────────────────────────────────────────────────────────────────────────────────
#                       도서 CRUD + 추천 도서 endpoint
# ────────────────────────────────────────────────────────────────────────────────
class BookViewSet(viewsets.ModelViewSet):
    """
    도서 CRUD (읽기: 모두, 쓰기/수정/삭제: 인증 사용자)
    retrieve 시에는 nested로 추천 도서(similar_books) 정보 포함
    추가로 /api/books/{pk}/similar/ 로 추천 도서 4권만 반환
    """
    queryset = Book.objects.select_related('author', 'category', 'genre')\
                           .prefetch_related('similar_books')\
                           .all()\
                           .order_by('id')
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'genre']
    search_fields = ['title', 'author__name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'similar', 'best_sellers', 'top_recommended', 'age_based', 'ai_search']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='ai-search')
    def ai_search(self, request):
        """AI prompt 기반으로 DB 책 검색.

        GET /api/books/ai-search/?prompt=...&nonce=...
        Returns: list[Book]
        """
        prompt_in = str(request.query_params.get('prompt') or '').strip()
        if not prompt_in:
            return Response([], status=status.HTTP_200_OK)

        nonce = request.query_params.get('nonce')
        base_qs = Book.objects.select_related('author', 'category', 'genre').all()

        model = getattr(settings, 'OPENAI_MODEL', None) or 'gpt-5-mini'
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        gms_key = getattr(settings, 'GMS_KEY', None)
        base_url = getattr(settings, 'OPENAI_BASE_URL', None)

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
            return Response(
                {
                    'detail': 'AI 검색이 설정되지 않았습니다. OPENAI_API_KEY 또는 GMS_KEY를 설정해주세요.',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            from openai import OpenAI
        except ModuleNotFoundError:
            return Response(
                {
                    'detail': 'OpenAI SDK가 설치되어 있지 않습니다. back/requirements.txt에 openai를 추가하고 설치해주세요.',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

        # Ask model to output search keywords or titles only.
        # NOTE: Per product decision, do not incorporate user profile/favorites/read history here.
        ai_prompt = (
            "You are a helpful assistant that maps a user's natural language book request to search keywords. "
            "Return up to 10 short keywords or book titles, one per line, and nothing else.\n\n"
        )
        if nonce:
            ai_prompt += f"Nonce: {nonce}\n"
        ai_prompt += f"User request: {prompt_in}\n"

        # Fetch all books from DB and ask GPT to select matching ones
        try:
            books_list = Book.objects.select_related('author', 'category', 'genre').all()[:200]
            
            # Build book catalog for GPT
            book_catalog = "Here are books in our database:\n"
            for b in books_list:
                author_name = (b.author.name if b.author else 'Unknown') or 'Unknown'
                book_catalog += f"{b.id}. Title: {b.title}, Author: {author_name}\n"
            
            gpt_prompt = (
                f"{book_catalog}\n"
                f"User request: {prompt_in}\n"
                f"Return ONLY the book IDs (as integers, comma-separated) that match the user request. No other text."
            )

            try:
                resp = client.responses.create(
                    model=model,
                    input=[{'role': 'user', 'content': gpt_prompt}],
                    max_output_tokens=500,
                    reasoning={"effort": "minimal"},
                    text={"verbosity": "low"},
                )
                id_text = (getattr(resp, 'output_text', '') or '').strip()
                
                if id_text:
                    # Parse comma-separated IDs
                    id_matches = re.findall(r'\d+', id_text)
                    book_ids = [int(bid) for bid in id_matches]
                    
                    if book_ids:
                        qs = Book.objects.filter(id__in=book_ids).select_related('author', 'category', 'genre')
                        data = BookSerializer(qs, many=True, context={'request': request}).data
                        if data:
                            return Response(data)
            except Exception:
                pass
        except Exception:
            pass

        try:
            resp = client.responses.create(
                model=model,
                input=[{'role': 'user', 'content': ai_prompt}],
                max_output_tokens=220,
                reasoning={"effort": "minimal"},
                text={"verbosity": "low"},
            )
            text = (getattr(resp, 'output_text', '') or '').strip()
        except Exception:
            return Response(
                {
                    'detail': 'AI 검색 중 오류가 발생했습니다. API Key/BASE_URL/MODEL 설정을 확인해주세요.',
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        terms = []
        for line in text.splitlines():
            s = line.strip()
            if not s:
                continue
            s = re.sub(r'^[\d\)\.\-\s]+', '', s).strip()
            if len(s) < 2:
                continue
            terms.append(s)
            if len(terms) >= 10:
                break

        if not terms:
            return Response(
                {
                    'detail': 'AI가 검색 키워드를 생성하지 못했습니다. prompt를 더 구체적으로 입력해주세요.',
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Convert terms to DB query
        q = Q()
        for t in terms:
            q |= Q(title__icontains=t) | Q(author__name__icontains=t) | Q(genre__name__icontains=t) | Q(category__name__icontains=t)

        qs = base_qs.filter(q).distinct().order_by('-global_recommend_count', 'id')[:40]
        data = BookSerializer(qs, many=True, context={'request': request}).data

        # If DB returned no results, try a lightweight Aladin ItemSearch fallback
        if not data:
            try:
                from api.services.aladin import fetch_aladin_books

                found = []
                for t in terms[:3]:
                    try:
                        items = fetch_aladin_books('ItemSearch', max_results=10, start=1, Query=t)
                    except Exception:
                        items = []
                    for it in items:
                        # basic ISBN normalization
                        isbn = (it.get('isbn13') or '').strip()
                        if not isbn:
                            raw = (it.get('isbn') or '')
                            m = re.search(r"\b(\d{13})\b", raw)
                            if m:
                                isbn = m.group(1)
                            else:
                                m2 = re.search(r"\b(\d{9}[\dXx])\b", raw)
                                if m2:
                                    isbn = m2.group(1)
                        if not isbn:
                            continue

                        title = (it.get('title') or '').strip()
                        author_name = (it.get('author') or '').strip()
                        publisher = (it.get('publisher') or '').strip()
                        cover = (it.get('cover') or '').strip()
                        desc = (it.get('description') or '').strip() or ''

                        try:
                            author, _ = Author.objects.get_or_create(name=author_name or 'Unknown')
                            book, created = Book.objects.get_or_create(
                                isbn=isbn,
                                defaults={
                                    'title': title or isbn,
                                    'author': author,
                                    'publisher': publisher,
                                    'cover_url': cover,
                                    'description': desc,
                                }
                            )
                            found.append(book)
                        except Exception:
                            # ignore DB errors in fallback
                            continue

                if found:
                    data = BookSerializer(found[:40], many=True, context={'request': request}).data
            except Exception:
                pass

        return Response(data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='similar')
    def similar(self, request, pk=None):
        """
        /api/books/{pk}/similar/ : 추천 도서 4권만 반환
        """
        book = self.get_object()
        sims = book.similar_books.all()[:4]
        serializer = SimilarBookSerializer(sims, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='best-sellers')
    def best_sellers(self, request):
        """Frontend expects: GET /api/books/best-sellers -> list[Book]."""
        qs = Book.objects.select_related('author', 'category', 'genre').all()
        # If category 1 exists, treat it as best-sellers.
        if qs.filter(category_id=1).exists():
            qs = qs.filter(category_id=1)
        qs = qs.order_by('id')[:10]
        return Response(BookSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='top-recommended')
    def top_recommended(self, request):
        """Frontend expects: GET /api/books/top-recommended -> list[Book]."""
        qs = Book.objects.select_related('author', 'category', 'genre').order_by('-global_recommend_count', 'id')[:10]
        return Response(BookSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='age-based')
    def age_based(self, request):
        """Frontend expects: GET /api/books/age-based?age=NN -> list[Book]."""
        try:
            age = int(request.query_params.get('age', '20'))
        except ValueError:
            age = 20

        qs = Book.objects.select_related('author', 'category', 'genre').all()
        # Very simple heuristic: younger -> category 2 if present; else fallback to top.
        if age < 20 and qs.filter(category_id=2).exists():
            qs = qs.filter(category_id=2).order_by('id')
        elif age >= 40 and qs.filter(category_id=3).exists():
            qs = qs.filter(category_id=3).order_by('id')
        else:
            qs = qs.order_by('-global_recommend_count', 'id')

        qs = qs[:10]
        return Response(BookSerializer(qs, many=True, context={'request': request}).data)


# ────────────────────────────────────────────────────────────────────────────────
#                       기타 읽기 전용 ViewSet
# ────────────────────────────────────────────────────────────────────────────────
class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.prefetch_related('books').all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.prefetch_related('books').all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='top10')
    def top10(self, request):
        """Return cached Top 10 books per category for the main page.

        Response: list[{id, name, books: list[Book]}]
        """
        cache_key = 'main:categories_top10:v1'
        cached = cache.get(cache_key)
        refresh = str(request.query_params.get('refresh') or '').lower() in {'1', 'true', 'yes'}
        if cached is not None and not refresh:
            return Response(cached)

        cats = Category.objects.all().order_by('id')
        payload = []
        for c in cats:
            qs = Book.objects.select_related('author', 'category', 'genre')\
                .filter(category_id=c.id)\
                .order_by('id')[:10]
            if not qs.exists():
                continue
            payload.append({
                'id': c.id,
                'name': c.name,
                'books': BookSerializer(qs, many=True, context={'request': request}).data,
            })

        # Cache for 1 hour (tune as needed). Cache resets on server restart.
        cache.set(cache_key, payload, timeout=60 * 60)
        return Response(payload)

    def get_serializer_class(self):
        # List is frequently used by the frontend; keep it lightweight.
        if self.action == 'list':
            return SimpleCategorySerializer
        return CategorySerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.prefetch_related('books').all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        # List is frequently used by the frontend; keep it lightweight.
        if self.action == 'list':
            return SimpleGenreSerializer
        return GenreSerializer


# EmotionTagViewSet removed — emotion tags are no longer used


# ────────────────────────────────────────────────────────────────────────────────
#                       리뷰 전용 커스텀 퍼미션 및 ViewSet
# ────────────────────────────────────────────────────────────────────────────────
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    SAFE_METHODS(GET, HEAD, OPTIONS)은 모두 허용,
    POST/PUT/PATCH/DELETE 등 수정 요청은 작성자(user) 본인만 허용.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('book', 'user').all()
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    def perform_create(self, serializer):
        # Save review and broadcast to book group via Channels
        """댓글 생성 후 WebSocket으로 브로드캐스트"""
        review = serializer.save(user=self.request.user)
        try:
            channel_layer = get_channel_layer()
            data = ReviewSerializer(review, context={'request': self.request}).data
            async_to_sync(channel_layer.group_send)(
                f'book_{review.book.id}',
                {
                    'type': 'review.created',
                    'review': data,
                }
            )
        except Exception:
            # Non-blocking: don't fail the request if broadcasting fails
            pass

        return review

    def perform_destroy(self, instance):
        """댓글 삭제 후 WebSocket으로 브로드캐스트"""
        book_id = instance.book.id
        review_id = instance.id
        deleted_ids = [review_id]

        # If a parent review is deleted, its replies will be cascaded.
        # Gather reply ids ahead of deletion so the frontend can remove them too.
        try:
            reply_ids = list(Review.objects.filter(parent_id=review_id).values_list('id', flat=True))
            deleted_ids.extend(reply_ids)
        except Exception:
            pass

        super().perform_destroy(instance)

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'book_{book_id}',
                {
                    'type': 'review.deleted',
                    'review_id': review_id,
                    'deleted_ids': deleted_ids,
                }
            )
        except Exception:
            pass


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_by_profile(request):
    """
    Recommend books for the authenticated user using OpenAI.
    Returns a list of serialized Book objects found in DB.
    """
    user = request.user
    # Gather profile info
    fav_qs = user.favorites.all()
    read_qs = user.read_books.all()
    exclude_ids = set(fav_qs.values_list('id', flat=True)) | set(read_qs.values_list('id', flat=True))

    fav_titles = list(fav_qs.values_list('title', flat=True))[:10]
    read_titles = list(read_qs.values_list('title', flat=True))[:20]
    occupation = getattr(user, 'occupation', '') or ''
    gender = getattr(user, 'gender', '') or ''
    interests = getattr(user, 'interests', '') or ''

    # Build prompt for OpenAI - now requesting book IDs and reasons
    # Fetch all books with relevant fields
    books_list = Book.objects.select_related('author', 'category', 'genre').all()[:300]
    
    # Build book catalog for GPT
    book_catalog = "Here are books in our database:\n"
    book_map = {}
    for b in books_list:
        author_name = (b.author.name if b.author else 'Unknown') or 'Unknown'
        description = (b.description or '')[:100]  # First 100 chars
        book_catalog += f"{b.id}. Title: {b.title}, Author: {author_name}, Description: {description}\n"
        book_map[b.id] = b
    
    nonce = request.query_params.get('nonce')
    prompt = (
        f"{book_catalog}\n"
        "You are a helpful book recommender. Given a user's profile and lists of books they've favorited and read, "
        "recommend books from the database above that this user would enjoy.\n"
        "For each book that matches the user's preferences, return: book_id|reason.\n"
        "Return ONLY comma-separated lines with format: book_id|reason. No other text. Maximum 8 books.\n\n"
    )
    if nonce:
        prompt += f"Nonce: {nonce}\n"
    prompt += f"Occupation: {occupation}\n"
    prompt += f"Gender: {gender}\n"
    prompt += f"Interests: {interests}\n\n"
    if fav_titles:
        prompt += "Favorites:\n"
        for t in fav_titles:
            prompt += f"- {t}\n"
    if read_titles:
        prompt += "\nRead books:\n"
        for t in read_titles:
            prompt += f"- {t}\n"

    model = getattr(settings, 'OPENAI_MODEL', None) or 'gpt-5-mini'
    openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
    gms_key = getattr(settings, 'GMS_KEY', None)
    base_url = getattr(settings, 'OPENAI_BASE_URL', None)

    DEFAULT_GMS_BASE_URL = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1'

    # Decide which base_url to use.
    # - If OPENAI_BASE_URL is explicitly set, respect it.
    # - Else if GMS_KEY is set, assume SSAFY GMS proxy.
    # - Else if the provided OPENAI_API_KEY does NOT look like an OpenAI key, assume it's actually a GMS key.
    if not base_url:
        if gms_key:
            base_url = DEFAULT_GMS_BASE_URL
        elif openai_api_key and not _looks_like_openai_key(openai_api_key):
            base_url = DEFAULT_GMS_BASE_URL

    # Decide which key to use for the chosen base_url.
    if base_url == DEFAULT_GMS_BASE_URL:
        api_key = gms_key or openai_api_key
    else:
        api_key = openai_api_key or gms_key

    # If OpenAI is not configured (common in local/dev), return a safe fallback list
    # so the frontend can keep functioning.
    def _fallback_list():
        qs = Book.objects.exclude(id__in=exclude_ids)
        # If the user has favorited/read everything (or exclusion yields none),
        # fall back to global recommendations so the UI still has content.
        if not qs.exists():
            qs = Book.objects.all()
        # If a nonce is provided, return a shuffled sample so "다시 추천" yields different results.
        if nonce:
            candidate_ids = list(qs.values_list('id', flat=True))
            if not candidate_ids:
                return []
            seed_src = f"{user.id}:{nonce}".encode('utf-8')
            seed = int(hashlib.sha256(seed_src).hexdigest()[:16], 16)
            rng = random.Random(seed)
            pick_count = min(8, len(candidate_ids))
            picked_ids = rng.sample(candidate_ids, pick_count)
            books_map = Book.objects.select_related('author', 'category', 'genre').in_bulk(picked_ids)
            picked = [books_map.get(i) for i in picked_ids if books_map.get(i) is not None]
            return [{'book': BookSerializer(b, context={'request': request}).data, 'reason': '추천 도서'} for b in picked]

        qs = qs.order_by('-global_recommend_count', 'id')[:8]
        return [{'book': BookSerializer(b, context={'request': request}).data, 'reason': '인기 도서'} for b in qs]

    if not api_key:
        return Response(_fallback_list())

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        return Response(_fallback_list())

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    try:
        resp = client.responses.create(
            model=model,
            input=[{'role': 'user', 'content': prompt}],
            max_output_tokens=500,
            reasoning={"effort": "minimal"},
            text={"verbosity": "low"},
        )
        text = (getattr(resp, 'output_text', '') or '').strip()
    except Exception:
        return Response(_fallback_list())

    # Parse response: expect lines like "123|The book matches because..."
    results = []
    seen_ids = set(exclude_ids)
    
    for line in text.splitlines():
        line = line.strip()
        if not line or '|' not in line:
            continue
        parts = line.split('|', 1)
        try:
            book_id = int(parts[0].strip())
            reason = parts[1].strip() if len(parts) > 1 else '추천 도서'
            
            # Skip if already seen or excluded
            if book_id in seen_ids:
                continue
                
            book = book_map.get(book_id)
            if book:
                seen_ids.add(book_id)
                book_data = BookSerializer(book, context={'request': request}).data
                results.append({
                    'book': book_data,
                    'reason': reason
                })
        except (ValueError, IndexError):
            continue

    if not results:
        results = _fallback_list()

    # Frontend expects list with book and reason
    return Response(results)


@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_by_prompt(request):
    """
    Recommend books from DB based on a user-provided prompt.
    Returns a list with each book having: { book, reason }
    """
    prompt_in = request.query_params.get('prompt', '').strip()
    if not prompt_in:
        return Response([], status=status.HTTP_400_BAD_REQUEST)

    # Fetch all books with relevant fields
    books_list = Book.objects.select_related('author', 'category', 'genre').all()[:300]
    
    # Build book catalog for GPT
    book_catalog = "Here are books in our database:\n"
    book_map = {}
    for b in books_list:
        author_name = (b.author.name if b.author else 'Unknown') or 'Unknown'
        description = (b.description or '')[:100]  # First 100 chars
        book_catalog += f"{b.id}. Title: {b.title}, Author: {author_name}, Description: {description}\n"
        book_map[b.id] = b

    nonce = request.query_params.get('nonce')
    
    # Build prompt for OpenAI
    gpt_prompt = (
        f"{book_catalog}\n"
        f"User request: {prompt_in}\n"
        f"For each book that matches the user request, return: ID | Reason.\n"
        f"Return ONLY comma-separated lines with format: book_id|reason. No other text. Maximum 10 books."
    )
    if nonce:
        gpt_prompt += f"\nNonce: {nonce}"

    model = getattr(settings, 'OPENAI_MODEL', None) or 'gpt-5-mini'
    openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
    gms_key = getattr(settings, 'GMS_KEY', None)
    base_url = getattr(settings, 'OPENAI_BASE_URL', None)

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

    # Fallback: return empty list if no API configured
    if not api_key:
        return Response([])

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        return Response([])

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    try:
        resp = client.responses.create(
            model=model,
            input=[{'role': 'user', 'content': gpt_prompt}],
            max_output_tokens=500,
            reasoning={"effort": "minimal"},
            text={"verbosity": "low"},
        )
        text = (getattr(resp, 'output_text', '') or '').strip()
    except Exception:
        return Response([])

    # Parse response: expect lines like "123|The book matches because..."
    results = []
    seen_book_ids = set()  # Track seen book IDs to prevent duplicates
    
    for line in text.splitlines():
        line = line.strip()
        if not line or '|' not in line:
            continue
        parts = line.split('|', 1)
        try:
            book_id = int(parts[0].strip())
            reason = parts[1].strip() if len(parts) > 1 else ''
            
            # Skip if already seen
            if book_id in seen_book_ids:
                continue
                
            book = book_map.get(book_id)
            if book:
                seen_book_ids.add(book_id)
                book_data = BookSerializer(book, context={'request': request}).data
                results.append({
                    'book': book_data,
                    'reason': reason
                })
        except (ValueError, IndexError):
            continue

    # If no results, return random 5 books
    if not results:
        import random
        random_books = random.sample(list(books_list), min(5, len(books_list))) if books_list else []
        for book in random_books:
            book_data = BookSerializer(book, context={'request': request}).data
            results.append({
                'book': book_data,
                'reason': '추천 도서'
            })

    return Response(results)

