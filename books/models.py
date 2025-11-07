from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Book(models.Model):
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    review = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="리뷰 점수 (0~10)"
    )
    author = models.CharField(max_length=100)


class Thread(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="threads"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    reading_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
