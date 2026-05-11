<template>
  <div class="call-page">

    <div class="call-topbar">
      <div class="call-peer-info">
        <div class="call-avatar-sm">{{ peerInitial }}</div>
        <div>
          <div class="call-peer-name">{{ peerName }}</div>
          <div class="call-status">{{ statusLabel }}</div>
        </div>
      </div>
      <router-link :to="`/messages/${userId}`" class="btn btn-secondary btn-sm">← Back to chat</router-link>
    </div>

    <div class="video-stage">
      <video ref="remoteVideo" class="remote-video" autoplay playsinline />

      <div v-if="state !== 'connected'" class="call-overlay">
        <div class="call-avatar-lg">{{ peerInitial }}</div>
        <p class="overlay-label">{{ statusLabel }}</p>
        <div v-if="state === 'calling' || state === 'ringing'" class="dots">
          <span /><span /><span />
        </div>
      </div>

      <video ref="localVideo" class="local-video" autoplay playsinline muted />
    </div>

    <div class="call-controls">
      <button class="ctrl-btn" :class="{ muted: !micOn }" @click="toggleMic" title="Mute">
        {{ micOn ? '🎙️' : '🔇' }}
      </button>
      <button class="ctrl-btn" :class="{ muted: !camOn }" @click="toggleCam" title="Camera">
        {{ camOn ? '📹' : '📷' }}
      </button>
      <button class="ctrl-btn end-btn" @click="endCall" title="End call">📵</button>
    </div>

    <div v-if="errorMsg" class="call-error">{{ errorMsg }}</div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { messagesAPI, profilesAPI } from '@/api'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const userId = Number(route.params.userId)

const localVideo  = ref(null)
const remoteVideo = ref(null)
const state       = ref('init')
const micOn       = ref(true)
const camOn       = ref(true)
const peerName    = ref('...')
const peerInitial = ref('?')
const errorMsg    = ref('')

let startedAtLocal = null

const statusLabel = computed(() => ({
  'init':          'Initialising…',
  'getting-media': 'Starting camera…',
  'calling':       'Calling…',
  'ringing':       'Incoming call…',
  'connected':     'Connected',
  'ended':         'Call ended',
}[state.value] ?? ''))

let pc          = null
let localStream = null
let pollTimer   = null
let lastMsgId   = 0

const ICE = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
]
const SIG = '__WEBRTC__'

function localTimeStr(date = new Date()) {
  return date.toLocaleString(undefined, {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true,
    timeZoneName: 'short',
  })
}

async function sendSignal(payload) {
  await messagesAPI.send(userId, SIG + JSON.stringify(payload))
}

function parseSignal(content) {
  if (!content?.startsWith(SIG)) return null
  try { return JSON.parse(content.slice(SIG.length)) } catch { return null }
}

async function pollSignals() {
  try {
    const res  = await messagesAPI.getConversation(userId)
    const msgs = res.data.messages || []
    for (const m of msgs) {
      if (m.id <= lastMsgId) continue
      lastMsgId = m.id
      if (m.sender_id === auth.user?.id) continue
      const sig = parseSignal(m.content)
      if (sig) await handleSignal(sig)
    }
  } catch { /* silent */ }
}

async function handleSignal(sig) {
  if (!pc) return
  try {
    if (sig.type === 'offer') {
      await pc.setRemoteDescription(new RTCSessionDescription(sig))
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)
      await sendSignal({ type: 'answer', sdp: answer.sdp })
      await markConnected()
    } else if (sig.type === 'answer') {
      await pc.setRemoteDescription(new RTCSessionDescription(sig))
      await markConnected()
    } else if (sig.type === 'ice') {
      await pc.addIceCandidate(new RTCIceCandidate(sig.candidate))
    } else if (sig.type === 'end') {
      state.value = 'ended'
      await cleanupSignalMessages()
      cleanup()
    }
  } catch { /* ignore stale ICE */ }
}

async function markConnected() {
  if (state.value === 'connected') return
  state.value    = 'connected'
  startedAtLocal = localTimeStr()
  try {
    await messagesAPI.callStarted(userId, { started_at_local: startedAtLocal })
  } catch { /* silent */ }
}

function buildPC() {
  pc = new RTCPeerConnection({ iceServers: ICE })
  pc.onicecandidate = (e) => {
    if (e.candidate) sendSignal({ type: 'ice', candidate: e.candidate.toJSON() })
  }
  pc.ontrack = (e) => {
    if (remoteVideo.value && e.streams[0]) {
      remoteVideo.value.srcObject = e.streams[0]
      markConnected()
    }
  }
  pc.onconnectionstatechange = () => {
    if (['disconnected', 'failed', 'closed'].includes(pc.connectionState)) {
      state.value = 'ended'
    }
  }
  if (localStream) localStream.getTracks().forEach(t => pc.addTrack(t, localStream))
}

