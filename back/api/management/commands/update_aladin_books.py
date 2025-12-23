# backend/api/management/commands/update_aladin_books.py

import json
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from api.models import Book, Author, Category, Genre
from api.services.aladin import (
    fetch_best_sellers_all,
    fetch_new_items_all,
    fetch_editor_picks_all,
)

# 7개 장르 매핑
GENRE_MAP = {
    "소설/시/희곡": ["소설", "시", "희곡"],
    "경제/경영":     ["경제", "경영"],
    "자기계발":     ["자기계발", "성장", "자기"],
    "인문/교양":     ["인문", "교양", "철학", "역사"],
    "취미/실용":     ["취미", "실용", "요리", "공예"],
    "어린이/청소년": ["어린이", "청소년", "아동"],
    "과학":         ["과학", "공학", "자연"],
}

def classify_genre(raw_cat: str) -> str:
    for genre, keywords in GENRE_MAP.items():
        for kw in keywords:
            if kw in (raw_cat or ""):
                return genre
    return "인문/교양"


_ISBN13_RE = re.compile(r"\b(\d{13})\b")
_ISBN10_RE = re.compile(r"\b(\d{9}[\dXx])\b")


def normalize_isbn(item: dict) -> str:
    """Return a stable identifier for dedupe/upsert.

    Aladin responses may provide `isbn`, sometimes containing multiple values.
    Prefer ISBN-13 if possible.
    """
    raw = (item.get("isbn13") or "").strip()
    if raw and raw.isdigit() and len(raw) == 13:
        return raw

    raw = (item.get("isbn") or "").strip()
    if not raw:
        return ""

    m13 = _ISBN13_RE.search(raw)
    if m13:
        return m13.group(1)

    m10 = _ISBN10_RE.search(raw)
    if m10:
        return m10.group(1).upper()

    return ""


def looks_weird_item(title: str, author: str, isbn: str) -> bool:
    """Conservative filter for obviously bad/placeholder items."""
    if not isbn:
        return True
    if not title or len(title) < 2:
        return True
    if len(title) > 255:
        # Book.title max_length is 255
        return True
    if not author:
        return True
    # Common placeholders/noise
    lowered = title.lower()
    if lowered in {"test", "sample", "n/a"}:
        return True
    return False

class Command(BaseCommand):
    help = 'Aladin API에서 도서 동기화'

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=50,
            help='각 소스(베스트셀러/신간/블로거 추천)에서 가져올 최대 도서 수 (기본: 50)',
        )
        parser.add_argument(
            '--per-page',
            type=int,
            default=50,
            help='페이지당 가져올 개수 (알라딘 MaxResults 상한 50). 기본: 50',
        )
        parser.add_argument(
        )

    def handle(self, *args, **opts):
        total = int(opts.get('total') or 50)
        per_page = int(opts.get('per_page') or 50)

        # 1) 장르 테이블 기본값 생성
        for g in GENRE_MAP.keys():
            Genre.objects.get_or_create(name=g)

        # 2) 동기화 대상 소스
        sources = [
            ("베스트셀러",  fetch_best_sellers_all),
            ("신간",        fetch_new_items_all),
            ("블로거 추천", fetch_editor_picks_all),
        ]

        # Cross-source de-dup so the first processed source wins category.
        global_seen_isbns = set()

        for label, fn in sources:
            cat, _ = Category.objects.get_or_create(name=label)
            self.stdout.write(f"→ Sync '{label}' (최대 {total}, per_page={per_page})…")
            items = fn(total=total, per_page=per_page)

            # Per-source de-dup (API quirks) + cross-source category precedence
            seen_isbns = set()

            skipped = 0
            upserted = 0

            for idx, item in enumerate(items, start=1):
                # — 제목 정리
                raw_title = item.get("title", "").strip()
                title = re.split(r"\s*-\s*", raw_title, 1)[0]
                title = re.sub(r"\s*\(.*?\)$", "", title).strip() or raw_title

                # — ISBN 정규화 및 이상치/중복 스킵
                isbn = normalize_isbn(item)
                name = (item.get("author", "") or "").strip()
                if looks_weird_item(title=title, author=name, isbn=isbn):
                    skipped += 1
                    continue
                if isbn in seen_isbns:
                    skipped += 1
                    continue
                seen_isbns.add(isbn)

                # Category precedence: if already seen in earlier source, skip.
                if isbn in global_seen_isbns:
                    skipped += 1
                    continue
                global_seen_isbns.add(isbn)

                self.stdout.write(f"[{idx}/{len(items)}] {title}")

                # — 출간일 파싱
                pd_raw = item.get("pubDate", "") or ""
                pd_digits = "".join(ch for ch in pd_raw if ch.isdigit())
                pub_date = None
                if len(pd_digits) >= 8:
                    try:
                        pub_date = datetime.strptime(pd_digits[:8], "%Y%m%d").date()
                    except ValueError:
                        pub_date = None

                # — 작가 처리
                author, created = Author.objects.get_or_create(name=name)

                # Author 모델은 name만 저장합니다.
                # (작가 소개/이미지/대표작은 저장하지 않음)

                # — 장르 분류
                raw_catname = item.get("categoryName", "")
                gen_name = classify_genre(raw_catname)
                genre, _ = Genre.objects.get_or_create(name=gen_name)

                # — 설명(description) 기본 문구 처리
                desc = (item.get("description") or "").strip()
                if not desc:
                    desc = "아직 설명이 등록되지 않은 도서입니다."

                # — Book upsert
                defaults = {
                    "title":                  title,
                    "author":                 author,
                    "publisher":              item.get("publisher", "").strip(),
                    "cover_url":              item.get("cover", "").strip(),
                    "description":            desc,
                    "pub_date":               pub_date,
                    "genre":                  genre,
                }

                book, created_book = Book.objects.get_or_create(
                    isbn=isbn,
                    defaults={
                        **defaults,
                        "category": cat,
                        "global_recommend_count": 0,
                    },
                )

                if not created_book:
                    # Update basic fields, but do NOT override existing category.
                    for k, v in defaults.items():
                        setattr(book, k, v)
                    if book.category_id is None:
                        book.category = cat
                    if book.genre_id is None:
                        book.genre = genre
                    book.save()

                upserted += 1

            self.stdout.write(self.style.SUCCESS(f"✓ '{label}' 완료 (upserted={upserted}, skipped={skipped})"))
