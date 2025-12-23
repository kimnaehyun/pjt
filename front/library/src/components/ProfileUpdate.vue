<template>
  <div class="p-8">
  <!-- Header -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-gray-800">회원정보</h2>

    <div class="flex gap-2">
      <!-- Cancel -->
      <button
      @click="goProfile"
        type="button"
        class="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          width="24"
          height="24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
          class="lucide lucide-x w-4 h-4"
        >
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
        취소
      </button>

      <!-- Save -->
      <button
        type="submit"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          width="24"
          height="24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
          class="lucide lucide-save w-4 h-4"
        >
          <path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" />
          <path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7" />
          <path d="M7 3v4a1 1 0 0 0 1 1h7" />
        </svg>
        저장
      </button>
    </div>
  </div>

  <!-- Form -->
  <form class="space-y-6">
    <div class="flex items-start gap-4">
    <div
      class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0"
    >
      <img :src="imgSrc" :alt="imgAlt" class="w-6 h-6" />
    </div>

    <div class="flex-1">
      <label class="block text-sm text-gray-600">{{ field }}</label>
      <BaseInput class="text-gray-800 py-2" :value="value" type="text" />
    </div>
  </div>
  </form>
</div>

 


</template>

<script setup>
import BaseInput from "./BaseInput.vue";
import { useRouter } from "vue-router";

const router = useRouter();

const goProfile = () => {
  router.push({ name: "profileDetail" });
};


const { imgSrc, imgAlt, field, value } = defineProps({
  imgSrc: String,
  imgAlt: String,
  field: String,
  value: String,
});
</script>

<style scoped></style>
