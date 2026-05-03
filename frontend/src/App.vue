<template>
  <div id="app-root">
    <NavBar v-if="showNav" />
    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/common/NavBar.vue'

const auth = useAuthStore()
const route = useRoute()
const guestRoutes = ['Home', 'Login', 'Register']
const showNav = computed(() => auth.isAuthenticated && !guestRoutes.includes(route.name))
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
