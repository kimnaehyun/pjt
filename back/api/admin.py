from django.contrib import admin
from .models import Category, Author, Book, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ('title', 'author', 'category', 'pub_date')
    list_filter   = ('category', 'author')
    search_fields = ('title', 'author__name', 'isbn')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('user', 'book', 'created_at')
    search_fields = ('user__username', 'book__title')

