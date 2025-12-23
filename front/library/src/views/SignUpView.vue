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
                
          <BaseInput v-model="name" type="text" msg="홍길동" :img-src="userImg" img-alt="이름" />
        </div>

        <!-- 이메일 -->
        <div>
          <label for="email" class="block text-sm mb-2 text-gray-700">이메일</label>
            <BaseInput v-model="email" type="email" msg="example@email.com" :img-src="mailImg" img-alt="이메일" />
        </div>

        <!-- 전화번호 -->
        <div>
          <label for="phone" class="block text-sm mb-2 text-gray-700">전화번호</label>
          <BaseInput v-model="phone" type="tel" msg="010-1234-5678" />
        </div>

        <!-- 비밀번호 -->
        <div>
          <label for="password" class="block text-sm mb-2 text-gray-700">비밀번호</label>
       <BaseInput v-model="password" type="password" msg="비밀번호를 입력하세요" :img-src="passwordImg" img-alt="비밀번호" />
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <label for="confirmPassword" class="block text-sm mb-2 text-gray-700">비밀번호 확인</label>
          <BaseInput v-model="confirmPassword" type="password" msg="비밀번호를 다시 입력하세요" :img-src="passwordImg" img-alt="비밀번호 확인" />
        </div>

        <!-- 생년월일 -->
        <div>
          <label for="birthdate" class="block text-sm mb-2 text-gray-700">생년월일</label>
          <BaseInput v-model="birthdate" type="date" msg="YYYY-MM-DD" />
        </div>

        <!-- 선택 사항 -->
        <div class="border-t pt-4">
          <p class="text-sm text-gray-600 mb-4">선택 사항</p>
          <div class="space-y-4">
            <!-- 성별 -->
            <div>
              <label for="gender" class="block text-sm mb-2 text-gray-700">성별</label>
              <select
                id="gender"
                v-model="gender"
                class="w-full pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
              >
                <option value="">선택 안함</option>
                <option value="male">남성</option>
                <option value="female">여성</option>
                <option value="other">기타</option>
              </select>
            </div>

            <!-- 직업 -->
            <div>
              <label for="occupation" class="block text-sm mb-2 text-gray-700">직업</label>
              <select
                id="occupation"
                v-model="occupation"
                class="w-full pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
              >
                <option value="">선택 안함</option>
                <option value="office">직장인</option>
                <option value="jobseeker">취준생</option>
                <option value="highschool">고등학생</option>
                <option value="college">대학생</option>
                <option value="student">학생</option>
                <option value="unemployed">백수</option>
              </select>
            </div>

            <!-- 관심사 -->
            <div>
              <label for="interests" class="block text-sm mb-2 text-gray-700">관심사</label>
              <BaseInput v-model="interests" type="text" msg="예: 소설, 자기계발, 경제" />
            </div>

            <!-- 주소 -->
            <div>
              <label for="address" class="block text-sm mb-2 text-gray-700">주소</label>
              <BaseInput v-model="address" type="text" msg="주소를 입력하세요" />
            </div>
          </div>
        </div>

        <!-- 가입하기 버튼 -->
        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>
        
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
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const phone = ref('')
const gender = ref('')
const occupation = ref('')
const interests = ref('')
const birthdate = ref('')
const address = ref('')
const errorMessage = ref('')

const goLanding = () => {
  router.back()
};
const onSubmit = () => {
  errorMessage.value = ''
  if (!name.value.trim()) {
    errorMessage.value = '이름을 입력해주세요.'
    return
  }
  if (!email.value.trim() || !password.value) {
    errorMessage.value = '이메일과 비밀번호를 입력해주세요.'
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  if (!birthdate.value) {
    errorMessage.value = '생년월일을 입력해주세요.'
    return
  }
  if (!address.value.trim()) {
    errorMessage.value = '주소를 입력해주세요.'
    return
  }

  authStore
    .signup({
      name: name.value,
      email: email.value,
      password: password.value,
      phone: phone.value,
      gender: gender.value,
      occupation: occupation.value,
      interests: interests.value,
      birthdate: birthdate.value,
      address: address.value,
    })
    .then(() => {
      router.push({ name: 'main' })
    })
    .catch((err) => {
      const msg =
        err?.response?.data?.error ||
        err?.response?.data?.detail ||
        '회원가입에 실패했습니다.'
      errorMessage.value = msg
    })
};
</script>

<style lang="scss" scoped>

</style>