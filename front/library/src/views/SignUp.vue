<template>
<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4 py-12">
  <div class="max-w-md w-full">
    <!-- 뒤로가기 버튼 -->
    <button @click="goBack" class="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
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
        <form @submit.prevent="handleSignup" class="space-y-6">
            <!-- 이름 -->
            <div>
                <label for="name" class="block text-sm mb-2 text-gray-700">이름</label>
                <BaseInput 
                  v-model="signupForm.name"
                  type="text" 
                  msg="홍길동" 
                  :img-src="userImg" 
                  img-alt="이름" 
                />
            </div>

        <!-- 이메일 -->
        <div>
          <label for="email" class="block text-sm mb-2 text-gray-700">이메일*</label>
            <BaseInput 
              v-model="signupForm.email"
              type="email" 
              msg="example@email.com" 
              :img-src="mailImg" 
              img-alt="이메일" 
            />
        </div>

        <!-- 비밀번호 -->
        <div>
          <label for="password" class="block text-sm mb-2 text-gray-700">비밀번호*</label>
          <BaseInput 
            v-model="signupForm.password"
            type="password" 
            msg="비밀번호를 입력하세요" 
            :img-src="passwordImg" 
            img-alt="비밀번호" 
          />
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <label for="confirmPassword" class="block text-sm mb-2 text-gray-700">비밀번호 확인*</label>
          <BaseInput 
            v-model="signupForm.passwordConfirm"
            type="password" 
            msg="비밀번호를 다시 입력하세요" 
            :img-src="passwordImg" 
            img-alt="비밀번호 확인" 
          />
        </div>

        <!-- 선택 사항 -->
        <div class="border-t pt-4">
          <p class="text-sm text-gray-600 mb-4">선택 사항</p>
          <div class="space-y-4">
            <!-- 전화번호 -->
            <div>
              <label for="phone" class="block text-sm mb-2 text-gray-700">전화번호</label>
              <BaseInput 
                v-model="signupForm.phone"
                type="tel" 
                msg="010-1234-5678" 
              />
            </div>

            <!-- 생년월일 -->
            <div>
              <label for="birthdate" class="block text-sm mb-2 text-gray-700">생년월일</label>
              <BaseInput 
                v-model="signupForm.birthdate"
                type="date" 
                msg="YYYY-MM-DD" 
              />
            </div>

            <!-- 주소 -->
            <div>
              <label for="address" class="block text-sm mb-2 text-gray-700">주소</label>
              <BaseInput 
                v-model="signupForm.address"
                type="text" 
                msg="주소를 입력하세요" 
              />
            </div>
          </div>
        </div>

        <!-- 에러 메시지 -->
        <div v-if="errorMessage" class="text-red-600 text-sm text-center">
          {{ errorMessage }}
        </div>

        <!-- 가입하기 버튼 -->
        <BaseButton 
          type="submit" 
          value="가입하기"
          class-name="bg-blue-600 text-white hover:bg-blue-700 transition-colors" 
        />
      </form>

      <!-- 로그인 안내 -->
      <div class="mt-6 text-center text-sm text-gray-600">
        <p>이미 계정이 있으신가요?</p>
        <button @click="goToLogin" class="text-blue-600 hover:underline mt-1">로그인하기</button>
      </div>
    </div>
  </div>
</div>


</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseInput from '@/components/BaseInput.vue'
import userImg from '@/assets/imges/userImgBlack.png'
import mailImg from '@/assets/imges/msgImg.png'
import passwordImg from '@/assets/imges/password.png'
import BaseButton from '@/components/BaseButton.vue'

const router = useRouter()
const authStore = useAuthStore()

const signupForm = ref({
  name: '',
  email: '',
  password: '',
  passwordConfirm: '',
  phone: '',
  birthdate: '',
  address: ''
})

const errorMessage = ref('')

const handleSignup = async () => {
  try {
    errorMessage.value = ''
    
    // 유효성 검사
    if (!signupForm.value.email || !signupForm.value.password) {
      errorMessage.value = '이메일과 비밀번호는 필수입니다.'
      return
    }
    
    if (signupForm.value.password !== signupForm.value.passwordConfirm) {
      errorMessage.value = '비밀번호가 일치하지 않습니다.'
      return
    }
    
    // 회원가입 요청
    const { passwordConfirm, ...userData } = signupForm.value
    await authStore.signup(userData)
    router.push({ name: 'main' })
  } catch (error) {
    console.error('Signup error:', error)
    errorMessage.value = error.response?.data?.error || '회원가입에 실패했습니다.'
  }
}

const goBack = () => {
  router.back()
}

const goToLogin = () => {
  router.push({ name: 'landing' })
}
</script>

<style lang="scss" scoped>

</style>