<template>
  <div class="page">
    <h1 class="page-title"><Search :size="26" /> Search Profiles</h1>

    <div class="card filter-card">
      <div class="filter-grid">
        <div class="form-group">
          <label><User :size="13" /> Name / Bio</label>
          <input v-model="filters.name" type="text" placeholder="Search name or bio…" />
        </div>
        <div class="form-group">
          <label><MapPin :size="13" /> City</label>
          <input v-model="filters.city" type="text" placeholder="City" />
        </div>
        <div class="form-group">
          <label><Globe :size="13" /> Country</label>
          <input v-model="filters.country" type="text" placeholder="Country" />
        </div>
        <div class="form-group">
          <label><Users :size="13" /> Gender</label>
          <select v-model="filters.gender">
            <option value="">Any</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="non-binary">Non-binary</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="form-group">
          <label><CalendarDays :size="13" /> Min Age</label>
          <input v-model.number="filters.min_age" type="number" min="18" max="99" placeholder="18" />
        </div>
        <div class="form-group">
          <label><CalendarDays :size="13" /> Max Age</label>
          <input v-model.number="filters.max_age" type="number" min="18" max="99" placeholder="99" />
        </div>
      </div>

      <div class="form-group">
        <label><Sparkles :size="13" /> Interests</label>
        <div class="interest-filter">
          <span v-for="i in availableInterests" :key="i.id" class="tag"
            :class="{ 'tag-active': filters.interests.includes(i.name) }"
            @click="toggleInterest(i.name)">{{ i.name }}</span>
        </div>
      </div>

      <div class="form-group">
        <label><ArrowUpDown :size="13" /> Sort By</label>
        <select v-model="filters.sort">
          <option value="match_score">Best Match</option>
          <option value="newest">Newest</option>
          <option value="name">Name A–Z</option>
        </select>
      </div>

      <div class="filter-actions">
        <button class="btn btn-primary" @click="doSearch" :disabled="searching">
          <Search :size="15" /> {{ searching ? 'Searching…' : 'Search' }}
        </button>
        <button class="btn btn-secondary" @click="resetFilters"><X :size="15" /> Reset</button>
      </div>
    </div>

    <div v-if="searched">
      <p class="results-count"><ListFilter :size="14" /> {{ results.length }} result{{ results.length !== 1 ? 's' : '' }} found</p>
      <div v-if="results.length === 0" class="empty-state">
        <SearchX :size="48" color="#ccc" />
        <p>No profiles match your filters. Try adjusting your search.</p>
      </div>
      <ProfileCard v-for="p in results" :key="p.user_id" :profile="p"
        :show-like="true" :show-pass="true" :show-favourite="true"
        :is-fav="favouriteIds.has(p.id)"
        @like="handleLike" @pass="handlePass" @favourite="toggleFavourite" />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { searchAPI, matchesAPI, favouritesAPI } from '@/api'
import ProfileCard from '@/components/profile/ProfileCard.vue'
import { Search, User, MapPin, Globe, Users, CalendarDays, Sparkles, ArrowUpDown, X, SearchX, ListFilter } from 'lucide-vue-next'

const filters = reactive({ name:'', city:'', country:'', gender:'', min_age:'', max_age:'', interests:[], sort:'match_score' })
const results = ref([]), searching = ref(false), searched = ref(false)
const availableInterests = ref([]), favouriteIds = ref(new Set())

onMounted(async () => {
  try {
    const [ints, favs] = await Promise.all([searchAPI.getInterests(), favouritesAPI.getAll()])
    availableInterests.value = ints.data.interests
    favouriteIds.value = new Set(favs.data.favourites.map(f => f.id))
    await doSearch()
  } catch {}
})

function toggleInterest(name) {
  const idx = filters.interests.indexOf(name)
  if (idx >= 0) { filters.interests.splice(idx, 1) } else { filters.interests.push(name) }
}
function resetFilters() {
  Object.assign(filters, { name:'', city:'', country:'', gender:'', min_age:'', max_age:'', interests:[], sort:'match_score' })
  results.value = []; searched.value = false
}
async function doSearch() {
  searching.value = true; searched.value = true
  try {
    const params = {}
    if (filters.name) params.name = filters.name
    if (filters.city) params.city = filters.city
    if (filters.country) params.country = filters.country
    if (filters.gender) params.gender = filters.gender
    if (filters.min_age) params.min_age = filters.min_age
    if (filters.max_age) params.max_age = filters.max_age
    if (filters.interests.length) params.interests = filters.interests
    params.sort = filters.sort
    const res = await searchAPI.search(params)
    results.value = res.data.profiles
  } catch {} finally { searching.value = false }
}
async function handleLike(profile) {
  const res = await matchesAPI.action(profile.user_id, 'like')
  if (res.data.is_mutual) alert(`It's a match with ${profile.first_name}!`)
}
async function handlePass(profile) { await matchesAPI.action(profile.user_id, 'pass') }
async function toggleFavourite(profile) {
  if (favouriteIds.value.has(profile.id)) {
    await favouritesAPI.remove(profile.id); favouriteIds.value.delete(profile.id)
  } else {
    await favouritesAPI.add(profile.id); favouriteIds.value.add(profile.id)
  }
  favouriteIds.value = new Set(favouriteIds.value)
}
</script>

<style scoped>
.filter-card { margin-bottom:24px; }
.filter-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:14px; }
.form-group label { display:flex; align-items:center; gap:5px; }
.interest-filter { display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }
.tag { cursor:pointer; }
.tag-active { background:var(--primary) !important; color:#fff !important; }
.filter-actions { display:flex; gap:12px; margin-top:8px; }
.results-count { color:var(--text-muted); font-size:0.9rem; margin-bottom:14px; display:flex; align-items:center; gap:5px; }
.empty-state { text-align:center; padding:60px 20px; color:var(--text-muted); display:flex; flex-direction:column; align-items:center; gap:14px; }
</style>
