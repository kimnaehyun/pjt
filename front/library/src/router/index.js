import { createRouter, createWebHistory } from "vue-router";
import LandingView from "@/views/LandingView.vue";
import MainView from "@/views/MainView.vue";
import SearchResultsView from "@/views/SearchResultsView.vue";
import BookDetailView from "@/views/BookDetailView.vue";
import SignUpView from "@/views/SignUpView.vue";
import ProfileView from "@/views/ProfileView.vue";
import ProfileInfo from "@/components/ProfileInfo.vue";
import ProfileUpdate from "@/components/ProfileUpdate.vue";

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

export default router;
