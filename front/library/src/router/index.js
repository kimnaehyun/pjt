import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '@/views/LandingView.vue'
import SignUp from '@/views/SignUp.vue'
import MainView from '@/views/MainView.vue'
import BookDetailView from '@/views/BookDetailView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SearchResultsView from '@/views/SearchResultsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUp
    },
    {
      path: '/main',
      name: 'main',
      component: MainView,
      meta: { requiresAuth: true }
    },
    {
      path: '/books/:id',
      name: 'bookDetail',
      component: BookDetailView
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/search',
      name: 'search',
      component: SearchResultsView
    }
  ]
})

// 인증 가드
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next({ name: 'landing' })
  } else {
    next()
  }
})

export default router
