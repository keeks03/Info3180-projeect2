<template>
  <div class="page">
    <h1 class="page-title"><HeartHandshake :size="26" /> Your Matches</h1>
    <div v-if="loading" class="spinner"></div>
    <div v-else-if="matches.length === 0" class="empty-state">
      <HeartCrack :size="54" color="#ccc" />
      <p>No mutual matches yet. Keep liking profiles!</p>
      <router-link to="/dashboard" class="btn btn-primary" style="margin-top:16px">
        <Compass :size="16" /> Browse Profiles
      </router-link>
    </div>
    <template v-else>
      <div class="matches-count alert alert-info">
        <HeartHandshake :size="16" /> You have {{ matches.length }} mutual match{{ matches.length !== 1 ? 'es' : '' }}!
      </div>
      <ProfileCard v-for="m in matches" :key="m.user_id" :profile="m">
        <template #actions>
          <router-link :to="`/messages/${m.user_id}`" class="btn btn-primary btn-sm">
            <MessageCircle :size="14" /> Message
          </router-link>
          <router-link :to="`/profile/${m.user_id}`" class="btn btn-secondary btn-sm">
            <Eye :size="14" /> View Profile
          </router-link>
        </template>
      </ProfileCard>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { matchesAPI } from '@/api'
import ProfileCard from '@/components/profile/ProfileCard.vue'
import { HeartHandshake, HeartCrack, MessageCircle, Eye, Compass } from 'lucide-vue-next'

const loading = ref(true)
const matches = ref([])
onMounted(async () => {
  try { const res = await matchesAPI.getMutual(); matches.value = res.data.matches }
  catch {} finally { loading.value = false }
})
</script>

<style scoped>
.empty-state { text-align:center; padding:60px 20px; color:var(--text-muted); display:flex; flex-direction:column; align-items:center; gap:14px; }
.matches-count { display:flex; align-items:center; gap:8px; }
</style>
