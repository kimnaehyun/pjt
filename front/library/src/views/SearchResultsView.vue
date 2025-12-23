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

        <h1 class="text-2xl font-semibold mb-4 text-gray-800">
            "{{ searchQuery }}" 검색 결과
        </h1>
        <p class="text-gray-600 mb-8">{{ books.length }}개의 도서를 찾았습니다.</p>

        <div v-if="loading" class="text-center py-12">
            <p class="text-gray-600">검색 중...</p>
        </div>

        <div v-else-if="books.length === 0" class="text-center py-12">
            <p class="text-gray-600">검색 결과가 없습니다.</p>
        </div>

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
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { bookAPI } from '@/api'
import BookCard from '@/components/BookCard.vue'

const router = useRouter()
const route = useRoute()
const books = ref([])
const loading = ref(false)
const searchQuery = ref(route.query.q || '')

const searchBooks = async () => {
    try {
        loading.value = true
        const response = await bookAPI.getBooks({ search: searchQuery.value })
        books.value = response.data
    } catch (error) {
        console.error('Failed to search books:', error)
    } finally {
        loading.value = false
    }
}

const goBack = () => {
    router.back()
}

const goToBookDetail = (bookId) => {
    router.push({ name: 'bookDetail', params: { id: bookId } })
}

watch(() => route.query.q, (newQuery) => {
    searchQuery.value = newQuery || ''
    if (searchQuery.value) {
        searchBooks()
    }
})

onMounted(() => {
    if (searchQuery.value) {
        searchBooks()
    }
})
</script>

<style lang="scss" scoped>

</style>