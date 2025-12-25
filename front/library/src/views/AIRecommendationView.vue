<template>
  <main class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="mb-6">
        <h1 class="text-gray-900 text-2xl sm:text-3xl font-semibold tracking-tight mb-4">AI 추천 도서</h1>
        <form @submit.prevent="submitAiSearch" class="mt-4">
          <div class="flex items-center gap-3">
            <BaseInput v-model="keyword" type="text" msg="어떤 책을 찾고 계신가요?" />
            <div class="sm:w-40">
              <BaseButton type="submit" value="검색" class-name="h-12 rounded-full bg-blue-600 border-blue-600 text-white hover:bg-blue-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-600/30 transition-colors"/>
            </div>
          </div>
        </form>
      </div>

      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="fidget text-blue-600" role="status" aria-label="불러오는 중">
          <span class="fidget__center" />
          <span class="fidget__dot fidget__dot--1" />
          <span class="fidget__dot fidget__dot--2" />
          <span class="fidget__dot fidget__dot--3" />
        </div>
      </div>

      <div v-else>
        <p v-if="recommendedBooks.length === 0" class="bg-white border border-gray-200 rounded-2xl shadow-sm p-8 text-center text-gray-600">
          추천 도서가 없습니다. 검색어를 입력하고 검색 버튼을 클릭해주세요.
        </p>

        <div v-else class="space-y-4">
          <RouterLink 
            v-for="item in recommendedBooks" 
            :key="item.book.id" 
            :to="{ name: 'bookDetail', params: { id: item.book.id } }"
            class="flex items-start gap-5 bg-white border border-gray-200 rounded-2xl shadow-sm p-5 hover:shadow-md hover:border-blue-300 transition-all duration-200 cursor-pointer"
          >
            <!-- 책 표지 이미지 -->
            <div class="w-24 h-36 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100 shadow-sm">
              <img 
                v-if="item.book.cover_url" 
                :src="item.book.cover_url" 
                :alt="item.book.title"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </div>
            <!-- 책 정보 -->
            <div class="flex-1 min-w-0 py-1">
              <h3 class="font-semibold text-gray-900 text-lg leading-snug line-clamp-2">{{ item.book.title }}</h3>
              <p class="text-sm text-gray-500 mt-1">{{ item.book.author?.name || item.book.author_name || '작자 미상' }}</p>
              <p class="text-sm text-blue-600 mt-3 leading-relaxed line-clamp-3">{{ item.reason }}</p>
            </div>
          </RouterLink>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { bookAPI } from '@/api'
import BaseInput from '@/components/BaseInput.vue'
import BaseButton from '@/components/BaseButton.vue'

const router = useRouter()
const route = useRoute()
const keyword = ref('')
const recommendedBooks = ref([])
const isLoading = ref(false)

const submitAiSearch = async () => {
  const prompt = String(keyword.value || '').trim()
  if (!prompt) return

  isLoading.value = true
  try {
    const res = await bookAPI.recommendByPrompt({ prompt, nonce: Date.now() })
    recommendedBooks.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    recommendedBooks.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // If prompt query param exists, fetch immediately
  const prompt = route.query.prompt
  if (prompt) {
    keyword.value = String(prompt).trim()
    submitAiSearch()
  }
})
</script>

<style lang="scss" scoped>
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
