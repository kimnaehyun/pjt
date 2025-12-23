from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "(Deprecated) Author는 name만 저장하도록 단순화되어 enrich_authors는 더 이상 사용하지 않습니다."

    def handle(self, *args, **opts):
        self.stdout.write(
            self.style.WARNING(
                "Author 모델이 name-only로 변경되어 enrich_authors 기능이 제거되었습니다.\n"
                "- 작가 이름은 update_aladin_books 실행 시 자동 생성됩니다.\n"
                "- 유사 도서 4권 생성은 update_similar_books를 실행하세요."
            )
        )
        return