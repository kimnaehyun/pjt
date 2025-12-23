# api/management/commands/update_similar_books.py

import os
import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Book
from api.utils import get_upstage_embedding


class Command(BaseCommand):
    help = '모든 도서에 대해 임베딩을 생성·업데이트하고, 유사도 상위 4권을 similar_books에 저장합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--k',
            type=int,
            default=4,
            help='각 도서에 대해 저장할 유사 도서 개수(기본: 4)',
        )
        parser.add_argument(
            '--create-embeddings',
            action='store_true',
            help='임베딩이 없는 도서에 대해 Upstage 임베딩을 생성(네트워크/API 필요). 기본은 생성하지 않음.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='처리할 도서 수 제한(0이면 전체). 디버깅용.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('유사 도서 업데이트 시작...'))

        k = int(options.get('k') or 4)
        if k < 1:
            k = 1
        create_embeddings = bool(options.get('create_embeddings'))
        limit = int(options.get('limit') or 0)

        # 모든 도서 로드
        qs = Book.objects.all()
        if limit and limit > 0:
            qs = qs.order_by('id')[:limit]
        books = list(qs)
        if len(books) < 2:
            self.stdout.write(self.style.WARNING('도서가 2권 미만이라 유사도 계산을 건너뜁니다.'))
            return

        def _ensure_embedding(book: Book) -> list[float] | None:
            if book.embedding:
                return book.embedding
            if not create_embeddings:
                return None
            text = f"{book.title} {book.description or ''}".strip()
            if not text:
                return None
            try:
                emb = get_upstage_embedding(text)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  ! 임베딩 실패: "{book.title}" ({e})'))
                return None
            book.embedding = emb
            book.save(update_fields=['embedding'])
            self.stdout.write(f'  - [임베딩 생성] "{book.title}"')
            return emb

        # 1) 각 도서 임베딩 생성 또는 로드
        embeddings: list[list[float] | None] = []
        for book in books:
            embeddings.append(_ensure_embedding(book))

        # 2) 각 도서에 대해 유사도 계산 및 similar_books 설정
        # - 임베딩이 없는 도서는 장르/카테고리 기반 fallback
        idx_with_vec = [i for i, e in enumerate(embeddings) if isinstance(e, list) and len(e) > 0]
        matrix = None
        if idx_with_vec:
            try:
                matrix = np.array([embeddings[i] for i in idx_with_vec], dtype=float)
            except Exception:
                matrix = None

        normed = None
        if matrix is not None and matrix.size > 0:
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            normed = matrix / norms

        def _fallback_candidates(base: Book) -> list[int]:
            # Prefer same genre, then same category, then anything.
            same_genre = [b.id for b in books if b.id != base.id and base.genre_id and b.genre_id == base.genre_id]
            same_cat = [b.id for b in books if b.id != base.id and base.category_id and b.category_id == base.category_id]
            any_others = [b.id for b in books if b.id != base.id]

            out: list[int] = []
            for pool in (same_genre, same_cat, any_others):
                for bid in pool:
                    if bid not in out:
                        out.append(bid)
                    if len(out) >= k:
                        return out[:k]

            return out[:k]

        # Map book index -> row index in normed matrix
        row_of = {book_idx: row_idx for row_idx, book_idx in enumerate(idx_with_vec)}

        for idx, book in enumerate(books):
            top_ids: list[int] = []

            if normed is not None and idx in row_of:
                row_idx = row_of[idx]
                sims = normed @ normed[row_idx]
                # Exclude itself
                sims[row_idx] = -1.0

                # Take top 4 among books that have embeddings
                top_rows = np.argsort(-sims)[:8]  # take a few extra then map/dedupe
                for r in top_rows:
                    if sims[r] <= 0:
                        continue
                    candidate_book_idx = idx_with_vec[int(r)]
                    candidate_id = books[candidate_book_idx].id
                    if candidate_id != book.id and candidate_id not in top_ids:
                        top_ids.append(candidate_id)
                    if len(top_ids) >= 4:
                        break

            if len(top_ids) < k:
                for bid in _fallback_candidates(book):
                    if bid not in top_ids:
                        top_ids.append(bid)
                    if len(top_ids) >= k:
                        break

            with transaction.atomic():
                book.similar_books.set(top_ids[:k])
            self.stdout.write(f'  - [추천 설정] "{book.title}": {top_ids[:k]}')

        self.stdout.write(self.style.SUCCESS('유사 도서 업데이트 완료!'))