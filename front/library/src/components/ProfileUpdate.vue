<template>
  <form class="p-8" @submit.prevent="onSubmit">
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

    <p v-if="errorMessage" class="mb-4 text-sm text-red-600">{{ errorMessage }}</p>
    <p v-if="successMessage" class="mb-4 text-sm text-blue-600">{{ successMessage }}</p>

    <!-- Form -->
    <div class="space-y-6">
      <div v-for="row in editRows" :key="row.key" class="flex items-start gap-4">
        <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
          <img :src="row.imgSrc" :alt="row.imgAlt" class="w-6 h-6" />
        </div>

        <div class="flex-1">
          <label class="block text-sm text-gray-600">{{ row.label }}</label>
          <select
            v-if="row.kind === 'select'"
            v-model="form[row.key]"
            class="w-full pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
          >
            <option v-for="opt in row.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
          <BaseInput
            v-else
            v-model="form[row.key]"
            class="text-gray-800 py-2"
            :type="row.type"
            :msg="row.placeholder"
          />
        </div>
      </div>
    </div>
  </form>


</template>

<script setup>
import BaseInput from "./BaseInput.vue";
import { useRouter } from "vue-router";
import { computed, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import userImg from "@/assets/imges/userImgBlue.png";

const router = useRouter();

const goProfile = () => {
  router.push({ name: "profileDetail" });
};

const authStore = useAuthStore();

const form = ref({
  name: "",
  phone: "",
  birthdate: "",
  address: "",
  occupation: "",
  interests: "",
  gender: "",
});

const initialized = ref(false);
watch(
  () => authStore.user,
  (u) => {
    if (!u || initialized.value) return;
    form.value.name = u.name || u.username || "";
    form.value.phone = u.phone || "";
    form.value.birthdate = u.birthdate || "";
    form.value.address = u.address || "";
    form.value.occupation = u.occupation || "";
    form.value.interests = u.interests || "";
    form.value.gender = u.gender || "";
    initialized.value = true;
  },
  { immediate: true }
);

const editRows = computed(() => {
  return [
    { key: "name", label: "이름", type: "text", placeholder: "이름", imgSrc: userImg, imgAlt: "유저" },
    { key: "phone", label: "전화번호", type: "text", placeholder: "전화번호", imgSrc: userImg, imgAlt: "유저" },
    { key: "birthdate", label: "생년월일", type: "text", placeholder: "YYYY-MM-DD", imgSrc: userImg, imgAlt: "유저" },
    { key: "address", label: "주소", type: "text", placeholder: "주소", imgSrc: userImg, imgAlt: "유저" },
    {
      key: "gender",
      label: "성별",
      kind: "select",
      imgSrc: userImg,
      imgAlt: "유저",
      options: [
        { value: "", label: "선택 안함" },
        { value: "male", label: "남성" },
        { value: "female", label: "여성" },
        { value: "other", label: "기타" },
      ],
    },
    {
      key: "occupation",
      label: "직업",
      kind: "select",
      imgSrc: userImg,
      imgAlt: "유저",
      options: [
        { value: "", label: "선택 안함" },
        { value: "office", label: "직장인" },
        { value: "jobseeker", label: "취준생" },
        { value: "highschool", label: "고등학생" },
        { value: "college", label: "대학생" },
        { value: "student", label: "학생" },
        { value: "unemployed", label: "백수" },
      ],
    },
    { key: "interests", label: "관심사", type: "text", placeholder: "예: 소설, 경제", imgSrc: userImg, imgAlt: "유저" },
  ];
});

const errorMessage = ref("");
const successMessage = ref("");

const onSubmit = async () => {
  errorMessage.value = "";
  successMessage.value = "";

  try {
    await authStore.updateUser({
      name: form.value.name,
      phone: form.value.phone,
      birthdate: form.value.birthdate,
      address: form.value.address,
      occupation: form.value.occupation,
      interests: form.value.interests,
      gender: form.value.gender,
    });
    successMessage.value = "저장되었습니다.";
    router.push({ name: "profileDetail" });
  } catch (err) {
    const msg =
      err?.response?.data?.error ||
      err?.response?.data?.detail ||
      "저장에 실패했습니다.";
    errorMessage.value = msg;
  }
};
</script>

<style scoped></style>
