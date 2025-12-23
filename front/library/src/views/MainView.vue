<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

    <!-- 검색 섹션 -->
    <div class="mb-12">
      <h1 class="text-center mb-8 text-gray-800 text-2xl font-semibold">도서를 검색해보세요</h1>
      <form class="mb-8" @submit.prevent="search">
        <div class="flex items-center gap-2">
          <BaseInput
            v-model="keyword"
            type="text"
            placeholder="책 제목, 저자, 카테고리로 검색"
            class=" border-gray-300 focus:border-blue-600 focus:outline-none shadow-lg"
          />
          <button
            type="button"
            class="px-4 py-2 rounded-full transition-colors"
            :class="isAiMode ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'"
            @click="aiSearch"
          >
            AI
          </button>
          <BaseButton
            type="submit"
            class="bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors px-6 py-2 flex-1"
            value="검색"
          />
        </div>
      </form>
    </div>

    <!-- 카테고리별 Top 10 -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="fidget text-blue-600" role="status" aria-label="불러오는 중">
        <span class="fidget__center" />
        <span class="fidget__dot fidget__dot--1" />
        <span class="fidget__dot fidget__dot--2" />
        <span class="fidget__dot fidget__dot--3" />
      </div>
    </div>

    <div v-else class="space-y-10">
      <section v-for="cat in categories" :key="cat.id">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-gray-800 text-xl font-semibold">{{ cat.name }}</h2>
          <p class="text-sm text-gray-500">Top 10</p>
        </div>

        <div class="flex items-center gap-3">
          <button
            type="button"
            class="px-3 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            @click="moveCategory(cat.id, -1)"
            aria-label="이전"
          >
            ‹
          </button>

          <div class="flex-1 overflow-hidden carousel-viewport" :ref="(el) => setViewport(cat.id, el)">
            <div class="track flex gap-6 w-max pb-2" :ref="(el) => setTrack(cat.id, el)" :style="trackStyle(cat.id)">
              <div
                v-for="book in booksByCategory(cat.id)"
                :key="book.id"
                class="book-item w-40 sm:w-44 md:w-48 lg:w-56 shrink-0"
              >
                <BookCard :book="book" />
              </div>
            </div>
          </div>

          <button
            type="button"
            class="px-3 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            @click="moveCategory(cat.id, 1)"
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
import BaseButton from '@/components/BaseButton.vue';
import BaseInput from '@/components/BaseInput.vue';
import BookCard from '@/components/BookCard.vue';
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { bookAPI, metaAPI } from '@/api';

const router = useRouter();
const keyword = ref('')
const isAiMode = ref(false)

const isLoading = ref(true)
const categories = ref([])
const categoryBooks = ref({}) // { [categoryId]: Book[] }
const carouselIndex = ref({}) // { [categoryId]: number }
const tracks = ref({}) // { [categoryId]: HTMLElement }
const viewports = ref({}) // { [categoryId]: HTMLElement }
const steps = ref({}) // { [categoryId]: number }
const visibleSlots = ref({}) // { [categoryId]: number }


const search = () => {
  if (!keyword.value?.trim()) return

  if (isAiMode.value) {
    const prompt = String(keyword.value || '').trim()
    router.push({ name: 'aiSearchResult', query: { prompt } })
    return
  }

  router.push({
  name: 'searchResult',
  params: {
    search: keyword.value,
  },
});
}

const aiSearch = () => {
  const prompt = String(keyword.value || '').trim()
  // If there's a prompt, run AI search immediately.
  if (prompt) {
    router.push({ name: 'aiSearchResult', query: { prompt } })
    return
  }
  // Otherwise, treat as a mode toggle (activate/deactivate AI mode).
  isAiMode.value = !isAiMode.value
}

