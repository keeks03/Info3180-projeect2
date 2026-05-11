<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">

      <!-- Header -->
      <div class="modal-header">
        <h3>{{ tab === 'report' ? ' Report User' : ' Block User' }}</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <!-- Tab switcher -->
      <div class="tab-row">
        <button :class="['tab-btn', { active: tab === 'report' }]" @click="tab='report'">Report</button>
        <button :class="['tab-btn', { active: tab === 'block' }]" @click="tab='block'">Block</button>
      </div>

      <!-- SUCCESS -->
      <div v-if="done" class="result-box" :class="doneType">
        <p>{{ doneMessage }}</p>
        <button class="btn btn-primary" style="margin-top:12px" @click="$emit('close')">Done</button>
      </div>

      <!-- REPORT TAB -->
      <template v-else-if="tab === 'report'">
        <p class="modal-sub">Report <strong>{{ userName }}</strong> to our moderation team.</p>
        <div class="form-group">
          <label>Reason <span class="req">*</span></label>
          <select v-model="reason">
            <option value="">— Select a reason —</option>
            <option value="spam">Spam</option>
            <option value="harassment">Harassment</option>
            <option value="fake_profile">Fake profile</option>
            <option value="inappropriate_content">Inappropriate content</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="form-group">
          <label>Additional details <span class="optional">(optional)</span></label>
          <textarea v-model="detail" maxlength="500" placeholder="Describe what happened…" rows="3" />
          <span class="char-count">{{ detail.length }}/500</span>
        </div>
        <p v-if="error" class="alert alert-error">{{ error }}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="$emit('close')">Cancel</button>
          <button class="btn btn-danger" :disabled="!reason || loading" @click="submitReport">
            {{ loading ? 'Submitting…' : 'Submit Report' }}
          </button>
        </div>
      </template>

      <!-- BLOCK TAB -->
      <template v-else>
        <p class="modal-sub">
          Blocking <strong>{{ userName }}</strong> will:
        </p>
        <ul class="block-list">
          <li>Hide their profile from your browse feed</li>
          <li>Remove any existing match between you</li>
          <li>Prevent them from seeing your profile</li>
          <li>Stop all messages between you</li>
        </ul>
        <p v-if="error" class="alert alert-error">{{ error }}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="$emit('close')">Cancel</button>
          <button class="btn btn-danger" :disabled="loading" @click="submitBlock">
            {{ loading ? 'Blocking…' : `Block ${userName}` }}
          </button>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { moderationAPI } from '@/api/index'

const props = defineProps({
  userId:   { type: Number, required: true },
  userName: { type: String, default: 'this user' },
})
const emit = defineEmits(['close', 'blocked'])

const tab     = ref('report')
const reason  = ref('')
const detail  = ref('')
const loading = ref(false)
const error   = ref('')
const done    = ref(false)
const doneMessage = ref('')
const doneType    = ref('success')

async function submitReport() {
  if (!reason.value) return
  loading.value = true
  error.value   = ''
  try {
    await moderationAPI.report({
      reported_id: props.userId,
      reason:      reason.value,
      detail:      detail.value,
    })
    doneMessage.value = 'Report submitted. Our team will review it shortly.'
    doneType.value    = 'success'
    done.value        = true
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not submit report.'
  } finally {
    loading.value = false
  }
}

async function submitBlock() {
  loading.value = true
  error.value   = ''
  try {
    await moderationAPI.block({ blocked_id: props.userId })
    doneMessage.value = `${props.userName} has been blocked.`
    doneType.value    = 'danger'
    done.value        = true
    emit('blocked', props.userId)
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not block user.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 16px;
}
.modal-box {
  background: var(--card); border-radius: var(--radius);
  width: 100%; max-width: 480px; padding: 28px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25); animation: slideUp 0.2s ease;
}
@keyframes slideUp { from { transform: translateY(20px); opacity:0; } to { transform: translateY(0); opacity:1; } }
.modal-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.modal-header h3 { font-size:1.2rem; font-weight:700; color:var(--text); }
.close-btn { background:none; border:none; font-size:1.2rem; cursor:pointer; color:var(--text-muted); padding:4px; }
.tab-row { display:flex; gap:8px; margin-bottom:20px; border-bottom:2px solid var(--border); padding-bottom:0; }
.tab-btn {
  background:none; border:none; padding:8px 18px; cursor:pointer;
  font-weight:600; color:var(--text-muted); border-bottom:3px solid transparent;
  margin-bottom:-2px; transition:all 0.15s;
}
.tab-btn.active { color:var(--primary); border-bottom-color:var(--primary); }
.modal-sub { color:var(--text-muted); margin-bottom:16px; font-size:0.95rem; }
.block-list { padding-left:20px; margin-bottom:20px; color:var(--text); }
.block-list li { margin-bottom:6px; font-size:0.9rem; }
.modal-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:20px; }
.req { color:var(--danger); }
.optional { color:var(--text-muted); font-size:0.8rem; font-weight:400; }
.char-count { font-size:0.78rem; color:var(--text-muted); float:right; }
.result-box { padding:20px; border-radius:var(--radius-sm); text-align:center; }
.result-box.success { background:#e8f5e9; color:#2e7d32; }
.result-box.danger  { background:#fdecea; color:#c62828; }
</style>