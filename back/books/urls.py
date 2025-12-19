from django.urls import path
from books import views

urlpatterns = [
    path('books/', views.book_list ),
    path('categorys/', views.category_list),
    path('books/<int:book_pk>/', views.book_detail),
    path('threads/', views.thread_list),
    path('threads/<int:thread_pk>/', views.thread_detail),
]
