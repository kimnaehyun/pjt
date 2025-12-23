<template>


  <div class="p-8">
  <!-- Header -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-gray-800">회원정보</h2>

    <button
      @click="goProfileUpdate"
      type="button"
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
        class="lucide lucide-pen w-4 h-4"
      >
        <path
          d="M21.174 6.812a1 1 0 0 0-3.986-3.987
             L3.842 16.174a2 2 0 0 0-.5.83
             l-1.321 4.352a.5.5 0 0 0 .623.622
             l4.353-1.32a2 2 0 0 0 .83-.497z"
        />
      </svg>
      수정하기
    </button>
  </div>

  <!-- User Info -->
  <form class="space-y-6">
    
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

  </form>
</div>

  
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const goProfileUpdate = () => {
  // TODO 프로필 수정 페이지로 이동
  router.push({ name: "profileUpdate" });
};

const { imgSrc, imgAlt, field, value } = defineProps({
  imgSrc: String,
  imgAlt: String,
  field: String,
  value: String,
});
</script>

<style scoped></style>
