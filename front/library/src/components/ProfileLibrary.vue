<template>
  <div class="p-6 sm:p-8">
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-gray-900 text-xl font-semibold">내 서재</h2>

      <button
        type="button"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        @click="goProfileInfo"
      >
        회원정보
      </button>
    </div>

    <div class="space-y-10">
      <!-- AI 추천 도서 -->
      <section class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 sm:p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-900 font-semibold">AI 추천 도서</h3>
          <div class="flex items-center gap-3">
            <span class="inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-2.5 py-1 text-xs font-semibold text-gray-600">
              최대 8권
            </span>
            <button
              type="button"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-600/30"
              :disabled="isAiLoading"
              @click="fetchAiBooks"
            >
              AI 다시 추천
            </button>
          </div>
        </div>

        <div v-if="isAiLoading" class="flex items-center justify-center py-10">
          <div class="fidget text-blue-600" role="status" aria-label="불러오는 중">
            <span class="fidget__center" />
            <span class="fidget__dot fidget__dot--1" />
            <span class="fidget__dot fidget__dot--2" />
            <span class="fidget__dot fidget__dot--3" />
          </div>
        </div>

        <p v-else-if="aiBooks.length === 0" class="text-gray-600 text-sm">추천 도서가 없습니다.</p>

        <div v-else class="flex items-center gap-3">
          <button
            type="button"
            class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            @click="move('ai', -1)"
            aria-label="이전"
          >
            ‹
          </button>

          <div class="flex-1 overflow-hidden carousel-viewport" :ref="(el) => setViewport('ai', el)">
            <div class="track flex gap-6 w-max pb-2" :ref="(el) => setTrack('ai', el)" :style="trackStyle('ai')">
              <div v-for="book in aiBooks" :key="book.id" class="book-item w-40 sm:w-44 md:w-48 lg:w-56 shrink-0">
                <BookCard :book="book" />
              </div>
            </div>
          </div>

          <button
            type="button"
            class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            @click="move('ai', 1)"
            aria-label="다음"
          >
            ›
          </button>
        </div>
      </section>

      <!-- 찜한 도서 -->
      <section class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 sm:p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-900 font-semibold">찜한 도서</h3>
        </div>

        <p v-if="favorites.length === 0" class="text-gray-600 text-sm">찜한 도서가 없습니다.</p>

        <div v-else class="flex items-center gap-3">
          <button
            type="button"
            class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            @click="move('favorites', -1)"
            aria-label="이전"
          >
            ‹
          </button>

          <div class="flex-1 overflow-hidden carousel-viewport" :ref="(el) => setViewport('favorites', el)">
            <div
              class="track flex gap-6 w-max pb-2"
              :ref="(el) => setTrack('favorites', el)"
              :style="trackStyle('favorites')"
            >
              <div
                v-for="book in favorites"
                :key="book.id"
                class="book-item w-40 sm:w-44 md:w-48 lg:w-56 shrink-0 relative"
              >
                <button
                  type="button"
                  class="absolute top-2 right-2 z-10 h-8 w-8 grid place-items-center rounded-full border border-gray-200 bg-white/90 text-gray-700 hover:text-red-600 hover:bg-white transition-colors"
                  aria-label="찜 도서 제거"
                  @click.stop.prevent="removeFavorite(book.id)"
                >
                  ×
                </button>
                <BookCard :book="book" />
              </div>
            </div>
          </div>

          <button
            type="button"
            class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            @click="move('favorites', 1)"
            aria-label="다음"
          >
            ›
          </button>
        </div>
      </section>

      <!-- 읽은 도서 -->
      <section class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 sm:p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-900 font-semibold">읽은 도서</h3>
        </div>

        <p v-if="readBooks.length === 0" class="text-gray-600 text-sm">읽은 도서가 없습니다.</p>

        <div v-else class="flex items-center gap-3">
          <button
            type="button"
            class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            @click="move('read', -1)"
            aria-label="이전"
          >
            ‹
          </button>

          <div class="flex-1 overflow-hidden carousel-viewport" :ref="(el) => setViewport('read', el)">
            <div class="track flex gap-6 w-max pb-2" :ref="(el) => setTrack('read', el)" :style="trackStyle('read')">
              <div v-for="book in readBooks" :key="book.id" class="book-item w-40 sm:w-44 md:w-48 lg:w-56 shrink-0 relative">
                <button
                  type="button"
                  class="absolute top-2 right-2 z-10 h-8 w-8 grid place-items-center rounded-full border border-gray-200 bg-white/90 text-gray-700 hover:text-red-600 hover:bg-white transition-colors"
                  aria-label="읽은 도서 제거"
                  @click.stop.prevent="removeRead(book.id)"
                >
                  ×
                </button>
                <BookCard :book="book" />
              </div>
            </div>
          </div>

          <button
            type="button"
            class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            @click="move('read', 1)"
            aria-label="다음"
          >
            ›
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BookCard from '@/components/BookCard.vue'
import { recommendAPI, userBookAPI } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const favorites = computed(() => {
  const list = authStore.user?.favorites
  return Array.isArray(list) ? list : []
})

const readBooks = computed(() => {
  const list = authStore.user?.read_books
  return Array.isArray(list) ? list : []
})

const aiBooks = ref([])
const isAiLoading = ref(false)

const removeFavorite = async (bookId) => {
  if (!bookId) return
  try {
    await userBookAPI.removeFavorite(bookId)
    await authStore.fetchUser()
  } catch (e) {
    // keep UI stable; errors are handled by interceptor/logout if needed
  }
}

