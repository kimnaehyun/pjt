<template>
  <main class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

      <!-- 검색 섹션 -->
      <section class="mb-12">
        <div class="text-center mb-8">
          <h1 class="text-gray-900 text-3xl sm:text-4xl font-semibold tracking-tight">어떤 책을 찾고 계신가요?</h1>
          <p class="mt-2 text-gray-600">키워드로 검색하거나, AI로 추천을 받아보세요.</p>
        </div>

        <div class="bg-white border border-gray-200 rounded-2xl shadow-md p-5 sm:p-6">
          <form @submit.prevent="search">
            <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div class="flex-1">
                <BaseInput
                  v-model="keyword"
                  type="text"
                  msg="책 제목, 저자, 카테고리로 검색"
                />
              </div>

              <button
                type="button"
                class="h-12 rounded-full px-5 font-semibold text-sm tracking-tight transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600/40 border-2 border-blue-600 text-blue-600 bg-white hover:bg-blue-50 hover:shadow-md"
                @click="aiSearch"
              >
                AI 추천
              </button>

              <button
                type="submit"
                class="h-12 rounded-full px-6 font-semibold text-sm tracking-tight transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600/40 bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md"
              >
                검색
              </button>
            </div>
          </form>
        </div>
      </section>

      <!-- 카테고리별 Top 10 -->
      <div v-if="isLoading" class="flex items-center justify-center py-16">
        <div class="fidget text-blue-600" role="status" aria-label="불러오는 중">
          <span class="fidget__center" />
          <span class="fidget__dot fidget__dot--1" />
          <span class="fidget__dot fidget__dot--2" />
          <span class="fidget__dot fidget__dot--3" />
        </div>
      </div>

      <div v-else class="space-y-10">
        <!-- 카테고리 섹션 -->
        <section
          v-for="cat in categories"
          :key="cat.id"
          class="bg-white border border-gray-200 rounded-2xl shadow-sm p-5 sm:p-6"
        >
          <div class="flex items-end justify-between gap-4 mb-4">
            <div>
              <h2 class="text-gray-900 text-xl font-semibold">{{ cat.name }}</h2>
              <span class="mt-1 inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-2.5 py-1 text-xs font-semibold text-gray-600">
                Top 10 추천 도서
              </span>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
              @click="moveCategory(cat.id, -1)"
              aria-label="이전"
            >
              ‹
            </button>

            <div class="flex-1 overflow-hidden carousel-viewport" :ref="(el) => setViewport(cat.id, el)">
              <div
                class="track flex gap-6 w-max pb-2"
                :ref="(el) => setTrack(cat.id, el)"
                :style="trackStyle(cat.id)"
              >
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
              class="h-10 w-10 grid place-items-center rounded-full border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
              @click="moveCategory(cat.id, 1)"
              aria-label="다음"
            >
              ›
            </button>
          </div>
        </section>
      </div>

    </div>
  </main>
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
  // Always perform a normal search on submit.
  router.push({
    name: 'searchResult',
    params: {
      search: keyword.value,
    },
  })
}

const aiSearch = () => {
  const prompt = String(keyword.value || '').trim()
  // Navigate to AI recommendation page with prompt
  router.push({ 
    name: 'aiRecommendation', 
    query: { prompt: prompt || '' } 
  })
}

const fetchBooks = async () => {
  isLoading.value = true
  try {
    // 1) Preferred: backend cached/stable Top10 per category.
    try {
      const res = await metaAPI.getCategoriesTop10()
      const list = Array.isArray(res.data) ? res.data : []

      const nextBooks = {}
      const nextIndex = {}
      const nextCategories = []

      for (const c of list) {
        const catId = c?.id
        const books = Array.isArray(c?.books) ? c.books : []
        if (!catId || books.length === 0) continue
        nextCategories.push({ id: catId, name: c?.name || '' })
        nextBooks[catId] = books.slice(0, 10)
        nextIndex[catId] = 0
      }

      if (nextCategories.length > 0) {
        categories.value = nextCategories
        categoryBooks.value = nextBooks
        carouselIndex.value = nextIndex
        return
      }
    } catch (e) {
      // fall through to legacy fetch below
    }

    // 2) Fallback: fetch category list + books and compute Top10 on the client.
    const catRes = await metaAPI.getCategories()
    const catList = Array.isArray(catRes.data) ? catRes.data : []
    categories.value = catList

    const requests = catList.map((c) => bookAPI.getBooks({ category: c.id }))
    const results = await Promise.allSettled(requests)

    const nextBooks = {}
    const nextIndex = {}

    for (let i = 0; i < catList.length; i++) {
      const catId = catList[i].id
      const r = results[i]
      const data = r.status === 'fulfilled' ? r.value.data : []
      const list = Array.isArray(data) ? data : []
      const picked = list
        .slice()
        .sort((a, b) => (a?.id ?? 0) - (b?.id ?? 0))
        .slice(0, 10)

      if (picked.length > 0) {
        nextBooks[catId] = picked
        nextIndex[catId] = 0
      }
    }

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