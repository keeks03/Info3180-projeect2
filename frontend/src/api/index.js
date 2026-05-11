import axios from 'axios'

const baseURL = (import.meta.env.VITE_API_BASE_URL || '').trim()
  ? `${import.meta.env.VITE_API_BASE_URL.trim()}/api`
  : '/api'

const api = axios.create({
  baseURL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
})

export const authAPI = {
  register: (data)  => api.post('/auth/register', data),
  login:    (data)  => api.post('/auth/login',    data),
  logout:   ()      => api.post('/auth/logout'),
  check:    ()      => api.get('/auth/check'),
  me:       ()      => api.get('/auth/me'),
}

export const profilesAPI = {
  create:    (fd)      => api.post('/profiles',   fd, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getMe:     ()        => api.get('/profiles/me'),
  updateMe:  (fd)      => api.put('/profiles/me', fd, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getById:   (userId)  => api.get(`/profiles/${userId}`),
  browse:    ()        => api.get('/profiles/browse'),
  getPictureUrl: (filename) => {
    if (!filename) return null
    const base = (import.meta.env.VITE_API_BASE_URL || '').trim()
    return base ? `${base}/api/profiles/picture/${filename}` : `/api/profiles/picture/${filename}`
  },
}

export const matchesAPI = {
  action:    (targetUserId, action) => api.post('/matches/action', { target_user_id: targetUserId, action }),
  getMutual: ()                     => api.get('/matches/mutual'),
  getCount:  ()                     => api.get('/matches/count'),
  getStatus: (targetUserId)         => api.get(`/matches/status/${targetUserId}`),
}

export const messagesAPI = {
  send:             (receiverId, content) => api.post('/messages/send', { receiver_id: receiverId, content }),
  getConversation:  (otherUserId)         => api.get(`/messages/conversation/${otherUserId}`),
  getConversations: ()                    => api.get('/messages/conversations'),
  // Send a "call started" notice into chat
  callStarted:      (otherUserId, data)  => api.post(`/messages/conversation/${otherUserId}/call-started`, data),
  // Delete signal messages and post a "call ended" notice (pass { started_at } in body)
  cleanupSignals:   (otherUserId, data)   => api.delete(`/messages/conversation/${otherUserId}/cleanup-signals`, { data }),
}

export const searchAPI = {
  search:       (params) => api.get('/search',           { params }),
  getInterests: ()       => api.get('/search/interests'),
}

export const favouritesAPI = {
  getAll:  ()           => api.get('/favourites'),
  add:     (profileId)  => api.post('/favourites',            { profile_id: profileId }),
  remove:  (profileId)  => api.delete(`/favourites/${profileId}`),
  check:   (profileId)  => api.get(`/favourites/check/${profileId}`),
}

export const moderationAPI = {
  report:      (data)      => api.post('/moderation/report',         data),
  block:       (data)      => api.post('/moderation/block',          data),
  unblock:     (blockedId) => api.delete(`/moderation/block/${blockedId}`),
  checkBlock:  (userId)    => api.get(`/moderation/block/check/${userId}`),
  getMyBlocks: ()          => api.get('/moderation/blocks'),
}

export default api