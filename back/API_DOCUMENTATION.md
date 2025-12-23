# API 문서

## 인증 API

### 회원가입
- **URL**: `POST /api/auth/signup`
- **인증**: 불필요
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "홍길동",
  "nickname": "길동",
  "phone": "010-1234-5678",
  "birthdate": "1990-01-01",
  "address": "서울시 강남구",
  "age": 30,
  "occupation": "student",
  "gender": "male",
  "interests": "소설, 자기계발"
}
```
- **필수 필드**: `email`, `password`
- **응답**:
```json
{
  "token": "abc123...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "홍길동",
    "nickname": "길동",
    ...
  }
}
```

### 로그인
- **URL**: `POST /api/auth/login`
- **인증**: 불필요
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- **응답**:
```json
{
  "token": "abc123...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    ...
  }
}
```

### 내 정보 조회
- **URL**: `GET /api/auth/users/me`
- **인증**: 필수 (Token)
- **헤더**: `Authorization: Token abc123...`
- **응답**:
```json
{
  "id": 1,
  "username": "user",
  "email": "user@example.com",
  "name": "홍길동",
  "nickname": "길동",
  "age": 30,
  "phone": "010-1234-5678",
  "birthdate": "1990-01-01",
  "address": "서울시 강남구",
  "status_message": "안녕하세요",
  "avatar_url": "http://...",
  "favorites": [...],
  "read_books": [...]
}
```

### 내 정보 수정
- **URL**: `PATCH /api/auth/users/me`
- **인증**: 필수 (Token)
- **Body** (모두 선택):
```json
{
  "name": "홍길동",
  "nickname": "새닉네임",
  "age": 31,
  "phone": "010-9999-9999",
  "birthdate": "1990-01-01",
  "address": "새 주소",
  "status_message": "새 상태메시지"
}
```

## 도서 API

### 도서 목록 조회
- **URL**: `GET /api/books/`
- **인증**: 불필요
- **쿼리 파라미터**:
  - `search`: 제목, 저자명으로 검색
  - `category`: 카테고리 ID로 필터
  - `genre`: 장르 ID로 필터
- **예시**: `GET /api/books/?search=달러구트&category=1`

### 도서 상세 조회
- **URL**: `GET /api/books/{id}/`
- **인증**: 불필요
- **응답**:
```json
{
  "id": 1,
  "title": "달러구트 꿈 백화점",
  "author": {
    "id": 1,
    "name": "이미예"
  },
  "cover_url": "https://...",
  "description": "책 소개...",
  "reviews": [
    {
      "id": 1,
      "user": "user1",
      "user_nickname": "닉네임",
      "content": "좋은 책이에요",
      "created_at": "2025-12-22T10:00:00Z"
    }
  ],
  "review_count": 5,
  "similar_books": [...]
}
```

### 베스트셀러
- **URL**: `GET /api/books/best-sellers/`
- **인증**: 불필요

### 추천 도서 (Top Recommended)
- **URL**: `GET /api/books/top-recommended/`
- **인증**: 불필요

### 나이별 추천
- **URL**: `GET /api/books/age-based/?age=25`
- **인증**: 불필요

### 유사 도서 (Similar Books)
- **URL**: `GET /api/books/{id}/similar/`
- **인증**: 불필요
- **응답**: 최대 4권의 유사 도서

## 리뷰 API

### 리뷰 목록 조회
- **URL**: `GET /api/reviews/`
- **인증**: 불필요
- **쿼리 파라미터**: `book={book_id}` - 특정 도서의 리뷰만 조회

### 리뷰 작성
- **URL**: `POST /api/reviews/`
- **인증**: 필수 (Token)
- **Body**:
```json
{
  "book": 1,
  "content": "정말 좋은 책이었습니다!"
}
```

### 리뷰 수정
- **URL**: `PATCH /api/reviews/{id}/`
- **인증**: 필수 (본인만 가능)
- **Body**:
```json
{
  "content": "수정된 리뷰 내용"
}
```

### 리뷰 삭제
- **URL**: `DELETE /api/reviews/{id}/`
- **인증**: 필수 (본인만 가능)

## 찜/읽음 관리 API

### 찜하기
- **URL**: `POST /api/auth/users/me/favorites/{book_id}`
- **인증**: 필수 (Token)

### 찜 해제
- **URL**: `DELETE /api/auth/users/me/favorites/{book_id}`
- **인증**: 필수 (Token)

### 찜한 도서 목록
- **URL**: `GET /api/auth/me/favorites`
- **인증**: 필수 (Token)

### 읽음 추가
- **URL**: `POST /api/auth/users/me/read_books/{book_id}`
- **인증**: 필수 (Token)

### 읽음 해제
- **URL**: `DELETE /api/auth/users/me/read_books/{book_id}`
- **인증**: 필수 (Token)

## 개인화 추천 API

### 프로필 기반 추천
- **URL**: `GET /api/recommendations/me/`
- **인증**: 필수 (Token)
- **설명**: 사용자의 찜/읽음 도서, 직업, 성별, 관심사를 기반으로 OpenAI가 추천

## 작가/카테고리/장르 API

### 작가 목록
- **URL**: `GET /api/authors/`

### 카테고리 목록
- **URL**: `GET /api/categories/`

### 장르 목록
- **URL**: `GET /api/genres/`

## 인증 방법

모든 인증이 필요한 API는 다음 헤더를 포함해야 합니다:

```
Authorization: Token {your-token-here}
```

예시:
```javascript
axios.get('/api/auth/users/me', {
  headers: {
    'Authorization': 'Token abc123def456...'
  }
})
```
