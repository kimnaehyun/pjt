# backend/api/tests.py

from django.test import TestCase
from api.services.aladin import fetch_best_sellers

class AladinServiceTest(TestCase):
    def test_fetch_best_sellers(self):
        books = fetch_best_sellers()
        # 10권을 가져오는 게 기본이므로
        self.assertIsInstance(books, list)
        self.assertEqual(len(books), 10)
        # 최소한 title 과 author 필드가 있어야 한다
        first = books[0]
        self.assertIn('title', first)
        self.assertIn('author', first)