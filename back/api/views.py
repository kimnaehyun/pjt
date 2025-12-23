from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend

from .models import Book, Author, Category, Genre, Review
from .serializers import (
    BookSerializer,
    SimilarBookSerializer,
    AuthorSerializer,
    CategorySerializer,
    GenreSerializer,
    ReviewSerializer,
)
from django.conf import settings
import re


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
                           .all()
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'genre']
    search_fields = ['title', 'author__name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'similar', 'best_sellers', 'top_recommended', 'age_based']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

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


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.prefetch_related('books').all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


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
    """
    리뷰 CRUD (읽기: 모두, 쓰기/수정/삭제: 인증 사용자)
    """
    queryset = Review.objects.select_related('book', 'user').all()
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['book']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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

    # Build prompt for OpenAI
    prompt = (
        "You are a helpful book recommender. Given a user's profile and lists of books they've favorited and read, "
        "suggest up to 8 book titles that this user would enjoy. Return the recommendations as a numbered list of titles only.\n\n"
    )
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

    if not api_key:
        return Response(
            {'detail': 'Missing API key. Set OPENAI_API_KEY (or GMS_KEY for SSAFY GMS).'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        return Response(
            {'detail': "Missing optional dependency 'openai'. Install it to enable AI recommendations."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            max_completion_tokens=300,
        )
        text = (resp.choices[0].message.content or '').strip()
    except Exception as e:
        return Response({'detail': 'OpenAI request failed', 'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    # Parse titles from response
    candidates = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r'^[\d\)\.\-\s]+', '', s).strip()
        if len(s) < 2:
            continue
        candidates.append(s)

    # Match candidates to books in DB
    found = []
    # Start with excluded IDs so we never recommend already-favorited/read books.
    seen_ids = set(exclude_ids)
    for title in candidates:
        qs = Book.objects.filter(title__icontains=title)[:3]
        if not qs.exists():
            qs = Book.objects.filter(author__name__icontains=title)[:3]
        for b in qs:
            if b.id in seen_ids:
                continue
            seen_ids.add(b.id)
            found.append(BookSerializer(b, context={'request': request}).data)

    if not found:
        qs = Book.objects.exclude(id__in=exclude_ids).all()[:8]
        found = BookSerializer(qs, many=True, context={'request': request}).data

    return Response({'recommendations': found})