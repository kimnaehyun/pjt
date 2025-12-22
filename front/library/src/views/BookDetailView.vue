<template>
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <button class="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
      class="lucide lucide-arrow-left w-5 h-5" aria-hidden="true">
      <path d="m12 19-7-7 7-7"></path>
      <path d="M19 12H5"></path>
    </svg>
    뒤로가기
  </button>

  <div class="bg-white rounded-xl shadow-lg p-8">
    <div class="grid md:grid-cols-[300px,1fr] gap-8">
      <BookCard />
        <!-- 책 소개 -->
        <div class="border-t pt-6">
          <h3 class="mb-4 text-gray-800">책 소개</h3>
          <p class="text-gray-700 leading-relaxed">
            당신이 잠든 사이 펼쳐지는 가장 특별한 꿈 이야기. 달러구트 꿈 백화점에서 일하게 된 페니의 특별한 여정을
            그린 판타지 소설입니다. 꿈을 판매하는 백화점이라는 독특한 설정과 따뜻한 이야기로 많은 독자들의 사랑을 받고 있습니다.
          </p>
        </div>
    </div>
  </div>

  <!-- 댓글 섹션 -->
  <div class="mt-8 bg-white rounded-xl shadow-lg p-8">
    <h2 class="mb-6 text-gray-800">댓글 (0)</h2>

    <form class="mb-8">
  <div class="flex items-center gap-2">
    <BaseInput 
      type="text" 
      placeholder="책 제목, 저자, 카테고리로 검색" 
      class=" border-gray-300 focus:border-blue-600 focus:outline-none shadow-lg"
    />
    <BaseButton 
      type="submit" 
      class="bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors px-6 py-2 flex-1" 
      :img-src="send"
      img-alt="작성"
      value="작성" 
    />
    </div>
    </form>

    <div class="space-y-4">
      <p class="text-center text-gray-500 py-8">아직 댓글이 없습니다.</p>
    </div>
  </div>
</div>

</template>

<script setup>
import BaseButton from '@/components/BaseButton.vue';
import BaseInput from '@/components/BaseInput.vue';
import BookCard from '@/components/BookCard.vue';
import send from '@/assets/imges/send.png';

</script>

<style lang="scss" scoped>

</style>