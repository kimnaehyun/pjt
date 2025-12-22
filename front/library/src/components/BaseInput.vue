<template>
<div class="relative w-full">
  <img
    v-if="imgSrc"
    :src="imgSrc"
    :alt="imgAlt"
    class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5"
  />

  <input
    :type="type"
    :class="imgSrc ? 'pl-11' : 'pl-4'"
    class="w-full pr-4 py-3 border border-gray-300 rounded-lg
           focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
    :placeholder="msg"
  />
</div>
    
  </input>
</template>

<script setup>

defineProps({
  type: String,
  imgSrc: String,
  imgAlt: String,
  msg: String,
});
</script>

<style lang="scss" scoped>

</style>