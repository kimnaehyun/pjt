<template>
 <div class="group cursor-pointer">
    <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
        <div class="aspect-[3/4] bg-gray-200 overflow-hidden">
            <img 
              :src="book.cover_url || defaultCover" 
              :alt="book.title" 
              @error="onCoverError"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
        </div>
        <div class="p-4">
            <div class="text-sm text-blue-600 mb-1">{{ book.category?.name || book.category_name }}</div>
            <h3 class="mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors font-semibold">
              {{ book.title }}
            </h3>
            <p class="text-gray-600 text-sm mb-2">{{ book.author?.name || book.author_name }}</p>
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-1">
                    <img :src="star" alt="별점" class="w-4 h-4">
                    <span class="text-sm">{{ book.global_recommend_count || 0 }}</span>
                </div>
                <span class="text-blue-600 text-sm">{{ book.genre?.name || book.genre_name }}</span>
            </div>
        </div>
    </div>
 </div>
</template>

<script setup>
import star from '../assets/imges/star.png'

defineProps({
  book: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const defaultCover = 'https://via.placeholder.com/300x400?text=No+Image'

const onCoverError = (e) => {
  // Prevent infinite loop if placeholder also fails.
  if (e?.target?.src && e.target.src !== defaultCover) {
    e.target.src = defaultCover
  }
}
</script>

<style scoped>

</style>