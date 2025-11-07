from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Book URLs
    path('', views.index, name='index'),
    path('create/', views.book_create, name='create'),
    path('<int:pk>/', views.book_detail, name='detail'),
    path('<int:pk>/update/', views.book_update, name='update'),
    path('<int:pk>/delete/', views.book_delete, name='delete'),

    # Thread URLs
    path('<int:book_pk>/threads/create/', views.thread_create, name='thread_create'),
    path('<int:book_pk>/threads/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('<int:book_pk>/threads/<int:pk>/update/', views.thread_update, name='thread_update'),
    path('<int:book_pk>/threads/<int:pk>/delete/', views.thread_delete, name='thread_delete'),
]
