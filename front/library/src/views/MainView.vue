<template>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

    <!-- 검색 섹션 -->
    <div class="mb-12">
      <h1 class="text-center mb-8 text-gray-800 text-2xl font-semibold">도서를 검색해보세요</h1>
     <form @submit.prevent="handleSearch" class="mb-8">
  <div class="flex items-center gap-2">
    <BaseInput 
      v-model="searchQuery"
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

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">도서 목록을 불러오는 중...</p>
    </div>

    <!-- 도서 카드 리스트 -->
    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <BookCard
          v-for="book in books"
          :key="book.id"
          :book="book"
          @click="goToBookDetail(book.id)" />
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { bookAPI } from '@/api'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'
import BookCard from '@/components/BookCard.vue'

const router = useRouter()
const books = ref([])
const loading = ref(false)
const searchQuery = ref('')

const fetchBooks = async () => {
  try {
    loading.value = true
    const response = await bookAPI.getBooks()
    books.value = response.data
  } catch (error) {
    console.error('Failed to fetch books:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ 
      name: 'search', 
      query: { q: searchQuery.value.trim() } 
    })
  }
}

const goToBookDetail = (bookId) => {
  router.push({ name: 'bookDetail', params: { id: bookId } })
}

onMounted(() => {
  fetchBooks()
})
</script>

<style lang="scss" scoped>

</style>