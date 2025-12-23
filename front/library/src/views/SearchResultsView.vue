<template>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 class="mb-6 text-gray-800 text-2xl font-semibold">"{{ search }}" 검색 결과</h1>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <BookCard
                v-for="book in books"
                :key="book.id"
                :book="book"
            />
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import BookCard from '@/components/BookCard.vue'
import { bookAPI } from '@/api'

const route = useRoute()
const search = computed(() => route.params.search)

const books = ref([])

const fetchBooks = async () => {
    const q = String(search.value || '').trim()
    const response = await bookAPI.getBooks({ search: q })
    books.value = Array.isArray(response.data) ? response.data : []
}

onMounted(() => {
    fetchBooks()
})

watch(search, () => {
    fetchBooks()
})
</script>

<style lang="scss" scoped>

</style>