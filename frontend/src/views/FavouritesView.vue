<template>
  <div class="page">
    <h1 class="page-title"><Bookmark :size="26" /> Saved Profiles</h1>
    <div v-if="loading" class="spinner"></div>
    <div v-else-if="favourites.length === 0" class="empty-state">
      <BookmarkX :size="54" color="#ccc" />
      <p>You haven't saved any profiles yet.</p>
      <router-link to="/dashboard" class="btn btn-primary" style="margin-top:16px">
        <Compass :size="16" /> Browse Profiles
      </router-link>
    </div>
    <template v-else>
      <p class="count-info"><Star :size="14" /> {{ favourites.length }} saved profile{{ favourites.length !== 1 ? 's' : '' }}</p>
      <ProfileCard
        v-for="p in favourites" :key="p.user_id" :profile="p"
        :show-like="true" :show-favourite="true" :is-fav="true"
        @like="handleLike" @favourite="removeFav"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { favouritesAPI, matchesAPI } from '@/api'
import ProfileCard from '@/components/profile/ProfileCard.vue'
import { Bookmark, BookmarkX, Star, Compass } from 'lucide-vue-next'

const loading = ref(true)
const favourites = ref([])
onMounted(async () => {
  try { const res = await favouritesAPI.getAll(); favourites.value = res.data.favourites }
  catch {} finally { loading.value = false }
})
async function handleLike(profile) {
  const res = await matchesAPI.action(profile.user_id, 'like')
  if (res.data.is_mutual) alert(`It's a match with ${profile.first_name}!`)
}
async function removeFav(profile) {
  await favouritesAPI.remove(profile.id)
  favourites.value = favourites.value.filter(f => f.id !== profile.id)
}
</script>

<style scoped>
.empty-state { text-align:center; padding:60px 20px; color:var(--text-muted); display:flex; flex-direction:column; align-items:center; gap:14px; }
.count-info { color:var(--text-muted); font-size:0.9rem; margin-bottom:14px; display:flex; align-items:center; gap:5px; }
</style>