async function startCall() {
  state.value = 'getting-media'
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (localVideo.value) localVideo.value.srcObject = localStream
  } catch {
    errorMsg.value = 'Could not access camera/microphone. Please allow permission and try again.'
    state.value = 'ended'
    return
  }
  buildPC()
  state.value = 'calling'
  const offer = await pc.createOffer()
  await pc.setLocalDescription(offer)
  await sendSignal({ type: 'offer', sdp: offer.sdp })
  pollTimer = setInterval(pollSignals, 2000)
}

function toggleMic() {
  micOn.value = !micOn.value
  localStream?.getAudioTracks().forEach(t => { t.enabled = micOn.value })
}

function toggleCam() {
  camOn.value = !camOn.value
  localStream?.getVideoTracks().forEach(t => { t.enabled = camOn.value })
}

async function cleanupSignalMessages() {
  try {
    await messagesAPI.cleanupSignals(userId, {
      started_at_local: startedAtLocal,
      ended_at_local:   localTimeStr(),
    })
  } catch { /* silent */ }
}

async function endCall() {
  await sendSignal({ type: 'end' }).catch(() => {})
  state.value = 'ended'
  await cleanupSignalMessages()
  cleanup()
  setTimeout(() => router.push(`/messages/${userId}`), 1000)
}

function cleanup() {
  clearInterval(pollTimer)
  localStream?.getTracks().forEach(t => t.stop())
  pc?.close()
  pc = null
}

async function loadPeer() {
  try {
    const res = await profilesAPI.getById(userId)
    const p   = res.data.profile || res.data
    peerName.value    = `${p.first_name} ${p.last_name}`
    peerInitial.value = p.first_name?.[0]?.toUpperCase() || '?'
  } catch { /* silent */ }
}

onMounted(async () => {
  await loadPeer()
  await startCall()
})

onUnmounted(cleanup)
</script>

<style scoped>
.call-page {
  display: flex; flex-direction: column; height: 100vh;
  background: #0f0e17; color: #fff; overflow: hidden;
}
.call-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 20px; background: rgba(255,255,255,0.05);
  border-bottom: 1px solid rgba(255,255,255,0.1); flex-shrink: 0;
}
.call-peer-info { display: flex; align-items: center; gap: 12px; }
.call-avatar-sm {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; font-weight: 700;
}
.call-peer-name { font-weight: 700; }
.call-status    { font-size: 0.8rem; color: #a89eff; }
.video-stage {
  flex: 1; position: relative; background: #0a0914;
  display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.remote-video { width: 100%; height: 100%; object-fit: cover; }
.local-video {
  position: absolute; bottom: 90px; right: 16px;
  width: 140px; height: 100px; border-radius: 12px; object-fit: cover;
  border: 2px solid rgba(255,255,255,0.3); background: #111; z-index: 5;
}
.call-overlay {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 16px; background: #0a0914;
}
.call-avatar-lg {
  width: 100px; height: 100px; border-radius: 50%;
  background: var(--primary); font-size: 2.5rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 0 16px rgba(108,99,255,0.15);
}
.overlay-label { font-size: 1.1rem; color: #a89eff; }
.dots { display: flex; gap: 8px; }
.dots span {
  width: 10px; height: 10px; border-radius: 50%; background: var(--primary);
  animation: pulse 1.2s ease-in-out infinite;
}
.dots span:nth-child(2) { animation-delay: 0.2s; }
.dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse { 0%,80%,100%{transform:scale(0.6);opacity:.5} 40%{transform:scale(1);opacity:1} }
.call-controls {
  display: flex; align-items: center; justify-content: center; gap: 20px;
  padding: 16px; background: rgba(255,255,255,0.05);
  border-top: 1px solid rgba(255,255,255,0.08); flex-shrink: 0;
}
.ctrl-btn {
  width: 56px; height: 56px; border-radius: 50%; border: none; font-size: 1.4rem;
  cursor: pointer; background: rgba(255,255,255,0.12);
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.ctrl-btn.muted { background: rgba(255,255,255,0.28); }
.ctrl-btn:hover { transform: scale(1.08); }
.end-btn { width: 64px; height: 64px; background: #e53935; font-size: 1.6rem; }
.end-btn:hover { background: #b71c1c; }
.call-error {
  position: absolute; bottom: 90px; left: 50%; transform: translateX(-50%);
  background: rgba(229,57,53,0.92); color: #fff; padding: 12px 24px;
  border-radius: 50px; font-size: 0.9rem; max-width: 90%; text-align: center;
}
</style>