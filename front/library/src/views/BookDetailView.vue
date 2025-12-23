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
    const wsUrl = `${wsProtocol}//127.0.0.1:8000/ws/books/${id.value}/`

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
