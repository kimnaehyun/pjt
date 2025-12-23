<template>
<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4 py-12">
  <div class="max-w-md w-full">
    <!-- 뒤로가기 버튼 -->
    <button class="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6" @click="goLanding">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" 
           viewBox="0 0 24 24" fill="none" stroke="currentColor" 
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
           class="lucide lucide-arrow-left w-5 h-5" aria-hidden="true">
        <path d="m12 19-7-7 7-7"></path>
        <path d="M19 12H5"></path>
      </svg>
      뒤로가기
    </button>
    
    <!-- 회원가입 폼 컨테이너 -->
    <div class="bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-center mb-8 text-gray-800">회원가입</h2>
        
        <!-- 회원가입 폼 -->
        <form class="space-y-6" @submit.prevent="onSubmit">
            <!-- 이름 -->
            <div>
                <label for="name" class="block text-sm mb-2 text-gray-700">이름</label>
                
            <BaseInput type="text" msg="홍길동" :img-src="userImg" img-alt="이름" />
        </div>

        <!-- 이메일 -->
        <div>
          <label for="email" class="block text-sm mb-2 text-gray-700">이메일</label>
            <BaseInput type="email" msg="example@email.com" :img-src="mailImg" img-alt="이메일" />
        </div>

        <!-- 비밀번호 -->
        <div>
          <label for="password" class="block text-sm mb-2 text-gray-700">비밀번호</label>
       <BaseInput type="password" msg="비밀번호를 입력하세요" :img-src="passwordImg" img-alt="비밀번호" />
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <label for="confirmPassword" class="block text-sm mb-2 text-gray-700">비밀번호 확인</label>
          <BaseInput type="password" msg="비밀번호를 다시 입력하세요" :img-src="passwordImg" img-alt="비밀번호 확인" />
        </div>

        <!-- 선택 사항 -->
        <div class="border-t pt-4">
          <p class="text-sm text-gray-600 mb-4">선택 사항</p>
          <div class="space-y-4">
            <!-- 전화번호 -->
            <div>
              <label for="phone" class="block text-sm mb-2 text-gray-700">전화번호</label>
              <BaseInput type="tel" msg="010-1234-5678" />
            </div>

            <!-- 생년월일 -->
            <div>
              <label for="birthdate" class="block text-sm mb-2 text-gray-700">생년월일</label>
              <BaseInput type="date" msg="YYYY-MM-DD" />
            </div>

            <!-- 주소 -->
            <div>
              <label for="address" class="block text-sm mb-2 text-gray-700">주소</label>
              <BaseInput type="text" msg="주소를 입력하세요" />
            </div>
          </div>
        </div>

        <!-- 가입하기 버튼 -->
        
        <BaseButton type="submit" value="가입하기"
          class-name="bg-blue-600 text-white hover:bg-blue-700 transition-colors" />
      </form>

      <!-- 로그인 안내 -->
      <div class="mt-6 text-center text-sm text-gray-600">
        <p>이미 계정이 있으신가요?</p>
        <button class="text-blue-600 hover:underline mt-1" @click="goLanding">로그인하기</button>
      </div>
    </div>
  </div>
</div>


</template>

<script setup>
import BaseInput from '@/components/BaseInput.vue';
import userImg from '@/assets/imges/userImgBlack.png';
import mailImg from '@/assets/imges/msgImg.png';
import passwordImg from '@/assets/imges/password.png';
import BaseButton from '@/components/BaseButton.vue';
import { useRouter } from 'vue-router'

const router = useRouter()

const goLanding = () => {
  router.back()
};
const onSubmit = () => {
  // TODO: 회원가입 폼 제출 처리 로직 / API 호출
  router.push({ name: "main" });
  console.log('회원가입 폼이 제출되었습니다.');
};
</script>

<style lang="scss" scoped>

</style>