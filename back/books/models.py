from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=20)

class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)  # 책 제목
    description = models.TextField()  # 책 설명
    isbn = models.CharField(max_length=13, unique=True)  # ISBN, 고유 번호
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)  # 책 표지 이미지
    publisher = models.CharField(max_length=100)  # 출판사
    pub_date = models.DateField()  # 출판일
    author = models.CharField(max_length=200)  # 저자
    customer_review_rank = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 고객 리뷰 평점

class Thread(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    content = models.CharField(max_length=200)
    reading_date = models.DateField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    