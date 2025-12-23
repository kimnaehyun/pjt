<template>
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <button class="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6" @click="goBack">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
      class="lucide lucide-arrow-left w-5 h-5" aria-hidden="true">
      <path d="m12 19-7-7 7-7"></path>
      <path d="M19 12H5"></path>
    </svg>
    뒤로가기
  </button>

  <div class="bg-white rounded-xl shadow-lg p-6 md:p-8">
    <div class="grid gap-6 md:grid-cols-2 md:gap-10">
      <!-- Cover -->
      <div class="w-full">
        <div class="w-full bg-gray-200 rounded-lg overflow-hidden aspect-[3/4]">
          <img
            v-if="book?.cover_url"
            :src="book.cover_url"
            :alt="book?.title || 'book cover'"
            class="w-full h-full object-cover"
          />
        </div>
      </div>

      <!-- Info -->
      <div>
        <div class="flex items-start justify-between gap-3 mb-2">
          <h1 class="text-gray-900 text-2xl font-semibold">{{ book?.title || '' }}</h1>

          <div class="flex items-center gap-2">
            <!-- Favorite (Heart) -->
            <button
              type="button"
              class="w-10 h-10 rounded-lg border border-gray-200 bg-white flex items-center justify-center transition-colors"
              :class="isFavorited ? 'text-red-500' : 'text-gray-700 hover:text-red-500'"
              @click="toggleFavorite"
              aria-label="찜하기"
              title="찜하기"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78Z" />
              </svg>
            </button>

            <!-- Read (Book) -->
            <button
              type="button"
              class="w-10 h-10 rounded-lg border border-gray-200 bg-white flex items-center justify-center transition-colors"
              :class="isRead ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'"
              @click="toggleRead"
              aria-label="읽음 표시"
              title="읽음 표시"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" :fill="isRead ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M12 7v14" />
                <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4a4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3a3 3 0 0 0-3-3z" />
              </svg>
            </button>
          </div>
        </div>
        <p class="text-gray-700 mb-4">{{ book?.author_name || book?.author?.name || '' }}</p>

        <div class="grid sm:grid-cols-2 gap-3 text-sm">
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-gray-500">카테고리</p>
            <p class="text-gray-800">{{ book?.category_name || book?.category?.name || '-' }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-gray-500">장르</p>
            <p class="text-gray-800">{{ book?.genre_name || book?.genre?.name || '-' }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-gray-500">출판사</p>
            <p class="text-gray-800">{{ book?.publisher || '-' }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-gray-500">리뷰</p>
            <p class="text-gray-800">{{ book?.review_count ?? 0 }}</p>
          </div>
        </div>

        <!-- Description (right column) -->
        <div class="mt-8">
          <h3 class="mb-3 text-gray-800">책 소개</h3>
          <p class="text-gray-700 leading-relaxed">{{ book?.description || '책 소개가 없습니다.' }}</p>
        </div>
      </div>
    </div>

    <!-- Similar books (full width) -->
    <div v-if="book" class="mt-10 border-t pt-6">
      <h3 class="mb-4 text-gray-800">유사한 책</h3>

      <p v-if="!similarBooks4.length" class="text-gray-600 text-sm">추천 도서가 없습니다.</p>

      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-5">
        <RouterLink
          v-for="b in similarBooks4"
          :key="b.id"
          class="group"
          :to="{ name: 'bookDetail', params: { id: b.id } }"
        >
          <div class="bg-white rounded-lg border border-gray-100 overflow-hidden hover:shadow-md transition-shadow h-full">
            <div class="bg-gray-200 aspect-[3/4] overflow-hidden">
              <img
                v-if="b.cover_url"
                :src="b.cover_url"
                :alt="b.title || 'book cover'"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform"
              />
            </div>
            <div class="p-3">
              <p class="text-sm text-gray-800 line-clamp-2">{{ b.title }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ b.author_name || '' }}</p>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>

  <!-- 댓글 섹션 -->
  <div class="mt-8 bg-white rounded-xl shadow-lg p-8">
    <h2 class="mb-6 text-gray-800">댓글 ({{ book?.review_count ?? 0 }})</h2>

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

    <div class="space-y-4">
     <p v-if="!book?.reviews?.length" class="text-center text-gray-500 py-8">
  아직 댓글이 없습니다.
</p>

<div v-else class="space-y-3">
  <div v-for="r in book.reviews" :key="r.id" class="border rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-gray-800">{{ r.user_nickname || r.user || '사용자' }}</p>
            <p class="text-gray-500 text-sm">{{ formatDate(r.created_at) }}</p>
          </div>
          <p class="text-gray-700">{{ r.content }}</p>
        </div>
      </div>
    </div>
  </div>
</div>

</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'
import send from '@/assets/imges/send.png'
import { bookAPI, userBookAPI, reviewAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'

/* ================= 기본 ================= */

let ws = null

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const id = computed(() => route.params.id)

const book = ref({
  reviews: [],
  review_count: 0,
})

const newReviewContent = ref('')

const isAuthenticated = computed(() => authStore.isAuthenticated)

/* ================= computed ================= */

const similarBooks = computed(() =>
  Array.isArray(book.value.similar_books) ? book.value.similar_books : []
)

const similarBooks4 = computed(() => similarBooks.value.slice(0, 4))

const bookIdNumber = computed(() => {
  const v = Number(id.value)
  return Number.isFinite(v) ? v : null
})

const favoriteIds = computed(() => {
  const list = authStore.user?.favorites
  return new Set(Array.isArray(list) ? list.map(b => b.id) : [])
})

const readIds = computed(() => {
  const list = authStore.user?.read_books
  return new Set(Array.isArray(list) ? list.map(b => b.id) : [])
})

const isFavorited = computed(
  () => bookIdNumber.value != null && favoriteIds.value.has(bookIdNumber.value)
)

const isRead = computed(
  () => bookIdNumber.value != null && readIds.value.has(bookIdNumber.value)
)

const canDeleteReview = review =>
  authStore.user &&
  (review.user === authStore.user.username ||
   review.user_id === authStore.user.id)

const goBack = () => router.back()

const formatDate = iso =>
  iso ? new Date(iso).toLocaleString() : ''

/* ================= API ================= */

const fetchBook = async () => {
  if (!id.value) return

  const { data } = await bookAPI.getBook(id.value)

  book.value = {
    reviews: [],
    review_count: 0,
    ...data,
  }

  if (!Array.isArray(book.value.reviews)) {
    book.value.reviews = []
  }
}

const ensureUserLoaded = async () => {
  if (!authStore.isAuthenticated) return
  if (!authStore.user?.favorites || !authStore.user?.read_books) {
    await authStore.fetchUser()
  }
}

/* ================= actions ================= */

const handleSubmitReview = async () => {
  if (!newReviewContent.value.trim()) return

  await reviewAPI.createReview({
    book: book.value.id,
    content: newReviewContent.value,
  })

  newReviewContent.value = ''

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    await fetchBook()
  }
}

const handleDeleteReview = async reviewId => {
  if (!confirm('정말 삭제하시겠습니까?')) return

  await reviewAPI.deleteReview(reviewId)

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    await fetchBook()
  }
}

const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) return router.push('/')
  if (bookIdNumber.value == null) return

  isFavorited.value
    ? await userBookAPI.removeFavorite(bookIdNumber.value)
    : await userBookAPI.addFavorite(bookIdNumber.value)

  await authStore.fetchUser()
}

