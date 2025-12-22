<template>
   <div class="flex items-start gap-4 ">

  <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">

    <img :src="imgSrc" :alt="imgAlt" class="w-6 h-6">
  </div>

  <div class="flex-1">
    <label class="block text-sm text-gray-600 ">{{ field }}</label>
    <component :is="componentToShow" v-bind="componentProps" />
  </div>
</div>

</template>

<script setup>
import InfoRow from './InfoRow.vue';
import BaseInput from './BaseInput.vue';

defineProps({
  imgSrc: String,
  imgAlt: String,
  field: String,
  value: String,
  type: {
    type: String,
    default: 'info' 
  }
});

const componentToShow = type === 'input' ? BaseInput : InfoRow;

const componentProps = type === 'input'
  ? { modelValue: value } 
  : { value };           
</script>

<style lang="scss" scoped>

</style>