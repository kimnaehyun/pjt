<template>
<nav class="bg-white shadow-md sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16 gap-4">

      <!-- Left: hamburger + logo -->
      <div class="flex items-center gap-3">
        <!-- Genre hamburger -->
        <div class="relative">
          <button
          v-if="authStore.isAuthenticated"
            type="button"
            class="p-2 rounded-lg text-gray-700 hover:text-blue-600 transition-colors"
            aria-label="장르 메뉴"
            @click="toggleGenreMenu"
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
              class="w-6 h-6"
            >
              <path d="M4 6h16" />
              <path d="M4 12h16" />
              <path d="M4 18h16" />
            </svg>
          </button>

          <div
            v-if="isGenreMenuOpen"
            class="absolute left-0 top-full mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-md overflow-hidden"
            role="menu"
          >
            <button
              v-for="g in genres"
              :key="g.id"
              type="button"
              class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              role="menuitem"
              @click="goGenre(g.id)"
            >
              {{ g.name }}
            </button>
          </div>
        </div>

        <!-- Logo -->
       <!-- Logo -->
<button
  type="button"
  @click="goLogo"
  class="flex items-center gap-2 hover:opacity-80 transition-opacity"
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
    class="w-8 h-8 text-blue-600"
  >
    <path d="M12 7v14" />
    <path
      d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5
         a4 4 0 0 1 4 4
         a4 4 0 0 1 4-4h5
         a1 1 0 0 1 1 1v13
         a1 1 0 0 1-1 1h-6
         a3 3 0 0 0-3 3
         a3 3 0 0 0-3-3z"
    />
  </svg>
  <span class="text-blue-600">bookfit</span>
</button>

      </div>

      <!-- Right menu -->
      <div class="flex items-center gap-4">
        
        <!-- Profile -->
        <a
          v-if="authStore.isAuthenticated"
          href="/main/profile"
          data-discover="true"
          class="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors"
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
            class="lucide lucide-user w-4 h-4"
          >
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <span class="hidden sm:inline">{{ authStore.user?.name  }}</span>
        </a>

        <!-- Logout -->
        <button
          v-if="authStore.isAuthenticated"
          type="button"
          class="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          @click="logOut"
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
            class="lucide lucide-log-out w-4 h-4"
          >
            <path d="m16 17 5-5-5-5" />
            <path d="M21 12H9" />
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          </svg>
          <span class="hidden sm:inline">로그아웃</span>
        </button>

      </div>
    </div>
  </div>
</nav>

</template>

<script setup>
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import { metaAPI } from '@/api'

  const router = useRouter()
  const authStore = useAuthStore()

  const genres = ref([])
  const selectedGenreId = ref('')
  const isGenreMenuOpen = ref(false)

  const fetchGenres = async () => {
    try {
      const res = await metaAPI.getGenres()
      genres.value = Array.isArray(res.data) ? res.data : []
    } catch (e) {
      genres.value = []
    }
  }

const goLogo = () => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'main' })
  } else {
    return
  }
}

  const onGenreChange = () => {
    const id = String(selectedGenreId.value || '').trim()
    if (!id) return
    router.push({ name: 'genreResult', params: { genreId: id } })
  }

  const toggleGenreMenu = () => {
    isGenreMenuOpen.value = !isGenreMenuOpen.value
  }

  const goGenre = (id) => {
    const genreId = String(id || '').trim()
    if (!genreId) return
    selectedGenreId.value = genreId
    isGenreMenuOpen.value = false
    router.push({ name: 'genreResult', params: { genreId } })
  }

  const logOut = () => {
    authStore.logout()
    router.replace({ name: 'landing' })
  }

  const goLogin = () => {
    router.push({ name: 'landing' })
  }

  onMounted(() => {
    fetchGenres()
  })
</script>

<style lang="scss" scoped></style>
