<template>
 <a href="" class="group">
    <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
        <div class="aspect-[3/4] bg-gray-200 overflow-hidden">
            <img src="" alt="" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
        </div>
        <div class="p-4">
            <div class="text-sm text-blue-600 mb-1"></div>
            <h3 class="mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors"></h3>
            <p class="text-gray-600 text-sm mb-2"></p>
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-1">
                    <img :src="star" alt="별점" class="w-4 h-4">
                    <span class="text-sm"></span>
                </div>
                <span class="text-blue-600"></span>
            </div>
        </div>
    </div>
 </a>
</template>

<script setup>
import star from '../assets/imges/star.png';
</script>

<style  scoped>

</style>