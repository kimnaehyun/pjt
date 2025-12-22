<template>
    <div :class="wrapperClass">
        <img v-if="imgSrc" :src="imgSrc" :alt="imgAlt" class="w-4 h-4 pr-2">
        <input :type="type" :value="value"/>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: String,
  value: String,
  imgSrc: String,
  imgAlt: String,
  className: {
    type: String,
    default: '',
  },
})

const wrapperClass = computed(() => [
  'w-full py-3 border-2 rounded-lg flex items-center justify-center',
  props.className,
])
</script>

<style scoped>

</style>