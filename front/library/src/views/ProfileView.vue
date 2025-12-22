<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white rounded-xl shadow-lg overflow-hidden">
      <!-- 상단 프로필 영역 -->
      <ProfileHeader />

      <!-- 회원 정보 영역 -->
      <div class="p-8">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-gray-800">회원정보</h2>
          <button
            class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-pen w-4 h-4"
              aria-hidden="true"
            >
              <path
                d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"
              ></path>
            </svg>
            수정하기
          </button>
        </div>

        <form class="space-y-6">
          <ProfileInfo
            v-for="info in infos"
            :field="info.label"
            :value="info.value"
            :img-src="info.imgSrc"
            :img-alt="info.imgAlt"
          />
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import ProfileHeader from "@/components/ProfileHeader.vue";
import ProfileInfo from "@/components/ProfileInfo.vue";
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
