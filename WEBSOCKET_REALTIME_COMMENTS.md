# 실시간 댓글 WebSocket 구현 가이드

## 개요
Django Channels를 사용하여 책 상세 페이지에서 댓글(리뷰)을 실시간으로 표시하는 기능입니다.
한 사용자가 댓글을 작성하면, 같은 책을 보고 있는 다른 모든 사용자에게 **실시간으로 반영**됩니다.

---

## 백엔드 구현

### 1. ASGI 설정 (`livria_backend/asgi.py`)
```python
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livria_backend.settings')

import api.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})
```

**설명:**
- `ProtocolTypeRouter`: HTTP와 WebSocket을 구분하여 라우팅
- `AuthMiddlewareStack`: WebSocket 연결 시 세션/토큰 기반 인증 처리
- `URLRouter`: WebSocket URL 패턴 매칭

---

### 2. Django 설정 (`livria_backend/settings.py`)

#### INSTALLED_APPS에 추가
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'channels',  # ← 추가
    'accounts',
    'api',
    'corsheaders',
    'rest_framework',
    # ... 나머지
]
```

#### ASGI 및 Channel Layers 설정
```python
# WSGI (기존, runserver용)
WSGI_APPLICATION = 'livria_backend.wsgi.application'

# ASGI (Channels용, uvicorn 실행 시)
ASGI_APPLICATION = 'livria_backend.asgi.application'

# Channel layers 설정
# 개발: InMemoryChannelLayer (단일 프로세스)
# 프로덕션: Redis 권장
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}
```

---

### 3. WebSocket 라우팅 (`api/routing.py`)
```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/books/(?P<book_id>\d+)/$', consumers.ReviewConsumer.as_asgi()),
]
```

**URL 패턴:** `ws://localhost:8001/ws/books/10/` → book_id = 10

---

### 4. WebSocket Consumer (`api/consumers.py`)
```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ReviewConsumer(AsyncWebsocketConsumer):
    """
    특정 책에 대한 실시간 댓글 업데이트를 처리합니다.
    - 연결 시: 해당 책의 group에 추가
    - 메시지 수신: JSON 파싱 후 클라이언트에 브로드캐스트
    - 연결 해제: group에서 제거
    """
    
    async def connect(self):
        """WebSocket 연결 수락"""
        self.book_id = self.scope['url_route']['kwargs'].get('book_id')
        self.group_name = f'book_{self.book_id}'
        
        # 같은 책을 보는 모든 클라이언트의 group에 추가
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """WebSocket 연결 종료"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # 백엔드에서 호출되는 이벤트 핸들러
    async def review_created(self, event):
        """댓글 생성 이벤트 → 클라이언트로 전송"""
        await self.send(text_data=json.dumps({
            'type': 'review.created',
            'review': event.get('review')
        }))

    async def review_deleted(self, event):
        """댓글 삭제 이벤트 → 클라이언트로 전송"""
        await self.send(text_data=json.dumps({
            'type': 'review.deleted',
            'review_id': event.get('review_id')
        }))
```

---

### 5. ViewSet에서 이벤트 브로드캐스트 (`api/views.py`)

#### 필요 import 추가
```python
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
```

#### ReviewViewSet 수정
```python
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('book', 'user').all()
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    def perform_create(self, serializer):
        """댓글 생성 후 WebSocket으로 브로드캐스트"""
        review = serializer.save(user=self.request.user)
        try:
            channel_layer = get_channel_layer()
            data = ReviewSerializer(review, context={'request': self.request}).data
            async_to_sync(channel_layer.group_send)(
                f'book_{review.book.id}',
                {
                    'type': 'review.created',
                    'review': data,
                }
            )
        except Exception:
            # 비동기 작업 실패 시에도 요청은 성공
            pass
        return review

    def perform_destroy(self, instance):
        """댓글 삭제 후 WebSocket으로 브로드캐스트"""
        book_id = instance.book.id
        review_id = instance.id
        super().perform_destroy(instance)
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'book_{book_id}',
                {
                    'type': 'review.deleted',
                    'review_id': review_id,
                }
            )
        except Exception:
            pass
```

