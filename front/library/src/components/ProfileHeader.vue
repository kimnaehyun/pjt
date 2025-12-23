<template>
<div class="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-12 text-white">
    <div class="flex items-center gap-4">
        <div class="w-20 h-20 bg-white rounded-full flex items-center justify-center overflow-hidden">
          <img
            :src="user?.avatar_url || defaultUserImg"
            :alt="user?.name || '사용자'"
            class="w-full h-full object-cover"
          />
        </div>
        <div>
            <h1 class="mb-2 text-white">{{ user?.name || user?.nickname || '사용자' }}</h1>
            <p class="text-blue-100">{{ user?.email || '' }}</p>
        </div>
    </div>
</div>
</template>

<script setup>
import defaultUserImg from '@/assets/imges/userImgBlue.png'

defineProps({
  user: {
    type: Object,
    default: null
  }
})
</script>

<style lang="scss" scoped>

</style>