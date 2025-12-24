import { createRouter, createWebHistory } from "vue-router";
import LandingView from "@/views/LandingView.vue";
import MainView from "@/views/MainView.vue";
import SearchResultsView from "@/views/SearchResultsView.vue";
import BookDetailView from "@/views/BookDetailView.vue";
import SignUpView from "@/views/SignUpView.vue";
import ProfileView from "@/views/ProfileView.vue";
import ProfileInfo from "@/components/ProfileInfo.vue";
import ProfileUpdate from "@/components/ProfileUpdate.vue";
import ProfileLibrary from "@/components/ProfileLibrary.vue";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "landing",
      component: LandingView,
    },
    {
      path: "/main",
      name: "main",
      component: MainView,
    },
    {
      path: "/main/books/:id",
      name: "bookDetail",
      component: BookDetailView,
      props: true,
    },
    {
      path: "/main/genres/:genreId",
      name: "genreResult",
      component: SearchResultsView,
      props: true,
    },
    {
      path: "/main/ai",
      name: "aiSearchResult",
      component: SearchResultsView,
    },
    {
      path: "/main/:search",
      name: "searchResult",
      component: SearchResultsView,
    },
    {
      path: "/signup",
      name: "signUp",
      component: SignUpView,
    },
    {
      path: "/main/profile",
      component: ProfileView,
      children: [
        {
          path: "",
          name: "profileHome",
          component: ProfileLibrary,
        },
        {
          path: "info",
          name: "profileDetail",
          component: ProfileInfo,
        },
        {
          path: "update",
          name: "profileUpdate",
          component: ProfileUpdate,
        },
      ],
    },
  ],
});


router.beforeEach((to, from) => {
  const accountStore = useAuthStore()

  // 로그인 필요 페이지 정의
  const protectedRoutes = ['main', 'bookDetail', 'genreResult', 'aiSearchResult'];

  if (protectedRoutes.includes(to.name) && !accountStore.isLogin) {
    window.alert('로그인이 필요합니다');
    // 랜딩으로 이동 + 로그인 모달 열기
    accountStore.showLoginModal = true; // store에서 모달 상태 관리한다고 가정
    return { name: 'landing' };
  }

  // 이미 로그인 상태에서 랜딩 접근 제한
  if (to.name === 'landing' && accountStore.isLogin) {
    window.alert('이미 로그인이 되어있습니다');
    return { name: 'main' };
  }
});
export default router;
