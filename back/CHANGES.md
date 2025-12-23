# 백엔드 변경사항 요약

## 주요 변경사항

### 1. 인증 시스템 변경

- **이메일 기반 인증으로 전환**
  - `USERNAME_FIELD`를 `email`로 변경
  - 회원가입/로그인 시 username 대신 email 사용
  - username은 email의 @ 앞부분에서 자동 생성

### 2. User 모델 확장

새로 추가된 필드:

- `email`: 필수, 고유 필드
- `name`: 실명
- `phone`: 전화번호
- `birthdate`: 생년월일
- `address`: 주소

기존 필드 유지:

- `nickname`, `age`, `avatar`, `status_message`
- `occupation`, `gender`, `interests`
- `favorites`, `read_books`

### 3. API 엔드포인트

#### 회원가입

```
POST /api/auth/signup
Body: { "email": "...", "password": "...", "name": "..." }
Response: { "token": "...", "user": {...} }
```

#### 로그인

```
POST /api/auth/login
Body: { "email": "...", "password": "..." }
Response: { "token": "...", "user": {...} }
```

#### 내 정보 조회/수정

```
GET /api/auth/users/me
PATCH /api/auth/users/me
```

#### 도서 검색

```
GET /api/books/?search={keyword}
GET /api/books/?category={id}
GET /api/books/?genre={id}
```

#### 도서 상세 (리뷰 포함)

```
GET /api/books/{id}/
Response includes: reviews, review_count
```

#### 리뷰 CRUD

```
GET /api/reviews/?book={id}
POST /api/reviews/
PATCH /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

#### 찜/읽음 관리

```
POST /api/auth/users/me/favorites/{book_id}
DELETE /api/auth/users/me/favorites/{book_id}
GET /api/auth/me/favorites

POST /api/auth/users/me/read_books/{book_id}
DELETE /api/auth/users/me/read_books/{book_id}
```

### 4. Serializer 개선

- **BookSerializer**: `reviews`, `review_count` 필드 추가
- **ReviewSerializer**: `user_nickname` 필드 추가
- **UserSerializer**: 새로운 필드들 추가 (`name`, `phone`, `birthdate`, `address`)

### 5. 데이터베이스 변경

- 새로운 마이그레이션 생성 및 적용: `0003_user_address_user_birthdate_user_name_user_phone_and_more.py`

## 프론트엔드 연동 가이드

### 1. 회원가입 폼

```javascript
const signup = async (formData) => {
  const response = await axios.post('/api/auth/signup', {
    email: formData.email,
    password: formData.password,
    name: formData.name,
    nickname: formData.nickname,
    phone: formData.phone,
    birthdate: formData.birthdate,
    address: formData.address
  });

  // 토큰 저장
  localStorage.setItem('token', response.data.token);
};
```

### 2. 로그인

```javascript
const login = async (email, password) => {
  const response = await axios.post('/api/auth/login', {
    email,
    password
  });

  localStorage.setItem('token', response.data.token);
};
```

### 3. 인증 헤더 설정

```javascript
axios.defaults.headers.common['Authorization'] = `Token ${localStorage.getItem('token')}`;
```

### 4. 도서 검색

```javascript
const searchBooks = async (keyword) => {
  const response = await axios.get('/api/books/', {
    params: { search: keyword }
  });
  return response.data;
};
```

### 5. 도서 상세 (리뷰 포함)

```javascript
const getBookDetail = async (bookId) => {
  const response = await axios.get(`/api/books/${bookId}/`);
  // response.data.reviews - 리뷰 목록
  // response.data.review_count - 리뷰 개수
  return response.data;
};
```

### 6. 리뷰 작성

```javascript
const createReview = async (bookId, content) => {
  const response = await axios.post('/api/reviews/', {
    book: bookId,
    content: content
  }, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('token')}`
    }
  });
  return response.data;
};
```

### 7. 프로필 조회/수정

```javascript
// 조회
const getProfile = async () => {
  const response = await axios.get('/api/auth/users/me', {
    headers: {
      'Authorization': `Token ${localStorage.getItem('token')}`
    }
  });
  return response.data;
};

// 수정
const updateProfile = async (formData) => {
  const response = await axios.patch('/api/auth/users/me', formData, {
    headers: {
      'Authorization': `Token ${localStorage.getItem('token')}`
    }
  });
  return response.data;
};
```

## 환경 설정

### .env 파일

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Aladin API
ALADIN_API_KEY=your-aladin-api-key
ALADIN_BASE_URL=https://www.aladin.co.kr/ttb/api/ItemList.aspx

# OpenAI API
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# Google Maps API
GMS_KEY=your-google-maps-api-key

# Upstage API
UPSTAGE_API_KEY=your-upstage-api-key

# Database Settings
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432
```

## 서버 실행

```bash
cd back
python manage.py runserver
```

서버는 `http://127.0.0.1:8000/`에서 실행됩니다.

## CORS 설정

프론트엔드가 `http://localhost:5173`에서 실행되도록 설정되어 있습니다.
다른 포트를 사용할 경우 `settings.py`의 `CORS_ALLOWED_ORIGINS`를 수정하세요.
