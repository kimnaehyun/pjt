from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet,
    AuthorViewSet,
    CategoryViewSet,
    GenreViewSet,
    ReviewViewSet
)
from .views import recommend_by_profile, recommend_by_prompt
# music react endpoint removed

router = DefaultRouter()
router.register(r'books',       BookViewSet)
router.register(r'authors',     AuthorViewSet)
router.register(r'categories',  CategoryViewSet)
router.register(r'genres',      GenreViewSet)
router.register(r'reviews',     ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recommendations/me/', recommend_by_profile, name='recommend_by_profile'),
    path('recommendations/by-prompt/', recommend_by_prompt, name='recommend_by_prompt'),
]