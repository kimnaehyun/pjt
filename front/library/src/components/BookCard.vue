<template>
 <RouterLink
     class="group"
     :to="{ name: 'bookDetail', params: { id: book.id } }"
 >
    <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
                <div class="aspect-[4/5] bg-gray-200 overflow-hidden">
            <img
              v-if="book?.cover_url"
              :src="book.cover_url"
              :alt="book.title || 'book cover'"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            >
        </div>
        <div class="p-4">
            <div class="text-sm text-blue-600 mb-1">{{ book?.category_name || book?.category?.name || '' }}</div>
            <h3 class="mb-2 line-clamp-1 group-hover:text-blue-600 transition-colors">{{ book?.title || '' }}</h3>
            <p class="text-gray-600 text-sm mb-2 line-clamp-1">{{ book?.author_name || book?.author?.name || '' }}</p>
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-1">
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="2"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            class="w-4 h-4 text-gray-600"
                                            aria-label="댓글 수"
                                            role="img"
                                        >
                                            <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
                                        </svg>
                    <span class="text-sm">{{ book?.review_count ?? '' }}</span>
                </div>
                <span class="text-blue-600">{{ book?.genre_name || book?.genre?.name || '' }}</span>
            </div>
        </div>
    </div>
 </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
    book: {
        type: Object,
        required: true,
    },
})
</script>

<style  scoped>

</style>