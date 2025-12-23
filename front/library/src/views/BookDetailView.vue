<template>
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <button @click="goBack" class="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
      class="lucide lucide-arrow-left w-5 h-5" aria-hidden="true">
      <path d="m12 19-7-7 7-7"></path>
      <path d="M19 12H5"></path>
    </svg>
    뒤로가기
  </button>

  <div v-if="loading" class="text-center py-12">
    <p class="text-gray-600">도서 정보를 불러오는 중...</p>
  </div>

  <div v-else-if="book" class="bg-white rounded-xl shadow-lg p-8">
    <div class="grid md:grid-cols-[300px,1fr] gap-8">
      <!-- 책 표지 -->
      <div>
        <img :src="book.cover_url || defaultCover" :alt="book.title" @error="onCoverError" class="w-full rounded-lg shadow-md" />
      </div>
      
      <!-- 책 정보 -->
      <div>
        <h1 class="text-3xl font-bold mb-4 text-gray-800">{{ book.title }}</h1>
        <div class="space-y-2 mb-6">
          <p class="text-gray-600"><span class="font-semibold">저자:</span> {{ book.author?.name }}</p>
          <p class="text-gray-600"><span class="font-semibold">출판사:</span> {{ book.publisher }}</p>
          <p class="text-gray-600"><span class="font-semibold">카테고리:</span> {{ book.category?.name }}</p>
          <p class="text-gray-600"><span class="font-semibold">장르:</span> {{ book.genre?.name }}</p>
          <p class="text-gray-600"><span class="font-semibold">출판일:</span> {{ book.pub_date }}</p>
        </div>

        <!-- 책 소개 -->
        <div class="border-t pt-6">
          <h3 class="mb-4 text-gray-800 font-semibold">책 소개</h3>
          <p class="text-gray-700 leading-relaxed">
            {{ book.description || '책 소개 정보가 없습니다.' }}
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- 댓글 섹션 -->
  <div v-if="book" class="mt-8 bg-white rounded-xl shadow-lg p-8">
    <h2 class="mb-6 text-gray-800 font-semibold">댓글 ({{ book.review_count || 0 }})</h2>

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
          class="bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors px-6 py-2 flex-1" 
          :img-src="send"
          img-alt="작성"
          value="작성" 
        />
      </div>
    </form>

    <div v-else class="mb-8 text-center py-4 bg-gray-50 rounded-lg">
      <p class="text-gray-600">댓글을 작성하려면 로그인이 필요합니다.</p>
    </div>

    <div class="space-y-4">
      <div v-if="!book.reviews || book.reviews.length === 0" class="text-center text-gray-500 py-8">
        아직 댓글이 없습니다.
      </div>
      
      <div v-else v-for="review in book.reviews" :key="review.id" 
           class="border-b pb-4 last:border-b-0">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-semibold text-gray-800">{{ review.user_nickname || review.user }}</p>
            <p class="text-sm text-gray-500">{{ formatDate(review.created_at) }}</p>
          </div>
          <button 
            v-if="canDeleteReview(review)" 
            @click="handleDeleteReview(review.id)"
            class="text-red-600 hover:text-red-800 text-sm">
            삭제
          </button>
        </div>
        <p class="mt-2 text-gray-700">{{ review.content }}</p>
      </div>
    </div>
  </div>
</div>

</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { bookAPI, reviewAPI } from '@/api'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'
import send from '@/assets/imges/send.png'

const defaultCover = 'https://via.placeholder.com/300x400?text=No+Image'

const onCoverError = (e) => {
  if (e?.target?.src && e.target.src !== defaultCover) {
    e.target.src = defaultCover
  }
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const book = ref([])
const loading = ref(false)
const newReviewContent = ref('')

const isAuthenticated = computed(() => authStore.isAuthenticated)

const fetchBook = async () => {
  try {
    loading.value = true
    const response = await bookAPI.getBook(route.params.id)
    book.value = response.data
  } catch (error) {
    console.error('Failed to fetch book:', error)
  } finally {
    loading.value = false
  }
}

const handleSubmitReview = async () => {
  if (!newReviewContent.value.trim()) return
  
  try {
    await reviewAPI.createReview({
      book: book.value.id,
      content: newReviewContent.value
    })
    newReviewContent.value = ''
    // Fallback: if WebSocket is not connected, reload book data
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      await fetchBook()
    }
  } catch (error) {
    console.error('Failed to create review:', error)
    alert('댓글 작성에 실패했습니다.')
  }
}

const handleDeleteReview = async (reviewId) => {
  if (!confirm('정말 삭제하시겠습니까?')) return
  
  try {
    await reviewAPI.deleteReview(reviewId)
    // Fallback: if WebSocket is not connected, reload book data
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      await fetchBook()
    }
  } catch (error) {
    console.error('Failed to delete review:', error)
    alert('댓글 삭제에 실패했습니다.')
  }
}

const canDeleteReview = (review) => {
  return authStore.user && (review.user === authStore.user.username || review.user_id === authStore.user.id)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR') + ' ' + date.toLocaleTimeString('ko-KR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchBook()
  connectWS()
})

onUnmounted(() => {
  try { ws?.close() } catch (e) {}
})

// WebSocket for real-time reviews
let ws = null
const connectWS = () => {
  try {
    // Use backend API port for WebSocket (currently 8001)
    const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//127.0.0.1:8001/ws/books/${route.params.id}/`
    console.log('Attempting WS connection:', wsUrl)
    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected successfully')
    }

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        console.log('WS message received:', data)
        if (data.type === 'review.created' && data.review) {
          book.value.reviews = [data.review, ...(book.value.reviews || [])]
          book.value.review_count = (book.value.review_count || 0) + 1
        } else if (data.type === 'review.deleted') {
          book.value.reviews = (book.value.reviews || []).filter(r => r.id !== data.review_id)
          book.value.review_count = Math.max(0, (book.value.review_count || 1) - 1)
        }
      } catch (err) {
        console.error('WS message parse error', err)
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected, retrying in 2s...')
      setTimeout(connectWS, 2000)
    }
    ws.onerror = (err) => console.error('WebSocket error', err)
  } catch (err) {
    console.error('Failed to connect WS', err)
  }
}
</script>

<style lang="scss" scoped>

</style>