<template>
  <div class="page conv-page">
    <div class="conv-header">
      <router-link to="/messages" class="btn btn-secondary btn-sm"><ChevronLeft :size="16" /> Back</router-link>
      <div v-if="partnerProfile" class="conv-partner">
        <img v-if="partnerPic" :src="partnerPic" class="partner-avatar" />
        <div v-else class="partner-placeholder"><UserCircle :size="34" color="#fff" /></div>
        <div>
          <strong>{{ partnerProfile.first_name }} {{ partnerProfile.last_name }}</strong>
          <div class="partner-loc" v-if="partnerProfile.city"><MapPin :size="11" /> {{ partnerProfile.city }}</div>
        </div>
      </div>
      <div class="conv-actions">
        <router-link v-if="partnerProfile" :to="`/call/${partnerId}`" class="btn btn-primary btn-sm">
          <Video :size="14" /> Video Call
        </router-link>
        <router-link v-if="partnerProfile" :to="`/profile/${partnerId}`" class="btn btn-outline btn-sm">
          <Eye :size="14" /> Profile
        </router-link>
      </div>
    </div>

    <div class="messages-box" ref="msgBox">
      <div v-if="loading" class="spinner"></div>
      <div v-else-if="visibleMessages.length === 0" class="empty-msg">
        <Hand :size="32" color="#ccc" /><p>Say hello! Start the conversation.</p>
      </div>
      <template v-else>
        <template v-for="msg in visibleMessages" :key="msg.id">

          <!-- Call STARTED notice -->
          <div v-if="isCallStarted(msg)" class="call-notice call-notice--started">
            <div class="call-notice-header">
              <span class="call-notice-icon">📹</span>
              <span class="call-notice-title">Video call started</span>
            </div>
            <div v-for="(line, i) in callNoticeBodyLines(msg)" :key="i" class="call-notice-body">
              {{ line }}
            </div>
          </div>

          <!-- Call ENDED notice -->
          <div v-else-if="isCallEnded(msg)" class="call-notice call-notice--ended">
            <div class="call-notice-header">
              <span class="call-notice-icon">📵</span>
              <span class="call-notice-title">Video call ended</span>
            </div>
            <div v-for="(line, i) in callNoticeBodyLines(msg)" :key="i" class="call-notice-body">
              {{ line }}
            </div>
          </div>

          <!-- Regular chat bubble -->
          <div
            v-else
            class="msg-bubble"
            :class="msg.sender_id === currentUserId ? 'msg-mine' : 'msg-theirs'"
          >
            <div class="msg-content">{{ msg.content }}</div>
            <div class="msg-time"><Clock :size="10" /> {{ formatTime(msg.created_at) }}</div>
          </div>

        </template>
      </template>
    </div>

    <div class="msg-input-bar">
      <input
        v-model="newMessage"
        type="text"
        placeholder="Type a message…"
        @keydown.enter="sendMessage"
        :disabled="sending"
      />
      <button class="btn btn-primary" @click="sendMessage" :disabled="!newMessage.trim() || sending">
        <Send :size="16" /> {{ sending ? '…' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { messagesAPI, profilesAPI } from '@/api'
import { ChevronLeft, UserCircle, MapPin, Eye, Hand, Clock, Send, Video } from 'lucide-vue-next'

const route          = useRoute()
const auth           = useAuthStore()
const partnerId      = Number(route.params.userId)
const currentUserId  = computed(() => auth.user?.id)
const loading        = ref(true)
const sending        = ref(false)
const messages       = ref([])
const newMessage     = ref('')
const partnerProfile = ref(null)
const partnerPic     = ref(null)
const msgBox         = ref(null)
let   pollInterval   = null

const SIG = '__WEBRTC__'

// Message classification 
const visibleMessages = computed(() =>
  messages.value.filter(m => !m.content?.startsWith(SIG))
)

function isCallStarted(msg) {
  return msg.content?.startsWith('📹 Video call started')
}

function isCallEnded(msg) {
  return msg.content?.startsWith('📹 Video call ended')
}

// Return lines after the first (which is used as the title)
function callNoticeBodyLines(msg) {
  return msg.content
    .split('\n')
    .slice(1)                    // skip first line already shown as title
    .filter(l => l.trim())
}

// Data loading 
onMounted(async () => {
  try {
    const [msgs, profile] = await Promise.all([
      messagesAPI.getConversation(partnerId),
      profilesAPI.getById(partnerId)
    ])
    messages.value       = msgs.data.messages
    partnerProfile.value = profile.data.profile
    partnerPic.value     = profilesAPI.getPictureUrl(partnerProfile.value?.profile_picture)
  } catch {} finally {
    loading.value = false
    scrollToBottom()
  }

  pollInterval = setInterval(async () => {
    try {
      const res = await messagesAPI.getConversation(partnerId)
      if (res.data.messages.length !== messages.value.length) {
        messages.value = res.data.messages
        scrollToBottom()
      }
    } catch {}
  }, 3000)
})

onUnmounted(() => clearInterval(pollInterval))

async function sendMessage() {
  const content = newMessage.value.trim()
  if (!content || sending.value) return
  sending.value = true
  try {
    const res = await messagesAPI.send(partnerId, content)
    messages.value.push(res.data.data)
    newMessage.value = ''
    scrollToBottom()
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to send')
  } finally {
    sending.value = false
  }
}

async function scrollToBottom() {
  await nextTick()
  if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZoneName: 'short',
  })
}
</script>

