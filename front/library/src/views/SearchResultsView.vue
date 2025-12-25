<template>
    <main class="min-h-screen bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div class="mb-6">
                <h1 class="text-gray-900 text-2xl sm:text-3xl font-semibold tracking-tight mb-4">{{ title }}</h1>
                <form @submit.prevent="submitSearch" class="mt-4">
                    <div class="flex items-center gap-3">
                        <BaseInput v-model="keyword" type="text" :msg="searchPlaceholder" />
                        <div class="sm:w-40">
                            <BaseButton type="submit" value="검색" class-name="h-12 rounded-full bg-blue-600 border-blue-600 text-white hover:bg-blue-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-600/30 transition-colors"/>
                        </div>
                        <!-- 장르 내 검색 초기화 버튼 -->
                        <button
                            v-if="isSearchingInGenre"
                            type="button"
                            @click="clearGenreSearch"
                            class="h-12 px-4 rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors text-sm font-medium whitespace-nowrap"
                        >
                            검색 초기화
                        </button>
                    </div>
                </form>
            </div>

            <div v-if="isLoading" class="flex items-center justify-center py-12">
                <div class="fidget text-blue-600" role="status" aria-label="불러오는 중">
                    <span class="fidget__center" />
                    <span class="fidget__dot fidget__dot--1" />
                    <span class="fidget__dot fidget__dot--2" />
                    <span class="fidget__dot fidget__dot--3" />
                </div>
            </div>

            <div v-else>
                <p v-if="books.length === 0" class="bg-white border border-gray-200 rounded-2xl shadow-sm p-8 text-center text-gray-600">
                    검색 결과가 없습니다.
                </p>

                <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    <BookCard
                        v-for="book in books"
                        :key="book.id"
                        :book="book"
                    />
                </div>
            </div>
        </div>
    </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BookCard from '@/components/BookCard.vue'
import { bookAPI, metaAPI } from '@/api'
import BaseInput from '@/components/BaseInput.vue'
import BaseButton from '@/components/BaseButton.vue'

const route = useRoute()
const search = computed(() => route.params.search)
const genreId = computed(() => route.params.genreId)

const genreName = ref('')
const genreNameById = ref({})
const router = useRouter()

// Keep a local keyword so the input stays visible and editable on results page
const keyword = ref(String(search.value || '').trim())

// 검색창 placeholder 동적 변경
const searchPlaceholder = computed(() => {
    const g = String(genreId.value || '').trim()
    if (g) {
        const name = String(genreName.value || '').trim()
        return name ? `${name} 내에서 검색` : '이 장르 내에서 검색'
    }
    return '책 제목, 저자, 카테고리로 검색'
})

// 장르 내 검색 초기화
const clearGenreSearch = () => {
    keyword.value = ''
    isSearchingInGenre.value = false
    fetchBooks()
}

watch(search, (v) => {
    keyword.value = String(v || '').trim()
})

const ensureGenresLoaded = async () => {
    const cached = genreNameById.value
    if (cached && Object.keys(cached).length > 0) return
    try {
        const res = await metaAPI.getGenres()
        const list = Array.isArray(res.data) ? res.data : []
        const map = {}
        for (const g of list) {
            if (!g?.id) continue
            map[String(g.id)] = String(g.name || '').trim()
        }
        genreNameById.value = map
    } catch (e) {
        genreNameById.value = {}
    }
}

const title = computed(() => {
    const g = String(genreId.value || '').trim()
    const q = String(keyword.value || '').trim()
    
    if (g) {
        const name = String(genreName.value || '').trim()
        // 장르 내에서 검색 중인 경우
        if (q && isSearchingInGenre.value) {
            return name ? `${name} - "${q}" 검색 결과` : `장르별 도서 - "${q}" 검색 결과`
        }
        return name ? name : '장르별 도서'
    }
    return `"${q}" 검색 결과`
})

// 장르 내 검색 여부를 추적
const isSearchingInGenre = ref(false)

const books = ref([])
const isLoading = ref(false)

const fetchBooks = async () => {
        isLoading.value = true
        try {
            const g = String(genreId.value || '').trim()
            const q = String(keyword.value || '').trim()
            
            if (g) {
                await ensureGenresLoaded()
                genreName.value = genreNameById.value?.[g] || ''
                
                // 장르 내에서 검색어가 있으면 함께 검색
                const params = { genre: g }
                if (q && isSearchingInGenre.value) {
                    params.search = q
                }
                
                const response = await bookAPI.getBooks(params)
                books.value = Array.isArray(response.data) ? response.data : []
                return
            }
            genreName.value = ''
            isSearchingInGenre.value = false
            const response = await bookAPI.getBooks({ search: q })
            books.value = Array.isArray(response.data) ? response.data : []
        } catch (e) {
            books.value = []
        } finally {
            isLoading.value = false
        }
}

onMounted(() => {
    fetchBooks()
})

watch([search, genreId], () => {
    // route 파라미터가 바뀌면 장르 내 검색 상태 초기화
    isSearchingInGenre.value = false
    keyword.value = String(search.value || '').trim()
    fetchBooks()
})

const submitSearch = () => {
    const q = String(keyword.value || '').trim()
    if (!q) return
    
    const g = String(genreId.value || '').trim()
    
    // 장르 페이지에 있으면 해당 장르 내에서 검색
    if (g) {
        isSearchingInGenre.value = true
        fetchBooks()
    } else {
        // 일반 검색 페이지면 전체 검색
        router.push({ name: 'searchResult', params: { search: q } })
    }
}
</script>

<style lang="scss" scoped>

.fidget {
    position: relative;
    width: 56px;
    height: 56px;
    animation: fidget-rotate 900ms linear infinite;
}

.fidget__center {
    position: absolute;
    inset: 0;
    margin: auto;
    width: 14px;
    height: 14px;
    border-radius: 9999px;
    background: currentColor;
    opacity: 0.85;
}

.fidget__dot {
    position: absolute;
    width: 12px;
    height: 12px;
    border-radius: 9999px;
    background: currentColor;
}

.fidget__dot--1 {
    left: 50%;
    top: 4px;
    transform: translateX(-50%);
}

.fidget__dot--2 {
    left: 10px;
    bottom: 10px;
}

.fidget__dot--3 {
    right: 10px;
    bottom: 10px;
}

@keyframes fidget-rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

@media (prefers-reduced-motion: reduce) {
    .fidget {
        animation: none;
    }
}

</style>