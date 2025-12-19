from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Category, Book, Thread, Comment
from .serializers import ThreadDetailSerializer, ThreadListSerializer, BookDetailSerializer, BookListSerializer, BookSerializer, CategorySerializer, ThreadSerializer, CommentSerializer
from django.shortcuts import get_list_or_404, get_object_or_404
# Create your views here.
@api_view(['GET'])
def category_list(request):
    # 전체 게시글 데이터 조회
    categorys = Category.objects.all()
    # Serialization 진행
    serializer = CategorySerializer(categorys, many=True)
    # serializer 덩어리에서 데이터 추출 (.data 속성)한 것을 응답
    return Response(serializer.data)

@api_view(['GET'])
def book_list(request):
    # 전체 게시글 데이터 조회
    books = get_list_or_404(Book)
    # Serialization 진행
    serializer = BookListSerializer(books, many=True)
    # serializer 덩어리에서 데이터 추출 (.data 속성)한 것을 응답
    return Response(serializer.data)

@api_view(['GET'])
def book_detail(request,book_pk):
    book = get_object_or_404(Book, pk =book_pk)
    serializer = BookDetailSerializer(book)
    return Response(serializer.data)

@api_view(['GET'])
def thread_list(request):
    thread = get_list_or_404(Thread)
    serializer = ThreadListSerializer(thread, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def thread_detail(request, thread_pk):
    # 1. 단일 댓글 조회
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.method == 'GET':
        # 2. 단일 댓글 데이터를 직렬화
        serializer = ThreadDetailSerializer(thread)
        # 3. 가공된 데이터 덩어리에서 json 데이터를 추출
        return Response(serializer.data)

    elif request.method == 'PUT':
        # 1. 사용자 입력 데이터 + 기존 댓글 데이터를 함께 직렬화
        serializer = ThreadDetailSerializer(thread, data=request.data)
        # 2. 유효성 검사
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        thread.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)