<style scoped>
.conv-page { display:flex; flex-direction:column; height:calc(100vh - 62px); padding-bottom:0; }
.conv-header {
  display:flex; align-items:center; gap:14px; padding:12px 16px;
  background:var(--card); border-radius:var(--radius); margin-bottom:12px;
  box-shadow:var(--shadow); flex-wrap:wrap; flex-shrink:0;
}
.conv-partner { display:flex; align-items:center; gap:10px; flex:1; }
.conv-actions { display:flex; gap:8px; align-items:center; }
.partner-avatar { width:44px; height:44px; border-radius:50%; object-fit:cover; border:2px solid var(--primary); }
.partner-placeholder {
  width:44px; height:44px; border-radius:50%;
  background:linear-gradient(135deg,var(--primary),var(--secondary));
  display:flex; align-items:center; justify-content:center;
}
.partner-loc { font-size:0.78rem; color:var(--text-muted); display:flex; align-items:center; gap:3px; margin-top:2px; }

.messages-box {
  background:var(--card); border-radius:var(--radius); box-shadow:var(--shadow);
  padding:16px; flex:1; overflow-y:auto;
  display:flex; flex-direction:column; gap:10px; margin-bottom:12px;
}
.empty-msg { display:flex; flex-direction:column; align-items:center; gap:10px; color:var(--text-muted); margin:auto; text-align:center; }

/* ── Call notices ─────────────────────────────────────────────────────── */
.call-notice {
  align-self: center;
  max-width: 85%;
  border-radius: 14px;
  padding: 10px 16px;
  font-size: 0.83rem;
  text-align: center;
  border: 1.5px solid;
}

/* green tint */
.call-notice--started {
  background: #e8f5e9;
  border-color: #66bb6a;
  color: #1b5e20;
}
:global([data-theme="dark"]) .call-notice--started {
  background: #0d2b0f;
  border-color: #388e3c;
  color: #a5d6a7;
}

/* grey-blue */
.call-notice--ended {
  background: #ede7f6;
  border-color: #9575cd;
  color: #311b92;
}
:global([data-theme="dark"]) .call-notice--ended {
  background: #1a1226;
  border-color: #7e57c2;
  color: #ce93d8;
}

.call-notice-header {
  display: flex; align-items: center; justify-content: center;
  gap: 6px; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px;
}
.call-notice-icon  { font-size: 1rem; }
.call-notice-title { }
.call-notice-body  { font-size: 0.8rem; opacity: 0.85; line-height: 1.6; }

/* Chat bubbles */
.msg-bubble { display:flex; flex-direction:column; max-width:72%; }
.msg-mine   { align-self:flex-end;   align-items:flex-end; }
.msg-theirs { align-self:flex-start; align-items:flex-start; }
.msg-content { padding:10px 16px; border-radius:20px; font-size:0.95rem; line-height:1.5; word-break:break-word; }
.msg-mine   .msg-content { background:var(--primary); color:#fff; border-bottom-right-radius:4px; }
.msg-theirs .msg-content { background:var(--border);  color:var(--text); border-bottom-left-radius:4px; }
.msg-time { font-size:0.72rem; color:var(--text-muted); margin-top:3px; display:flex; align-items:center; gap:3px; }

/*  Input bar */
.msg-input-bar {
  display:flex; gap:10px; background:var(--card); border-radius:var(--radius);
  padding:12px; box-shadow:var(--shadow); flex-shrink:0;
}
.msg-input-bar input {
  flex:1; padding:10px 16px; border:2px solid var(--border); border-radius:50px;
  font-size:0.95rem; outline:none; background:var(--card); color:var(--text);
}
.msg-input-bar input:focus { border-color:var(--primary); }
</style>