**동작 원리:**
1. 댓글 저장
2. `channel_layer.group_send()`: book_10 group의 모든 consumer에게 이벤트 전송
3. Consumer의 `review_created()` 메서드가 자동으로 호출
4. 모든 연결된 클라이언트에게 메시지 전송

---

## 프론트엔드 구현

### 1. API 기본 URL 설정 (`src/api/index.js`)
```javascript
const api = axios.create({
  baseURL: 'http://127.0.0.1:8001/api',  // ← 포트 8001 (ASGI 서버)
  headers: {
    'Content-Type': 'application/json'
  }
})
```

---

### 2. WebSocket 클라이언트 (`src/views/BookDetailView.vue`)

#### Template (댓글 작성 폼)
```vue
<form v-if="isAuthenticated" @submit.prevent="handleSubmitReview" class="mb-8">
  <div class="flex items-center gap-2">
    <BaseInput 
      v-model="newReviewContent"
      type="text" 
      placeholder="댓글을 작성해주세요" 
      class="border-gray-300 focus:border-blue-600 focus:outline-none shadow-lg"
    />
    <BaseButton 
      type="submit" 
      class="bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors px-4 py-2 shrink-0" 
      :img-src="send"
      img-alt="작성"
      value="작성" 
    />
  </div>
</form>
```

#### Script - WebSocket 로직
```javascript
<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
let ws = null  // WebSocket 인스턴스

// ========== 댓글 작성 ==========
const handleSubmitReview = async () => {
  if (!newReviewContent.value.trim()) return
  
  try {
    await reviewAPI.createReview({
      book: book.value.id,
      content: newReviewContent.value
    })
    newReviewContent.value = ''
    
    // WebSocket이 연결되지 않으면 Fallback: 수동 새로고침
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      await fetchBook()
    }
  } catch (error) {
    console.error('Failed to create review:', error)
    alert('댓글 작성에 실패했습니다.')
  }
}

// ========== 댓글 삭제 ==========
const handleDeleteReview = async (reviewId) => {
  if (!confirm('정말 삭제하시겠습니까?')) return
  
  try {
    await reviewAPI.deleteReview(reviewId)
    
    // WebSocket이 연결되지 않으면 Fallback: 수동 새로고침
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      await fetchBook()
    }
  } catch (error) {
    console.error('Failed to delete review:', error)
    alert('댓글 삭제에 실패했습니다.')
  }
}

// ========== Lifecycle ==========
onMounted(() => {
  fetchBook()
  connectWS()
})

onUnmounted(() => {
  try { ws?.close() } catch (e) {}
})

// ========== WebSocket 연결 ==========
const connectWS = () => {
  try {
    // 프로토콜 결정 (http → ws, https → wss)
    const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//127.0.0.1:8001/ws/books/${route.params.id}/`
    
    console.log('Attempting WS connection:', wsUrl)
    ws = new WebSocket(wsUrl)

    // 연결 성공
    ws.onopen = () => {
      console.log('WebSocket connected successfully')
    }

    // 메시지 수신
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        console.log('WS message received:', data)
        
        // 댓글 생성 이벤트
        if (data.type === 'review.created' && data.review) {
          // 새 댓글을 맨 앞에 추가
          book.value.reviews = [data.review, ...(book.value.reviews || [])]
          book.value.review_count = (book.value.review_count || 0) + 1
        }
        // 댓글 삭제 이벤트
        else if (data.type === 'review.deleted') {
          // 해당 댓글 필터링
          book.value.reviews = (book.value.reviews || []).filter(r => r.id !== data.review_id)
          book.value.review_count = Math.max(0, (book.value.review_count || 1) - 1)
        }
      } catch (err) {
        console.error('WS message parse error', err)
      }
    }

    // 연결 해제 (자동 재연결)
    ws.onclose = () => {
      console.log('WebSocket disconnected, retrying in 2s...')
      setTimeout(connectWS, 2000)
    }

    // 연결 에러
    ws.onerror = (err) => console.error('WebSocket error', err)
  } catch (err) {
    console.error('Failed to connect WS', err)
  }
}
</script>
```

---

## 실행 방법

### 1. 의존성 설치

```bash
# 백엔드
cd back/back
pip install -r requirements.txt
pip install websockets wsproto  # WebSocket 라이브러리

