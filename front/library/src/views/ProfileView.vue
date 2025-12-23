<template>
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <div class="bg-white rounded-xl shadow-lg overflow-hidden">
    
    <!-- 상단 프로필 영역 -->
    <ProfileHeader :user="user" />

    <!-- 회원 정보 영역 -->
    <div class="p-8">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-gray-800">회원정보</h2>
        <button 
          v-if="!isEditing"
          @click="startEdit"
          class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-pen w-4 h-4" aria-hidden="true">
            <path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"></path>
          </svg>
          수정하기
        </button>
      </div>

      <form v-if="!loading" class="space-y-6">
        <div v-for="field in userFields" :key="field.key" class="flex items-center gap-4">
          <label class="w-24 text-gray-700 font-medium">{{ field.label }}</label>
          <input 
            v-if="isEditing"
            v-model="editForm[field.key]"
            :type="field.type || 'text'"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-600"
            :placeholder="field.placeholder"
          />
          <p v-else class="flex-1 text-gray-600">
            {{ user?.[field.key] || '-' }}
          </p>
        </div>

        <div v-if="isEditing" class="flex gap-4 justify-end pt-4">
          <button 
            type="button"
            @click="cancelEdit"
            class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            취소
          </button>
          <button 
            type="button"
            @click="saveProfile"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            저장
          </button>
        </div>
      </form>

      <!-- 로그아웃 버튼 -->
      <div class="mt-8 pt-6 border-t">
        <button 
          @click="handleLogout"
          class="w-full px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
          로그아웃
        </button>
      </div>
    </div>
  </div>
</div>

</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ProfileHeader from '@/components/ProfileHeader.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const isEditing = ref(false)
const editForm = ref({})

const user = computed(() => authStore.user)

const userFields = [
  { key: 'name', label: '이름', placeholder: '이름을 입력하세요' },
  { key: 'email', label: '이메일', placeholder: 'email@example.com' },
  { key: 'nickname', label: '닉네임', placeholder: '닉네임을 입력하세요' },
  { key: 'age', label: '나이', type: 'number', placeholder: '나이를 입력하세요' },
  { key: 'phone', label: '전화번호', placeholder: '010-1234-5678' },
  { key: 'birthdate', label: '생년월일', type: 'date' },
  { key: 'address', label: '주소', placeholder: '주소를 입력하세요' }
]

const startEdit = () => {
  editForm.value = { ...user.value }
  isEditing.value = true
}

const cancelEdit = () => {
  editForm.value = {}
  isEditing.value = false
}

const saveProfile = async () => {
  try {
    loading.value = true
    await authStore.updateUser(editForm.value)
    isEditing.value = false
    alert('프로필이 수정되었습니다.')
  } catch (error) {
    console.error('Failed to update profile:', error)
    alert('프로필 수정에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  if (confirm('로그아웃 하시겠습니까?')) {
    authStore.logout()
    router.push({ name: 'landing' })
  }
}

onMounted(async () => {
  try {
    loading.value = true
    await authStore.fetchUser()
  } catch (error) {
    console.error('Failed to fetch user:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>

</style>