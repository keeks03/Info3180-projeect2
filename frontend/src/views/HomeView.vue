<template>
  <div class="home">
    <div class="home-hero">
      <div class="hero-content">
        <div class="hero-logo"><HeartHandshake :size="64" color="#6c63ff" /></div>
        <h1>DriftDater</h1>
        <p class="hero-sub">Find your perfect match. Connect with people who share your passions.</p>
        <div class="hero-cta">
          <router-link to="/register" class="btn btn-primary btn-lg"><UserPlus :size="18" /> Get Started Free</router-link>
          <router-link to="/login" class="btn btn-outline btn-lg"><LogIn :size="18" /> Sign In</router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-card fc1">
          <div class="fc-avatar"><UserCircle :size="40" color="#6c63ff" /></div>
          <div><strong class="fc-name">Alice, 25</strong><br><small class="fc-match">98% match</small></div>
        </div>
        <div class="floating-card fc2">
          <div class="fc-avatar"><UserCircle :size="40" color="#ff6584" /></div>
          <div><strong class="fc-name">Bob, 27</strong><br><small class="fc-match">91% match</small></div>
        </div>
        <div class="floating-card fc3">
          <div class="fc-avatar"><UserCircle :size="40" color="#43b89c" /></div>
          <div><strong class="fc-name">Emma, 23</strong><br><small class="fc-match">85% match</small></div>
        </div>
      </div>
    </div>

    <div class="home-features">
      <div class="feature-card">
        <div class="feat-icon"><Target :size="36" color="#6c63ff" /></div>
        <h3>Smart Matching</h3>
        <p>Our algorithm finds compatible partners based on interests, location and preferences.</p>
      </div>
      <div class="feature-card">
        <div class="feat-icon"><MessageCircle :size="36" color="#6c63ff" /></div>
        <h3>Private Messaging</h3>
        <p>Chat only with your mutual matches meaning no unwanted messages EVER.</p>
      </div>
      <div class="feature-card">
        <div class="feat-icon"><ShieldCheck :size="36" color="#6c63ff" /></div>
        <h3>Safe & Secure</h3>
        <p>Your data is encrypted and your profile visibility is always in your control.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { HeartHandshake, UserPlus, LogIn, UserCircle, Target, MessageCircle, ShieldCheck } from 'lucide-vue-next'
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f7ff 0%, #e8e6ff 100%);
}
:global([data-theme="dark"]) .home {
  background: linear-gradient(135deg, #0f0e17 0%, #1a1826 100%);
}
.home-hero {
  max-width: 1100px; margin: 0 auto; padding: 80px 20px 60px;
  display: flex; align-items: center; gap: 60px; flex-wrap: wrap;
}
.hero-content { flex: 1; min-width: 280px; }
.hero-logo { margin-bottom: 16px; }
h1 { font-size: 3.5rem; font-weight: 900; color: var(--primary); line-height: 1; margin-bottom: 16px; }
.hero-sub { font-size: 1.2rem; color: var(--text-muted); margin-bottom: 32px; max-width: 400px; line-height: 1.6; }
.hero-cta { display: flex; gap: 14px; flex-wrap: wrap; }
.hero-visual { flex: 1; min-width: 260px; position: relative; height: 300px; }
.floating-card {
  position: absolute;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px; padding: 14px 18px;
  box-shadow: var(--shadow); display: flex; align-items: center; gap: 12px;
  animation: float 3s ease-in-out infinite;
}
.fc1 { top: 0;     left: 0;    animation-delay: 0s; }
.fc2 { top: 100px; right: 0;   animation-delay: 1s; }
.fc3 { bottom: 0;  left: 60px; animation-delay: 2s; }
.fc-name  { color: var(--text); font-weight: 700; }
.fc-match { color: var(--text-muted); font-size: 0.85rem; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
.home-features {
  max-width: 1000px; margin: 0 auto; padding: 40px 20px 80px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px;
}
.feature-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius); padding: 28px;
  box-shadow: var(--shadow); text-align: center;
}
.feat-icon { margin-bottom: 14px; display: flex; justify-content: center; }
h3 { font-size: 1.2rem; font-weight: 700; color: var(--primary); margin-bottom: 8px; }
p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; }
</style>