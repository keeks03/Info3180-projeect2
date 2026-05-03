<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-logo">
        <HeartHandshake :size="32" color="#6c63ff" />
        <span>DriftDater</span>
      </div>
      <h2>Sign Up</h2>
      <p class="auth-sub">Create your account to find your match</p>

      <div v-if="error" class="alert alert-error">
        <AlertCircle :size="16" /> {{ error }}
      </div>

      <!-- Step indicator -->
      <div class="steps">
        <div class="step" :class="{ active: step >= 1, done: step > 1 }">
          <div class="step-dot">
            <Check v-if="step > 1" :size="13" />
            <span v-else>1</span>
          </div>
          <span>Account</span>
        </div>
        <div class="step-line"></div>
        <div class="step" :class="{ active: step >= 2, done: step > 2 }">
          <div class="step-dot">
            <Check v-if="step > 2" :size="13" />
            <span v-else>2</span>
          </div>
          <span>Profile</span>
        </div>
        <div class="step-line"></div>
        <div class="step" :class="{ active: step >= 3 }">
          <div class="step-dot"><span>3</span></div>
          <span>Interests</span>
        </div>
      </div>

      <!-- Step 1: Account credentials -->
      <div v-if="step === 1" class="step-content">
        <div class="form-group">
          <label><Mail :size="14" /> Email</label>
          <input v-model="form.email" type="email" placeholder="your@email.com" @keydown.enter="nextStep" />
        </div>
        <div class="form-group">
          <label><User :size="14" /> Username</label>
          <input v-model="form.username" type="text" placeholder="username" @keydown.enter="nextStep" />
        </div>
        <div class="form-group">
          <label><Lock :size="14" /> Password</label>
          <div class="pw-wrap">
            <input v-model="form.password" :type="showPw ? 'text' : 'password'" placeholder="Min 6 characters" @keydown.enter="nextStep" />
            <button type="button" class="pw-toggle" @click="showPw = !showPw">
              <EyeOff v-if="showPw" :size="16" />
              <Eye v-else :size="16" />
            </button>
          </div>
        </div>
        <button class="btn btn-primary btn-lg step-btn" @click="nextStep" :disabled="loading">
          Next <ChevronRight :size="18" />
        </button>
      </div>

      <!-- Step 2: Personal info -->
      <div v-if="step === 2" class="step-content">
        <div class="form-row">
          <div class="form-group">
            <label><UserCircle :size="14" /> First Name</label>
            <input v-model="form.first_name" type="text" placeholder="First Name" />
          </div>
          <div class="form-group">
            <label><UserCircle :size="14" /> Last Name</label>
            <input v-model="form.last_name" type="text" placeholder="Last Name" />
          </div>
        </div>
        <div class="form-group">
          <label><Calendar :size="14" /> Date of Birth</label>
          <input v-model="form.date_of_birth" type="date" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><Users :size="14" /> Gender</label>
            <select v-model="form.gender">
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non-binary">Non-binary</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label><Heart :size="14" /> Looking For</label>
            <select v-model="form.looking_for">
              <option value="any">Any</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><MapPin :size="14" /> City</label>
            <input v-model="form.city" type="text" placeholder="Your city" />
          </div>
          <div class="form-group">
            <label><Globe :size="14" /> Country</label>
            <input v-model="form.country" type="text" placeholder="Country" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><Briefcase :size="14" /> Occupation</label>
            <input v-model="form.occupation" type="text" placeholder="Job / occupation" />
          </div>
          <div class="form-group">
            <label><GraduationCap :size="14" /> Education</label>
            <select v-model="form.education_level">
              <option value="">Select level</option>
              <option value="high_school">High School</option>
              <option value="bachelor">Bachelor's</option>
              <option value="master">Master's</option>
              <option value="phd">PhD</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label><FileText :size="14" /> Bio</label>
          <textarea v-model="form.bio" placeholder="Tell potential matches about yourself…" rows="3"></textarea>
        </div>
        <div class="form-group">
          <label><Camera :size="14" /> Profile Picture</label>
          <div class="pic-upload-area" @click="$refs.picInput.click()">
            <img v-if="previewUrl" :src="previewUrl" class="pic-preview-img" alt="Preview" />
            <div v-else class="pic-placeholder">
              <Upload :size="28" color="#6c63ff" />
              <span>Click to upload photo</span>
              <small>PNG, JPG, WEBP up to 16MB</small>
            </div>
          </div>
          <input ref="picInput" type="file" accept="image/*" @change="onFileChange" style="display:none" />
        </div>
        <div class="step-buttons">
          <button class="btn btn-secondary btn-lg" @click="step = 1">
            <ChevronLeft :size="18" /> Back
          </button>
          <button class="btn btn-primary btn-lg" @click="nextStep" :disabled="loading">
            Next <ChevronRight :size="18" />
          </button>
        </div>
      </div>

      <!-- Step 3: Interests + submit -->
      <div v-if="step === 3" class="step-content">
        <div class="form-group">
          <label><Sparkles :size="14" /> Interests <small>(min 3)</small></label>
          <InterestSelector v-model="form.interests" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><Sliders :size="14" /> Min Age Pref</label>
            <input v-model.number="form.min_age_preference" type="number" min="18" max="99" />
          </div>
          <div class="form-group">
            <label><Sliders :size="14" /> Max Age Pref</label>
            <input v-model.number="form.max_age_preference" type="number" min="18" max="99" />
          </div>
        </div>
        <div class="form-group visibility-toggle">
          <label>
            <input type="checkbox" v-model="form.is_public" />
            <Eye :size="14" /> Make profile public
          </label>
        </div>
        <div class="step-buttons">
          <button class="btn btn-secondary btn-lg" @click="step = 2">
            <ChevronLeft :size="18" /> Back
          </button>
          <button class="btn btn-primary btn-lg" @click="handleRegister" :disabled="loading">
            {{ loading ? 'Creating account…' : 'Create Account' }}
            <UserCheck v-if="!loading" :size="18" />
          </button>
        </div>
      </div>

      <p class="auth-footer">Already have an account? <router-link to="/login">Login here</router-link></p>
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
  HeartHandshake, Heart, Mail, User, Lock, Eye, EyeOff,
  UserCircle, Calendar, Users, MapPin, Globe, Briefcase,
  GraduationCap, FileText, Camera, Upload, ChevronRight,
  ChevronLeft, Check, AlertCircle, Sparkles, Sliders,
  UserCheck
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const step = ref(1)
const showPw = ref(false)
const error = ref('')
const loading = ref(false)
const previewUrl = ref(null)
const selectedFile = ref(null)
const picInput = ref(null)

