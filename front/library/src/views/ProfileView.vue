<template>
  <main class="min-h-screen bg-gray-50">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="bg-white border border-gray-200 rounded-2xl shadow-md overflow-hidden">
        <!-- 상단 프로필 영역 -->
        <ProfileHeader />

        <!-- 회원 정보 영역 -->
        <RouterView />
      </div>
    </div>
  </main>
</template>

<script setup>
import ProfileHeader from "@/components/ProfileHeader.vue";
import { RouterView } from "vue-router";
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: "landing" });
    return;
  }

  try {
    await authStore.fetchUser();
  } catch (e) {
    // 401 등은 axios interceptor에서 landing으로 이동 처리됨
  }
});
</script>

<style lang="scss" scoped></style>
