<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="max-w-md mx-auto mb-20">
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <!-- 헤더 -->
        <div class="text-center mb-8">
          <h1 class="mb-4 text-gray-800">환영합니다</h1>
          <p class="text-gray-600">로그인하여 다양한 도서를 만나보세요</p>
        </div>

        <!-- 로그인 폼 -->
        <form class="space-y-6" @submit.prevent="onSubmit">
          <!-- 이메일 입력 -->
          <div>
            <label for="email" class="block text-sm mb-2 text-gray-700"
              >이메일</label
            >
            <BaseInput
              type="email"
              :img-src="msgImg"
              img-alt="이메일"
              msg="example@email.com"
            />
          </div>

          <!-- 비밀번호 입력 -->
          <div>
            <label for="password" class="block text-sm mb-2 text-gray-700"
              >비밀번호</label
            >
            <BaseInput
              type="password"
              :img-src="passImg"
              img-alt="비밀번호"
              msg="비밀번호를 입력하세요"
            />
          </div>

          <!-- 로그인 버튼 -->
          <BaseButton
            type="submit"
            value="로그인"
            class-name="bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          />
        </form>

        <!-- 회원가입 안내 -->
        <div class="mt-6 text-center">
          <p class="text-gray-600 mb-4">아직 회원이 아니신가요?</p>
          <BaseButton
            @click="goSignup"
            type="button"
            value="회원가입"
            class-name="bg-white border-2 border-blue-600 text-blue-600 
        hover:bg-blue-50 transition-colors flex items-center justify-center gap-2"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import BaseInput from "@/components/BaseInput.vue";
import msgImg from "@/assets/imges/msgImg.png";
import passImg from "@/assets/imges/password.png";
import BaseButton from "@/components/BaseButton.vue";
import { useRouter } from "vue-router";

const router = useRouter();
const onSubmit = () => {
  // TODO: 로그인 검증 / API 호출
  router.push({ name: "main" });
};
const goSignup = () => {
  router.push({ name: "signUp" });
};
</script>

<style lang="scss" scoped></style>
