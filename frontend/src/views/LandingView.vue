<script setup lang="ts">
defineEmits<{ enter: [] }>()
</script>

<template>
  <div class="landing-wrapper" @click="$emit('enter')">
    <div class="bg-layer" />
    <div class="film-band top-band" />
    <div class="film-band bottom-band" />
    <div class="paper-photo photo-one"></div>
    <div class="paper-photo photo-two"></div>
    <div class="stamp-mark">GOOD LIGHT</div>
    <div class="center">
      <span class="kodak-tag">Kodak Portra 400</span>
      <h1 class="title">Film Journal</h1>
      <p class="subtitle">记录每一次快门的心跳</p>
      <div class="enter-hint">轻触任意位置进入 U-Life</div>
    </div>
  </div>
</template>

<style scoped>
.landing-wrapper {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  color: var(--journal-ink);
  background: var(--journal-paper);
}

.bg-layer {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 16% 24%, rgb(200 90 84 / 13%), transparent 15rem),
    radial-gradient(circle at 78% 72%, rgb(232 195 108 / 24%), transparent 18rem),
    linear-gradient(90deg, rgb(62 50 40 / 5%) 1px, transparent 1px),
    linear-gradient(rgb(62 50 40 / 3%) 1px, transparent 1px),
    #fdfbf7;
  background-size: auto, auto, 30px 30px, 30px 30px, auto;
}

.bg-layer::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(100deg, transparent 0 47%, rgb(62 50 40 / 5%) 48%, transparent 50%),
    radial-gradient(circle at 9% 84%, rgb(118 79 44 / 10%), transparent 8rem);
  opacity: 0.75;
}

.film-band {
  position: absolute;
  left: -2vw;
  right: -2vw;
  height: 74px;
  background:
    radial-gradient(circle, #fdfbf7 36%, transparent 39%) left 8px top 8px / 32px 18px repeat-x,
    radial-gradient(circle, #fdfbf7 36%, transparent 39%) left 8px bottom 8px / 32px 18px repeat-x,
    linear-gradient(#2b1c13, #100b08);
  box-shadow: 0 16px 32px rgb(62 50 40 / 22%);
  opacity: 0.94;
}

.top-band {
  top: 42px;
  rotate: -2deg;
}

.bottom-band {
  bottom: 48px;
  rotate: 2deg;
}

.paper-photo {
  position: absolute;
  width: min(25vw, 270px);
  aspect-ratio: 4 / 5;
  border: 14px solid #fff7e4;
  border-bottom-width: 48px;
  background:
    linear-gradient(135deg, rgb(232 195 108 / 45%), rgb(200 90 84 / 18%)),
    linear-gradient(160deg, #a7c7c2, #f3c27c 58%, #4f3828);
  box-shadow: 0 20px 44px rgb(62 50 40 / 25%);
}

.photo-one {
  left: 9vw;
  top: 25vh;
  rotate: -8deg;
}

.photo-two {
  right: 8vw;
  bottom: 22vh;
  rotate: 7deg;
}

.stamp-mark {
  position: absolute;
  right: 16vw;
  top: 22vh;
  padding: 12px 16px;
  border: 2px solid var(--journal-stamp);
  border-radius: 999px;
  color: var(--journal-stamp);
  font-weight: 700;
  rotate: -10deg;
}

.center {
  position: relative;
  z-index: 10;
  width: min(640px, calc(100vw - 44px));
  padding: 38px 30px 34px;
  text-align: center;
  background: rgb(255 248 232 / 72%);
  border: 1px solid rgb(62 50 40 / 18%);
  box-shadow: 0 22px 52px rgb(62 50 40 / 18%);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  animation: scaleIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.center::before {
  content: "";
  position: absolute;
  top: -16px;
  left: 50%;
  width: 136px;
  height: 30px;
  background: rgb(232 195 108 / 58%);
  border: 1px solid rgb(62 50 40 / 10%);
  transform: translateX(-50%) rotate(-2deg);
}

.kodak-tag {
  display: inline-block;
  padding: 6px 14px;
  color: var(--journal-ink);
  background: var(--journal-kodak);
  font-size: 13px;
  font-weight: 700;
  rotate: -2deg;
}

.title {
  font-family: "Dancing Script", "Brush Script MT", cursive;
  font-size: clamp(4rem, 10vw, 7.2rem);
  font-weight: 700;
  letter-spacing: 0;
  color: var(--journal-ink);
  text-shadow: 0 6px 0 rgb(232 195 108 / 22%);
  margin: 10px 0 0;
  line-height: 1.1;
}

.subtitle {
  font-size: clamp(1rem, 2.5vw, 1.4rem);
  font-weight: 700;
  color: var(--journal-muted);
  margin-top: 0.8rem;
  letter-spacing: 0.12em;
}

.enter-hint {
  margin-top: 3rem;
  font-size: 0.85rem;
  color: var(--journal-stamp);
  font-weight: 700;
  letter-spacing: 0.1em;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes scaleIn {
  from { transform: scale(0.6); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

@media (max-width: 720px) {
  .film-band {
    height: 54px;
  }

  .paper-photo,
  .stamp-mark {
    display: none;
  }
}
</style>
