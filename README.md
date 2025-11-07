# Branch 전략
우리는 GitHub Flow 방식을 기본으로 사용한다.

- master : 제품 배포용 안정 브랜치
- feature/{기능명} : 기능 개발 브랜치
    예) feature/login, feature/post-create
- hotfix/{이슈명} : 배포 중 발생한 긴급 버그 수정 브랜치

# Branch 생성 및 Merge 규칙
1. 모든 작업은 feature 브랜치에서 진행한다.
2. 기능 개발이 완료되면 Pull Request(PR)을 생성한다.
3. 다른 팀원이 코드 리뷰 후 승인하면 master에 merge한다.
4. merge 시 squash merge를 사용하여 commit 내역을 정리한다.

# Commit 메시지 규칙
Commit 메시지는 작업의 목적이 드러나도록 명확하게 작성한다.

형식:
<타입>: <요약 설명>

타입 예시:
feat  : 새로운 기능 추가
fix   : 버그 수정
docs  : 문서 수정
style : 코드 포맷팅, 세미콜론 누락 등 기능 영향 없는 변경
refactor : 코드 개선
test  : 테스트 관련 작업
chore : 빌드 설정, 패키지 관리 등의 잡무 변경

예)
feat: 로그인 페이지 UI 구현
fix: 회원가입 시 이메일 중복 체크 오류 해결
refactor: PostList 컴포넌트 렌더링 코드 개선

# Commit 시점 원칙
- 기능 단위로 commit 한다 (너무 큰 덩어리 X).
- 단, UI + 기능이 완전하지 않아도 구성 요소가 완료되면 중간 commit 허용.
