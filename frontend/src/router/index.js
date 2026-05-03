import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/HomeView.vue'), meta: { guest: true } },
  { path: '/login', name: 'Login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  { path: '/profile/create', name: 'CreateProfile', component: () => import('@/views/CreateProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/profile/edit', name: 'EditProfile', component: () => import('@/views/EditProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/profile/:userId', name: 'ViewProfile', component: () => import('@/views/ProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/matches', name: 'Matches', component: () => import('@/views/MatchesView.vue'), meta: { requiresAuth: true } },
  { path: '/messages', name: 'Messages', component: () => import('@/views/MessagesView.vue'), meta: { requiresAuth: true } },
  { path: '/messages/:userId', name: 'Conversation', component: () => import('@/views/ConversationView.vue'), meta: { requiresAuth: true } },
  { path: '/search', name: 'Search', component: () => import('@/views/SearchView.vue'), meta: { requiresAuth: true } },
  { path: '/favourites', name: 'Favourites', component: () => import('@/views/FavouritesView.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (!auth.checked) {
    await auth.checkAuth()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'Login' })
  }

  if (to.meta.guest && auth.isAuthenticated && to.name !== 'Home') {
    return next({ name: 'Dashboard' })
  }

  // If authenticated but no profile and trying to go to a protected page (not profile creation)
  if (auth.isAuthenticated && !auth.hasProfile &&
      to.name !== 'CreateProfile' && to.meta.requiresAuth) {
    return next({ name: 'CreateProfile' })
  }

  next()
})

export default router
