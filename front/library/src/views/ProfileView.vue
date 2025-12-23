<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white rounded-xl shadow-lg overflow-hidden">
      <!-- 상단 프로필 영역 -->
      <ProfileHeader />

      <!-- 회원 정보 영역 -->
   <RouterView />
    </div>
  </div>
</template>

<script setup>
import ProfileHeader from "@/components/ProfileHeader.vue";
import { RouterView } from "vue-router";
import { ref } from "vue";
import userImg from "@/assets/imges/userImgBlue.png";




const infos = ref([
  { label: "이름", value: "사용자", imgSrc: userImg, imgAlt: "유저 이미지" },
  { label: "이름", value: "사용자", imgSrc: userImg, imgAlt: "유저 이미지" },
  { label: "이름", value: "사용자", imgSrc: userImg, imgAlt: "유저 이미지" },
  { label: "이름", value: "사용자", imgSrc: userImg, imgAlt: "유저 이미지" },
  { label: "이름", value: "사용자", imgSrc: userImg, imgAlt: "유저 이미지" },
  { label: "이름", value: "사용자", imgSrc: userImg, imgAlt: "유저 이미지" },
]);
</script>

<style lang="scss" scoped></style>