# 프론트
cd front/library
npm install
```

### 2. 서버 실행

```bash
# 터미널 1: 백엔드 (ASGI 서버)
cd back/back
uvicorn livria_backend.asgi:application --host 127.0.0.1 --port 8000
```

```bash
# 터미널 2: 프론트
cd front/library
npm run dev
```

### 3. 테스트

1. 브라우저에서 `http://localhost:5173` 열기
2. 책 상세 페이지 접속
3. **F12 (개발자 도구) → 콘솔**에서 로그 확인:
   ```
   Attempting WS connection: ws://127.0.0.1:8001/ws/books/10/
   WebSocket connected successfully
   ```
4. **두 개의 브라우저 탭**에서 같은 책을 열기
5. 한쪽에서 댓글 작성 → **다른 쪽에서 즉시 나타남** (새로고침 없음)

---

## 필요한 패키지 (`requirements.txt`)

```
channels
channels-redis  # 프로덕션용 (다중 프로세스)
websockets
wsproto
```

---

## 프로덕션 배포 시 변경사항

### 1. Redis 설정 (다중 프로세스 지원)
```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis-server-ip', 6379)],
        },
    },
}
```

### 2. ASGI 서버 실행
```bash
# Gunicorn + Daphne (권장)
pip install daphne
daphne -b 0.0.0.0 -p 8000 livria_backend.asgi:application
```

### 3. 프론트 API URL 변경
```javascript
// src/api/index.js
const api = axios.create({
  baseURL: 'https://your-domain.com/api',  // 프로덕션 도메인
})
```

### 4. BookDetailView.vue WebSocket URL 변경
```javascript
const connectWS = () => {
  const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${location.host}/ws/books/${route.params.id}/`
  // → 자동으로 현재 도메인 사용
}
```

---

## 문제 해결

### 404 Not Found 에러
- ❌ `python manage.py runserver` 사용 중
- ✅ 반드시 `uvicorn`으로 실행 필요

### "WebSocket connected successfully" 안 뜸
- ❌ WebSocket 라이브러리 미설치
- ✅ `pip install websockets wsproto` 설치

### 포트 충돌
```bash
# 현재 포트 사용 중인 프로세스 확인
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# 프로세스 종료
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

---

## 아키텍처 요약

```
┌─────────────────────────────────────────────────┐
│ 클라이언트 A (브라우저)                          │
│  ↓                                               │
│ [WebSocket] ws://localhost:8001/ws/books/10/   │
└────────────────┬────────────────────────────────┘
                 │
           ┌─────▼─────────────────────────┐
           │ uvicorn (ASGI 서버)           │
           │                               │
           │ api.consumers.ReviewConsumer  │
           │ (book_10 group에 가입)        │
           └─────┬─────────────────────────┘
                 │
           ┌─────▼─────────────────────────┐
           │ Channel Layer                 │
           │ (메모리 또는 Redis)           │
           │                               │
           │ book_10 group:                │
           │  - Consumer A                 │
           │  - Consumer B                 │
           │  - Consumer C                 │
           └─────────────────────────────────┘
                 ▲
                 │
        [API] POST /api/reviews/
        댓글 작성 → perform_create()
        group_send('review.created')
```

---

## 참고 문서
- [Django Channels 공식 문서](https://channels.readthedocs.io/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
