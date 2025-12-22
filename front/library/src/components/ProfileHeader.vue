<template>
<div class="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-12 text-white">
    <div class="flex items-center gap-4">
        <div class="w-20 h-20 bg-white rounded-full flex items-center justify-center overflow-hidden">
  <img
    :src="userImg"
    alt="유저 이미지"
    class="w-8 h-8 object-cover"
  />
</div>
        <div>
            <h1 class="mb-2 text-white">{{ userName }}</h1>
            <p class="text-blue-100">{{ userEmail }}</p>
        </div>
    </div>
</div>
</template>

<script setup>
import userImg from '@/assets/imges/userImg.png';
defineProps({
  userName: String,
  userEmail: String,
}) 
</script>

<style lang="scss" scoped>

</style>