# backend/accounts/views.py

from django.contrib.auth import get_user_model, authenticate
from django.db import IntegrityError
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from api.serializers import BookSerializer

from .serializers import UserSerializer, UserUpdateSerializer
from api.models import Book

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    """
    signup/login 만 AllowAny
    """

    @action(
        detail=False,
        methods=['post'],
        url_path='signup',
        permission_classes=[permissions.AllowAny]
    )
    def signup(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name', '')
        
        if not email or not password:
            return Response(
                {'error': 'email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 이메일 중복 체크
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # username은 email에서 자동 생성 (@ 앞부분 사용)
            username = email.split('@')[0]
            # username 중복시 숫자 추가
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                name=name,
                nickname=request.data.get('nickname', ''),
                age=request.data.get('age'),
                phone=request.data.get('phone', ''),
                birthdate=request.data.get('birthdate'),
                address=request.data.get('address', ''),
                occupation=request.data.get('occupation', ''),
                gender=request.data.get('gender', ''),
                interests=request.data.get('interests', '')
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 감정 태그 기능 제거 — 더 이상 수집하지 않음

        token, _ = Token.objects.get_or_create(user=user)
        serialized_user = UserSerializer(user, context={'request': request})

        return Response({
            'token': token.key,
            'user': serialized_user.data
        })

    @action(
        detail=False,
        methods=['post'],
        url_path='login',
        permission_classes=[permissions.AllowAny]
    )
    def login(self, request):
        """
        POST /api/auth/login
        { "email":"...", "password":"..." }
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 이메일로 사용자 찾기
        try:
            user = User.objects.get(email=email)
            # 비밀번호 확인
            if not user.check_password(password):
                user = None
        except User.DoesNotExist:
            user = None
        
        if user is None:
            return Response(
                {'error': 'invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        serialized_user = UserSerializer(user, context={'request': request})

        return Response({
            'token': token.key,
            'user': serialized_user.data
        })

class UserViewSet(viewsets.ModelViewSet):
    """
    사용자 정보 조회/수정 + 읽음/찜 토글
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    lookup_field = 'pk'

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """
        GET  /api/auth/users/me     → 현재 사용자 정보 반환  
        PATCH /api/auth/users/me    → 사용자 정보 업데이트
        """
        if request.method == 'GET':
            serializer = UserSerializer(request.user, context={'request': request})
            return Response(serializer.data)

        # PATCH
        update_serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        update_serializer.is_valid(raise_exception=True)
        update_serializer.save()

        # 변경된 정보 다시 반환
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post', 'delete'], url_path=r'me/favorites/(?P<book_pk>[^/.]+)')
    def favorites(self, request, book_pk=None):
        """
        POST   /api/auth/users/me/favorites/{book_pk}   → 찜 추가  
        DELETE /api/auth/users/me/favorites/{book_pk}   → 찜 해제
        """
        user = request.user
        try:
            book = Book.objects.get(pk=book_pk)
        except Book.DoesNotExist:
            return Response({'detail': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            user.favorites.add(book)
            return Response({'detail': 'Added to favorites.'}, status=status.HTTP_201_CREATED)

        user.favorites.remove(book)
        return Response({'detail': 'Removed from favorites.'}, status=status.HTTP_204_NO_CONTENT)
    
     # 추가된 부분: 찜한 도서 목록을 반환하는 GET 요청
    @action(detail=False, methods=['get'], url_path='me/favorites')
    def get_favorites(self, request):
        """
        GET /api/auth/users/me/favorites → 찜한 도서 목록 반환
        """
        user = request.user
        books = user.favorites.all()  # 유저가 찜한 도서 목록을 가져옵니다.
        serialized_books = BookSerializer(books, many=True, context={'request': request})
        return Response(serialized_books.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'delete'], url_path=r'me/read_books/(?P<book_pk>[^/.]+)')
    def read_books(self, request, book_pk=None):
        """
        POST   /api/auth/users/me/read_books/{book_pk}   → 읽음 추가  
        DELETE /api/auth/users/me/read_books/{book_pk}   → 읽음 해제
        """
        user = request.user
        try:
            book = Book.objects.get(pk=book_pk)
        except Book.DoesNotExist:
            return Response({'detail': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            user.read_books.add(book)
            return Response({'detail': 'Marked as read.'}, status=status.HTTP_201_CREATED)

        user.read_books.remove(book)
        return Response({'detail': 'Unmarked as read.'}, status=status.HTTP_204_NO_CONTENT)