const removeRead = async (bookId) => {
  if (!bookId) return
  try {
    await userBookAPI.removeReadBook(bookId)
    await authStore.fetchUser()
  } catch (e) {
  }
}

const carouselIndex = ref({}) // { [sectionId]: number }
// IMPORTANT: DOM element references must be non-reactive.
// If we store them in refs and mutate during render via function refs,
// Vue will re-render and the refs will run again -> recursive update loop.
const tracks = Object.create(null) // { [sectionId]: HTMLElement }
const viewports = Object.create(null) // { [sectionId]: HTMLElement }
const steps = ref({}) // { [sectionId]: number }
const visibleSlots = ref({}) // { [sectionId]: number }

const setViewport = (sectionId, el) => {
  if (!el) return
  if (viewports[sectionId] === el) return
  viewports[sectionId] = el
  // Defer metrics to after the DOM settles for this render.
  nextTick(() => computeMetrics(sectionId))
}

const setTrack = (sectionId, el) => {
  if (!el) return
  if (tracks[sectionId] === el) return
  tracks[sectionId] = el
  nextTick(() => computeMetrics(sectionId))
}

const listBySection = (sectionId) => {
  if (sectionId === 'ai') return aiBooks.value
  if (sectionId === 'favorites') return favorites.value
  if (sectionId === 'read') return readBooks.value
  return []
}

const computeMetrics = (sectionId) => {
  const track = tracks?.[sectionId]
  const viewport = viewports?.[sectionId]
  if (!track || !viewport) return
  const item = track.querySelector('.book-item')
  if (!item) return

  const style = window.getComputedStyle(track)
  const gap = parseFloat(style.columnGap || style.gap || '0') || 0
  const step = item.getBoundingClientRect().width + gap
  if (!step) return
  const prevStep = steps.value?.[sectionId]
  if (prevStep !== step) {
    steps.value = { ...steps.value, [sectionId]: step }
  }

  const slots = Math.max(1, Math.floor((viewport.clientWidth + gap) / step))
  const prevSlots = visibleSlots.value?.[sectionId]
  if (prevSlots !== slots) {
    visibleSlots.value = { ...visibleSlots.value, [sectionId]: slots }
  }
}

const maxStartIndex = (sectionId) => {
  const list = listBySection(sectionId)
  const slots = visibleSlots.value?.[sectionId] ?? 1
  return Math.max(0, list.length - slots)
}

const move = (sectionId, direction) => {
  computeMetrics(sectionId)
  const maxIdx = maxStartIndex(sectionId)
  const cur = carouselIndex.value?.[sectionId] ?? 0
  if (maxIdx <= 0) {
    return
  }

  let next
  if (direction > 0) {
    next = cur >= maxIdx ? 0 : cur + 1
  } else {
    next = cur <= 0 ? maxIdx : cur - 1
  }
  carouselIndex.value = { ...carouselIndex.value, [sectionId]: next }
}

const trackStyle = (sectionId) => {
  const step = steps.value?.[sectionId] ?? 0
  const idx = carouselIndex.value?.[sectionId] ?? 0
  return {
    transform: `translateX(${-idx * step}px)`,
    transition: 'transform 260ms ease',
  }
}

const clampIndexes = () => {
  for (const sectionId of ['ai', 'favorites', 'read']) {
    computeMetrics(sectionId)
    const maxIdx = maxStartIndex(sectionId)
    const cur = carouselIndex.value?.[sectionId] ?? 0
    if (cur > maxIdx) {
      carouselIndex.value = { ...carouselIndex.value, [sectionId]: maxIdx }
    }
  }
}

const fetchAiBooks = async () => {
  isAiLoading.value = true
  try {
    const res = await recommendAPI.getPersonalized({ nonce: Date.now() })
    aiBooks.value = Array.isArray(res.data) ? res.data : []
    if (!(carouselIndex.value?.ai >= 0)) {
      carouselIndex.value = { ...carouselIndex.value, ai: 0 }
    }
  } catch (e) {
    aiBooks.value = []
  } finally {
    isAiLoading.value = false
    clampIndexes()
  }
}

const onResize = () => {
  clampIndexes()
}

watch([favorites, readBooks], () => {
  clampIndexes()
})

watch(aiBooks, () => {
  clampIndexes()
})

const goProfileInfo = () => {
  router.push({ name: 'profileDetail' })
}

onMounted(() => {
  carouselIndex.value = { ai: 0, favorites: 0, read: 0 }
  fetchAiBooks()
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.carousel-viewport {
  /* no drag scroll */
  touch-action: pan-y;
}

.fidget {
  position: relative;
  width: 56px;
  height: 56px;
  animation: fidget-rotate 900ms linear infinite;
}

.fidget__center {
  position: absolute;
  inset: 0;
  margin: auto;
  width: 14px;
  height: 14px;
  border-radius: 9999px;
  background: currentColor;
  opacity: 0.85;
}

.fidget__dot {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 9999px;
  background: currentColor;
}

.fidget__dot--1 {
  left: 50%;
  top: 4px;
  transform: translateX(-50%);
}

.fidget__dot--2 {
  left: 10px;
  bottom: 10px;
}

.fidget__dot--3 {
  right: 10px;
  bottom: 10px;
}

@keyframes fidget-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .fidget {
    animation: none;
  }
}
</style>
