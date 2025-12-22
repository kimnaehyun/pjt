<template>
  <div class="flex items-start gap-4">
    <div
      class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0"
    >
      <img :src="imgSrc" :alt="imgAlt" class="w-6 h-6" />
    </div>

    <div class="flex-1">
      <label class="block text-sm text-gray-600">{{ field }}</label>
      <p class="text-gray-800 py-2">{{ value }}</p>
    </div>
  </div>
</template>

<script setup>
const { imgSrc, imgAlt, field, value } = defineProps({
  imgSrc: String,
  imgAlt: String,
  field: String,
  value: String,
});
</script>

<style scoped></style>
