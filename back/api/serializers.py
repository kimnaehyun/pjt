import re

from rest_framework import serializers

from .models import Author, Book, Category, Genre, Review


def _upgrade_cover_url(url: str | None) -> str | None:
    """Return a higher-resolution cover URL when the source is Aladin.

    Our DB currently stores Aladin `cover200` URLs (low-res). Aladin serves `cover500`
    at the same path for better quality.
    """
    if not url:
        return url
    if 'image.aladin.co.kr' not in url:
        return url
    if '/cover500/' in url:
        return url

    upgraded = re.sub(r'/cover\d+/', '/cover500/', url)
    upgraded = upgraded.replace('/cover/', '/cover500/')
    return upgraded

class SimilarBookSerializer(serializers.ModelSerializer):
    """추천 도서 카드용 최소 필드."""

    author_name = serializers.CharField(source='author.name', read_only=True)
    cover_url = serializers.SerializerMethodField()

    def get_cover_url(self, obj):
        return _upgrade_cover_url(getattr(obj, 'cover_url', None))

    class Meta:
        model = Book
        fields = ('id', 'title', 'cover_url', 'author_name')

class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name')


class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class SimpleGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')


class AuthorSerializer(serializers.ModelSerializer):
    """작가는 name-only 정책이므로 최소 필드만 반환."""

    class Meta:
        model = Author
        fields = ('id', 'name')

# EmotionTagSerializer removed (emotion tags no longer used)
# Music-related serializers removed

class BookSerializer(serializers.ModelSerializer):
    """Vue에서 바로 쓰기 쉬운 형태(id + nested object)로 직렬화."""

    similar_books = SimilarBookSerializer(many=True, read_only=True)

    cover_url = serializers.SerializerMethodField()

    author = SimpleAuthorSerializer(read_only=True)
    category = SimpleCategorySerializer(read_only=True)
    genre = SimpleGenreSerializer(read_only=True)
    reviews = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    def get_reviews(self, obj):
        # top-level reviews + nested replies
        reviews = (
            Review.objects
            .filter(book=obj, parent__isnull=True)
            .select_related('user', 'book')
            .prefetch_related('replies__user')
            .order_by('-created_at')
        )
        return ReviewWithRepliesSerializer(reviews, many=True, context=self.context).data
    
    def get_review_count(self, obj):
        return obj.review_set.count()

    def get_cover_url(self, obj):
        return _upgrade_cover_url(getattr(obj, 'cover_url', None))

    # Backward-compatible flat name fields (already used widely in Vue).
    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    genre_name = serializers.CharField(source='genre.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'publisher', 'cover_url',
            'description', 'pub_date',
            'category', 'category_name',
            'genre', 'genre_name',
            'author', 'author_name',
            'global_recommend_count',
            'similar_books',  # 추가된 추천 도서 필드
            'reviews', 'review_count',
        ]

class CategorySerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'books')

class GenreSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Genre
        fields = ('id', 'name', 'books')

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    book_cover_url = serializers.SerializerMethodField()
    book_id = serializers.IntegerField(source='book.id', read_only=True)

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        required=False,
        allow_null=True,
    )
    parent_id = serializers.IntegerField(source='parent.id', read_only=True)

    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    def get_user_avatar(self, obj):
        request = self.context.get('request')
        url = obj.user.get_avatar_url()
        return request.build_absolute_uri(url) if url else None
    
    def get_book_cover_url(self, obj):
        return _upgrade_cover_url(getattr(obj.book, 'cover_url', None))

    class Meta:
        model  = Review
        fields = [
            'id', 'book_id', 'book_cover_url', 'book',
            'parent', 'parent_id',
            'user', 'user_id', 'user_nickname', 'user_avatar', 'content', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'user_id', 'user_nickname', 'created_at', 'user_avatar']

    def validate(self, attrs):
        book = attrs.get('book')
        parent = attrs.get('parent')
        if parent is None:
            return attrs
        if book is None:
            # book is required anyway; keep error message predictable
            raise serializers.ValidationError({'book': 'book is required'})
        if parent.book_id != book.id:
            raise serializers.ValidationError({'parent': 'parent must belong to the same book'})
        if getattr(parent, 'parent_id', None) is not None:
            raise serializers.ValidationError({'parent': 'only one level of replies is supported'})
        return attrs


class ReviewReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    book_id = serializers.IntegerField(source='book.id', read_only=True)
    parent_id = serializers.IntegerField(source='parent.id', read_only=True)

    def get_user_avatar(self, obj):
        request = self.context.get('request')
        url = obj.user.get_avatar_url()
        return request.build_absolute_uri(url) if url else None

    class Meta:
        model = Review
        fields = [
            'id', 'book_id', 'parent_id',
            'user', 'user_id', 'user_nickname', 'user_avatar',
            'content', 'created_at'
        ]


class ReviewWithRepliesSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    book_cover_url = serializers.SerializerMethodField()
    book_id = serializers.IntegerField(source='book.id', read_only=True)

    parent_id = serializers.IntegerField(source='parent.id', read_only=True)
    replies = serializers.SerializerMethodField()

    def get_user_avatar(self, obj):
        request = self.context.get('request')
        url = obj.user.get_avatar_url()
        return request.build_absolute_uri(url) if url else None

    def get_book_cover_url(self, obj):
        return _upgrade_cover_url(getattr(obj.book, 'cover_url', None))

    def get_replies(self, obj):
        qs = obj.replies.select_related('user', 'book').order_by('created_at')
        return ReviewReplySerializer(qs, many=True, context=self.context).data

    class Meta:
        model = Review
        fields = [
            'id', 'book_id', 'book_cover_url',
            'parent_id',
            'user', 'user_id', 'user_nickname', 'user_avatar',
            'content', 'created_at',
            'replies',
        ]