const fetchBooks = async () => {
  isLoading.value = true
  try {
    const catRes = await metaAPI.getCategories()
    const catList = Array.isArray(catRes.data) ? catRes.data : []
    categories.value = catList

    const requests = catList.map((c) => bookAPI.getBooks({ category: c.id }))
    const results = await Promise.allSettled(requests)

    const nextBooks = {}
    const nextIndex = {}
    const usedTitleKeys = new Set()

    const norm = (s) => String(s || '').trim().toLowerCase().replace(/\s+/g, ' ')
    const titleKey = (book) => {
      const t = norm(book?.title)
      const a = norm(book?.author_name || book?.author?.name)
      return `${t}|${a}`
    }

    for (let i = 0; i < catList.length; i++) {
      const catId = catList[i].id
      const r = results[i]
      const data = r.status === 'fulfilled' ? r.value.data : []
      const list = Array.isArray(data) ? data : []
      const sorted = list
        .slice()
        .sort((a, b) => (b?.global_recommend_count ?? 0) - (a?.global_recommend_count ?? 0))

      // 중복 도서 제거: 같은 제목(+저자)면 제외 (카테고리 내/카테고리 간 모두)
      const picked = []
      const localKeys = new Set()
      for (const book of sorted) {
        if (!book?.id) continue
        const key = titleKey(book)
        if (!key || key.startsWith('|')) continue
        if (localKeys.has(key)) continue
        if (usedTitleKeys.has(key)) continue
        localKeys.add(key)
        usedTitleKeys.add(key)
        picked.push(book)
        if (picked.length >= 10) break
      }

      if (picked.length > 0) {
        nextBooks[catId] = picked
        nextIndex[catId] = 0
      }
    }

    // books가 없는 카테고리는 화면에서 제외
    categories.value = categories.value.filter((c) => (nextBooks[c.id] || []).length > 0)
    categoryBooks.value = nextBooks
    carouselIndex.value = nextIndex
  } finally {
    isLoading.value = false
  }
}

const booksByCategory = (categoryId) => {
  return categoryBooks.value?.[categoryId] || []
}

const setViewport = (categoryId, el) => {
  if (!el) return
  if (viewports.value?.[categoryId] === el) return
  viewports.value = { ...viewports.value, [categoryId]: el }
  nextTick(() => computeMetrics(categoryId))
}

const setTrack = (categoryId, el) => {
  if (!el) return
  if (tracks.value?.[categoryId] === el) return
  tracks.value = { ...tracks.value, [categoryId]: el }
  nextTick(() => computeMetrics(categoryId))
}

const computeMetrics = (categoryId) => {
  const track = tracks.value?.[categoryId]
  const viewport = viewports.value?.[categoryId]
  if (!track || !viewport) return
  const item = track.querySelector('.book-item')
  if (!item) return

  const style = window.getComputedStyle(track)
  const gap = parseFloat(style.columnGap || style.gap || '0') || 0
  const step = item.getBoundingClientRect().width + gap
  if (!step) return
  const prevStep = steps.value?.[categoryId]
  if (prevStep !== step) {
    steps.value = { ...steps.value, [categoryId]: step }
  }

  const slots = Math.max(1, Math.floor((viewport.clientWidth + gap) / step))
  const prevSlots = visibleSlots.value?.[categoryId]
  if (prevSlots !== slots) {
    visibleSlots.value = { ...visibleSlots.value, [categoryId]: slots }
  }
}

const maxStartIndex = (categoryId) => {
  const list = booksByCategory(categoryId)
  const slots = visibleSlots.value?.[categoryId] ?? 1
  return Math.max(0, list.length - slots)
}

const moveCategory = (categoryId, direction) => {
  computeMetrics(categoryId)
  const maxIdx = maxStartIndex(categoryId)
  const cur = carouselIndex.value?.[categoryId] ?? 0
  if (maxIdx <= 0) {
    return
  }

  let next
  if (direction > 0) {
    next = cur >= maxIdx ? 0 : cur + 1
  } else {
    next = cur <= 0 ? maxIdx : cur - 1
  }
  carouselIndex.value = { ...carouselIndex.value, [categoryId]: next }
}

const trackStyle = (categoryId) => {
  const step = steps.value?.[categoryId] ?? 0
  const idx = carouselIndex.value?.[categoryId] ?? 0
  return {
    transform: `translateX(${-idx * step}px)`,
    transition: 'transform 260ms ease',
  }
}

const onResize = () => {
  for (const c of categories.value) {
    computeMetrics(c.id)
    const maxIdx = maxStartIndex(c.id)
    const cur = carouselIndex.value?.[c.id] ?? 0
    if (cur > maxIdx) {
      carouselIndex.value = { ...carouselIndex.value, [c.id]: maxIdx }
    }
  }
}

onMounted(() => {
  fetchBooks()
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