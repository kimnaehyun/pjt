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
          <BaseButton
            type="submit"
            class="bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors px-6 py-2 flex-1"
            value="검색"
          />
        </div>
      </form>
    </div>

    <!-- 카테고리별 Top 10 -->
    <div v-if="isLoading" class="text-center text-gray-600">불러오는 중...</div>

    <div v-else class="space-y-10">
      <section v-for="cat in categories" :key="cat.id">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-gray-800 text-xl font-semibold">{{ cat.name }}</h2>
          <p class="text-sm text-gray-500">Top 10</p>
        </div>

        <div class="marquee overflow-hidden">
          <div class="marquee-track flex gap-6" :style="marqueeStyle(cat.id)">
            <div
              v-for="(book, idx) in marqueeBooksByCategory(cat.id)"
              :key="`${book.id}-${idx}`"
              class="w-40 sm:w-44 md:w-48 lg:w-56 shrink-0"
            >
              <BookCard :book="book" />
            </div>
          </div>
        </div>
      </section>
    </div>

  </div>
</template>

<script setup>
import BaseButton from '@/components/BaseButton.vue';
import BaseInput from '@/components/BaseInput.vue';
import BookCard from '@/components/BookCard.vue';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { bookAPI, metaAPI } from '@/api';

const router = useRouter();
const keyword = ref('')

const isLoading = ref(true)
const categories = ref([])
const categoryBooks = ref({}) // { [categoryId]: Book[] }


const search = () => {
  if (!keyword.value?.trim()) return

  router.push({
  name: 'searchResult',
  params: {
    search: keyword.value,
  },
});
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
    for (let i = 0; i < catList.length; i++) {
      const catId = catList[i].id
      const r = results[i]
      const data = r.status === 'fulfilled' ? r.value.data : []
      const list = Array.isArray(data) ? data : []
      const top10 = list
        .slice()
        .sort((a, b) => (b?.global_recommend_count ?? 0) - (a?.global_recommend_count ?? 0))
        .slice(0, 10)
      if (top10.length > 0) {
        nextBooks[catId] = top10
      }
    }

    // books가 없는 카테고리는 화면에서 제외
    categories.value = categories.value.filter((c) => (nextBooks[c.id] || []).length > 0)
    categoryBooks.value = nextBooks
  } finally {
    isLoading.value = false
  }
}

const marqueeBooksByCategory = (categoryId) => {
  const list = categoryBooks.value?.[categoryId] || []
  if (list.length <= 1) return list
  // Duplicate once so we can loop seamlessly.
  return [...list, ...list]
}

const marqueeStyle = (categoryId) => {
  const list = categoryBooks.value?.[categoryId] || []
  // Duration scales with item count; keep it readable.
  const seconds = Math.max(18, list.length * 2.2)
  return { '--marquee-duration': `${seconds}s` }
}

onMounted(() => {
  fetchBooks()
})
</script>

<style lang="scss" scoped>
.marquee-track {
  width: max-content;
  animation: marquee var(--marquee-duration, 22s) linear infinite;
}

@keyframes marquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .marquee-track {
    animation: none;
  }
}
</style>