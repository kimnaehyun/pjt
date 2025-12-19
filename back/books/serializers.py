from rest_framework import serializers
from .models import Category, Book, Thread, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id','title', 'author', 'isbn', 'cover')

class BookDetailSerializer(serializers.ModelSerializer):
    class ThreadSerializer(serializers.ModelSerializer):
        class Meta:
            model = Thread
            fields = ('id','title','content','reading_date',)

    thread_set = ThreadSerializer(many=True, read_only=True)

    num_of_threads = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    def get_num_of_threads(self, obj):
        return obj.thread_set.count()

class ThreadListSerializer(serializers.ModelSerializer):
    class BookSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = ('title',)
    book = BookSerializer(read_only=True)
    class Meta:
        model = Thread
        fields = ('id','title', 'book',)
    
class ThreadDetailSerializer(serializers.ModelSerializer):
    class BookSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = ('title',)
    book = BookSerializer(read_only=True)


    class CommentSerializer(serializers.ModelSerializer):
        class ThreadSerializer(serializers.ModelSerializer):
            class Meta:
                model = Thread
                fields = ('title',)

        thread = ThreadSerializer(read_only=True)
        class Meta:
            model =Comment
            fields= ('id', 'thread', 'content', 'created_at', 'updated_at',)

    comments = CommentSerializer(many=True, read_only=True)
    num_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = '__all__'

    def get_num_of_comments(self, obj):
        return obj.comments.count()