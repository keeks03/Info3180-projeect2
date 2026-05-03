<template>
  <div class="auth-page">
    <div class="profile-form card">
      <div class="auth-logo">
        <HeartHandshake :size="28" color="#6c63ff" /><span>DriftDater</span>
      </div>
      <h2>Complete Your Profile</h2>
      <p class="auth-sub">Help others get to know you</p>
      <div v-if="error" class="alert alert-error"><AlertCircle :size="15" /> {{ error }}</div>

      <div class="form-row">
        <div class="form-group">
          <label><UserCircle :size="13" /> First Name *</label>
          <input v-model="form.first_name" type="text" placeholder="First Name" />
        </div>
        <div class="form-group">
          <label><UserCircle :size="13" /> Last Name *</label>
          <input v-model="form.last_name" type="text" placeholder="Last Name" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label><Calendar :size="13" /> Date of Birth *</label>
          <input v-model="form.date_of_birth" type="date" />
        </div>
        <div class="form-group">
          <label><Users :size="13" /> Gender *</label>
          <select v-model="form.gender">
            <option value="">Select gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="non-binary">Non-binary</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label><Heart :size="13" /> Looking For</label>
        <select v-model="form.looking_for">
          <option value="any">Any</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </div>
      <div class="form-group">
        <label><FileText :size="13" /> Bio</label>
        <textarea v-model="form.bio" placeholder="Tell potential matches about yourself…" rows="3"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label><MapPin :size="13" /> City</label>
          <input v-model="form.city" type="text" placeholder="City" />
        </div>
        <div class="form-group">
          <label><Globe :size="13" /> Country</label>
          <input v-model="form.country" type="text" placeholder="Country" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label><Briefcase :size="13" /> Occupation</label>
          <input v-model="form.occupation" type="text" placeholder="Your occupation" />
        </div>
        <div class="form-group">
          <label><GraduationCap :size="13" /> Education</label>
          <select v-model="form.education_level">
            <option value="">Select</option>
            <option value="high_school">High School</option>
            <option value="bachelor">Bachelor's</option>
            <option value="master">Master's</option>
            <option value="phd">PhD</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label><Sparkles :size="13" /> Interests (min 3) *</label>
        <InterestSelector v-model="form.interests" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Min Age Pref</label>
          <input v-model.number="form.min_age_preference" type="number" min="18" max="99" />
        </div>
        <div class="form-group">
          <label>Max Age Pref</label>
          <input v-model.number="form.max_age_preference" type="number" min="18" max="99" />
        </div>
      </div>
      <div class="form-group">
        <label><Camera :size="13" /> Profile Picture</label>
        <div class="pic-upload-area" @click="$refs.picFileInput.click()">
          <img v-if="previewUrl" :src="previewUrl" class="pic-preview-img" alt="Preview" />
          <div v-else class="pic-placeholder">
            <Upload :size="26" color="#6c63ff" />
            <span>Click to upload photo</span>
            <small>PNG, JPG, WEBP up to 16MB</small>
          </div>
        </div>
        <input ref="picFileInput" type="file" accept="image/*" @change="onFileChange" style="display:none" />
      </div>
      <div class="form-group">
        <label style="display:flex;align-items:center;gap:6px;cursor:pointer;">
          <input type="checkbox" v-model="form.is_public" /> <Eye :size="13" /> Make profile public
        </label>
      </div>
      <button class="btn btn-primary btn-lg" style="width:100%" @click="handleSubmit" :disabled="loading">
        <UserCheck v-if="!loading" :size="18" /> {{ loading ? 'Creating profile…' : 'Create Profile' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { profilesAPI } from '@/api'
import InterestSelector from '@/components/profile/InterestSelector.vue'
import {
  HeartHandshake, UserCircle, Calendar, Users, Heart, FileText,
  MapPin, Globe, Briefcase, GraduationCap, Sparkles, Camera,
  Upload, Eye, UserCheck, AlertCircle
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const error = ref(''), loading = ref(false), previewUrl = ref(null), selectedFile = ref(null)
const form = reactive({
  first_name:'', last_name:'', date_of_birth:'', gender:'', looking_for:'any',
  bio:'', city:'', country:'', occupation:'', education_level:'',
  interests:[], min_age_preference:18, max_age_preference:99, is_public:true,
})
function onFileChange(e) {
  const file = e.target.files[0]
  if (file) { selectedFile.value = file; previewUrl.value = URL.createObjectURL(file) }
}
async function handleSubmit() {
  error.value = ''
  if (!form.first_name || !form.last_name || !form.date_of_birth || !form.gender) {
    error.value = 'Please fill all required fields'; return
  }
  if (form.interests.length < 3) { error.value = 'Please add at least 3 interests'; return }
  loading.value = true
  try {
    const fd = new FormData()
    Object.entries(form).forEach(([k, v]) => {
      if (k === 'interests') v.forEach(i => fd.append('interests', i))
      else fd.append(k, v)
    })
    if (selectedFile.value) fd.append('profile_picture', selectedFile.value)
    await profilesAPI.create(fd)
    auth.setHasProfile(true)
    router.push('/dashboard')
  } catch (e) { error.value = e.response?.data?.error || 'Failed to create profile' }
  finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height:100vh; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#f8f7ff,#e8e6ff); padding:20px; }
.profile-form { width:100%; max-width:600px; }
.auth-logo { display:flex; align-items:center; justify-content:center; gap:8px; font-size:1.4rem; font-weight:900; color:var(--primary); margin-bottom:12px; }
h2 { font-size:1.6rem; font-weight:800; text-align:center; margin-bottom:4px; }
.auth-sub { color:var(--text-muted); text-align:center; margin-bottom:22px; }
.form-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.form-group label { display:flex; align-items:center; gap:5px; }
.pic-upload-area { border:2px dashed var(--border); border-radius:var(--radius-sm); padding:20px; cursor:pointer; text-align:center; transition:border-color 0.2s; display:flex; align-items:center; justify-content:center; min-height:110px; }
.pic-upload-area:hover { border-color:var(--primary); }
.pic-placeholder { display:flex; flex-direction:column; align-items:center; gap:6px; color:var(--text-muted); }
.pic-placeholder span { font-weight:600; color:var(--primary); }
.pic-placeholder small { font-size:0.78rem; }
.pic-preview-img { width:90px; height:90px; border-radius:50%; object-fit:cover; border:3px solid var(--primary); }
@media(max-width:500px){.form-row{grid-template-columns:1fr;}}
</style>