const toggleRead = async () => {
  if (!authStore.isAuthenticated) return router.push('/')
  if (bookIdNumber.value == null) return

  isRead.value
    ? await userBookAPI.removeReadBook(bookIdNumber.value)
    : await userBookAPI.addReadBook(bookIdNumber.value)

  await authStore.fetchUser()
}

/* ================= WebSocket ================= */

const connectWS = () => {
  try {
    const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//${location.host}/ws/books/${id.value}/`
    ws = new WebSocket(wsUrl)

    ws.onmessage = e => {
      const data = JSON.parse(e.data)

      if (data.type === 'review.created') {
        book.value.reviews.unshift(data.review)
        book.value.review_count++
      }

      if (data.type === 'review.deleted') {
        book.value.reviews = book.value.reviews.filter(
          r => r.id !== data.review_id
        )
        book.value.review_count = Math.max(0, book.value.review_count - 1)
      }
    }

    ws.onclose = () => setTimeout(connectWS, 2000)
  } catch (e) {
    console.error(e)
  }
}

/* ================= lifecycle ================= */

onMounted(async () => {
  await fetchBook()
  await ensureUserLoaded()
  connectWS()
})

onUnmounted(() => {
  try { ws?.close() } catch {}
})

watch(id, async () => {
  try { ws?.close() } catch {}
  await fetchBook()
  connectWS()
})
</script>



<style lang="scss" scoped>

</style>