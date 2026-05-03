<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-logo">
        <HeartHandshake :size="32" color="#6c63ff" />
        <span>DriftDater</span>
      </div>
      <h2>Welcome Back</h2>
      <p class="auth-sub">Sign in to find your match</p>

      <div v-if="error" class="alert alert-error"><AlertCircle :size="16" /> {{ error }}</div>

      <div class="form-group">
        <label><Mail :size="14" /> Email</label>
        <input v-model="email" type="email" placeholder="your@email.com" @keydown.enter="handleLogin" />
      </div>
      <div class="form-group">
        <label><Lock :size="14" /> Password</label>
        <div class="pw-wrap">
          <input v-model="password" :type="showPw ? 'text' : 'password'" placeholder="Password" @keydown.enter="handleLogin" />
          <button type="button" class="pw-toggle" @click="showPw = !showPw">
            <EyeOff v-if="showPw" :size="16" /><Eye v-else :size="16" />
          </button>
        </div>
      </div>

      <button class="btn btn-primary btn-lg" style="width:100%" @click="handleLogin" :disabled="loading">
        <LogIn v-if="!loading" :size="18" />
        {{ loading ? 'Signing in…' : 'Sign In' }}
      </button>

      <p class="auth-footer">Don't have an account? <router-link to="/register">Sign up here</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { HeartHandshake, Mail, Lock, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showPw = ref(false)

async function handleLogin() {
  error.value = ''
  if (!email.value || !password.value) { error.value = 'Please fill all fields'; return }
  loading.value = true
  try {
    const res = await auth.login(email.value, password.value)
    router.push(res.has_profile ? '/dashboard' : '/profile/create')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed'
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height:100vh; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#f8f7ff,#e8e6ff); padding:20px; }
.auth-card { width:100%; max-width:440px; text-align:center; }
.auth-logo { display:flex; align-items:center; justify-content:center; gap:8px; font-size:1.5rem; font-weight:900; color:var(--primary); margin-bottom:16px; }
h2 { font-size:1.8rem; font-weight:800; margin-bottom:6px; }
.auth-sub { color:var(--text-muted); margin-bottom:24px; }
.auth-footer { margin-top:20px; color:var(--text-muted); font-size:0.9rem; }
.form-group { text-align:left; }
.form-group label { display:flex; align-items:center; gap:5px; }
.pw-wrap { position:relative; }
.pw-wrap input { padding-right:42px; }
.pw-toggle { position:absolute; right:12px; top:50%; transform:translateY(-50%); background:none; border:none; cursor:pointer; color:var(--text-muted); display:flex; align-items:center; }
</style>