const form = reactive({
  email: '', username: '', password: '',
  first_name: '', last_name: '', date_of_birth: '',
  gender: '', looking_for: 'any',
  bio: '', city: '', country: '',
  occupation: '', education_level: '',
  interests: [],
  min_age_preference: 18, max_age_preference: 99,
  is_public: true,
})

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

function validateStep1() {
  if (!form.email || !form.username || !form.password) return 'Email, username and password are required'
  if (!form.email.includes('@')) return 'Enter a valid email address'
  if (form.password.length < 6) return 'Password must be at least 6 characters'
  return null
}

function validateStep2() {
  if (!form.first_name || !form.last_name) return 'First and last name are required'
  if (!form.date_of_birth) return 'Date of birth is required'
  if (!form.gender) return 'Please select your gender'
  return null
}

function nextStep() {
  error.value = ''
  if (step.value === 1) {
    const err = validateStep1()
    if (err) { error.value = err; return }
    step.value = 2
  } else if (step.value === 2) {
    const err = validateStep2()
    if (err) { error.value = err; return }
    step.value = 3
  }
}

async function handleRegister() {
  error.value = ''
  if (form.interests.length < 3) { error.value = 'Please add at least 3 interests'; return }
  loading.value = true
  try {
    // Register user account
    await auth.register(form.email, form.username, form.password)

    // Create profile immediately
    const fd = new FormData()
    const profileFields = [
      'first_name','last_name','date_of_birth','gender','looking_for',
      'bio','city','country','occupation','education_level',
      'min_age_preference','max_age_preference'
    ]
    profileFields.forEach(k => { if (form[k] !== undefined) fd.append(k, form[k]) })
    form.interests.forEach(i => fd.append('interests', i))
    fd.append('is_public', form.is_public ? 'true' : 'false')
    if (selectedFile.value) fd.append('profile_picture', selectedFile.value)

    await profilesAPI.create(fd)
    auth.setHasProfile(true)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed. Please try again.'
    // If profile creation failed but account was created, go to profile create
    if (auth.isAuthenticated) router.push('/profile/create')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: flex-start; justify-content: center;
  background: linear-gradient(135deg, #f8f7ff, #e8e6ff); padding: 30px 16px;
}
.auth-card { width: 100%; max-width: 520px; text-align: center; }
.auth-logo {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  font-size: 1.5rem; font-weight: 900; color: var(--primary); margin-bottom: 12px;
}
h2 { font-size: 1.7rem; font-weight: 800; margin-bottom: 4px; }
.auth-sub { color: var(--text-muted); margin-bottom: 20px; font-size: 0.95rem; }
.auth-footer { margin-top: 18px; color: var(--text-muted); font-size: 0.9rem; }

/* Step indicator */
.steps {
  display: flex; align-items: center; justify-content: center;
  gap: 0; margin-bottom: 24px;
}
.step { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.step-dot {
  width: 32px; height: 32px; border-radius: 50%; border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem; font-weight: 700; color: var(--text-muted);
  background: #fff; transition: all 0.2s;
}
.step.active .step-dot { border-color: var(--primary); color: var(--primary); }
.step.done .step-dot { background: var(--primary); border-color: var(--primary); color: #fff; }
.step span:last-child { font-size: 0.75rem; font-weight: 600; color: var(--text-muted); }
.step.active span:last-child { color: var(--primary); }
.step-line { flex: 1; height: 2px; background: var(--border); width: 50px; margin: 0 4px; margin-bottom: 18px; }

.step-content { text-align: left; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-group label { display: flex; align-items: center; gap: 5px; }

/* Password field */
.pw-wrap { position: relative; }
.pw-wrap input { padding-right: 42px; }
.pw-toggle {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--text-muted);
  display: flex; align-items: center;
}

/* Picture upload */
.pic-upload-area {
  border: 2px dashed var(--border); border-radius: var(--radius-sm);
  padding: 20px; cursor: pointer; text-align: center; transition: border-color 0.2s;
  display: flex; align-items: center; justify-content: center; min-height: 120px;
}
.pic-upload-area:hover { border-color: var(--primary); }
.pic-placeholder { display: flex; flex-direction: column; align-items: center; gap: 6px; color: var(--text-muted); }
.pic-placeholder span { font-weight: 600; color: var(--primary); }
.pic-placeholder small { font-size: 0.78rem; }
.pic-preview-img { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 3px solid var(--primary); }

.visibility-toggle label {
  display: flex; align-items: center; gap: 8px; cursor: pointer; font-weight: 600;
}
.visibility-toggle input[type=checkbox] { width: 16px; height: 16px; accent-color: var(--primary); }

.step-btn { width: 100%; justify-content: center; }
.step-buttons { display: flex; gap: 12px; margin-top: 4px; }
.step-buttons .btn { flex: 1; justify-content: center; }

@media (max-width: 500px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>
