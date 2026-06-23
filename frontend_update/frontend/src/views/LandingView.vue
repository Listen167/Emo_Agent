<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{ enter: [] }>()
const exiting = ref(false)

const enterApp = () => {
  if (exiting.value) return
  exiting.value = true
  window.setTimeout(() => emit('enter'), 520)
}
</script>

<template>
  <div :class="['landing-wrapper', { exiting }]" @click="enterApp">
    <div class="bg-layer" />
    <div class="scan-beam" />
    <div class="light-leak leak-left" />
    <div class="light-leak leak-right" />
    <div class="film-band top-band">
      <span class="film-track"></span>
    </div>
    <div class="film-band bottom-band">
      <span class="film-track"></span>
    </div>
    <div class="paper-photo photo-one">
      <span>ULIFE</span>
    </div>
    <div class="paper-photo photo-two">
      <span>MEMORY</span>
    </div>
    <div class="stamp-mark">GOOD LIGHT</div>
    <div class="frame-counter">
      <span>FRAME</span>
      <strong>01</strong>
    </div>
    <div class="shutter-aperture" aria-hidden="true">
      <i v-for="index in 6" :key="index"></i>
    </div>
    <div class="center">
      <span class="kodak-tag">Kodak Portra 400</span>
      <h1 class="title" aria-label="Film Journal">
        <span>Film</span>
        <span>Journal</span>
      </h1>
      <p class="subtitle">记录每一次快门的心跳</p>
      <div class="loading-rail">
        <span></span>
      </div>
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

.landing-wrapper::before {
  content: "";
  position: absolute;
  inset: -12%;
  z-index: 2;
  pointer-events: none;
  background:
    repeating-linear-gradient(90deg, transparent 0 26px, rgb(62 50 40 / 4%) 27px 28px),
    repeating-linear-gradient(180deg, transparent 0 5px, rgb(62 50 40 / 3%) 6px 7px);
  mix-blend-mode: multiply;
  animation: grainJitter 5s steps(8) infinite;
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

.scan-beam {
  position: absolute;
  inset: -20% -10%;
  z-index: 1;
  background: linear-gradient(105deg, transparent 0 42%, rgb(255 255 255 / 28%) 47%, transparent 54%);
  opacity: 0.6;
  transform: translateX(-72%);
  animation: scanBeam 4.8s ease-in-out infinite 0.8s;
}

.light-leak {
  position: absolute;
  z-index: 1;
  width: 38vw;
  min-width: 300px;
  aspect-ratio: 1;
  border-radius: 999px;
  filter: blur(34px);
  mix-blend-mode: screen;
  pointer-events: none;
}

.leak-left {
  left: -13vw;
  bottom: 10vh;
  background: radial-gradient(circle, rgb(255 196 94 / 62%), rgb(200 90 84 / 24%) 44%, transparent 72%);
  animation: leakFloatOne 12s ease-in-out infinite;
}

.leak-right {
  right: -16vw;
  top: 10vh;
  background: radial-gradient(circle, rgb(255 248 232 / 54%), rgb(154 122 168 / 20%) 45%, transparent 74%);
  animation: leakFloatTwo 14s ease-in-out infinite;
}

.film-band {
  position: absolute;
  left: -2vw;
  right: -2vw;
  height: 74px;
  z-index: 4;
  overflow: hidden;
  background: linear-gradient(#2b1c13, #100b08);
  box-shadow: 0 16px 32px rgb(62 50 40 / 22%);
  opacity: 0.94;
  transform-origin: center;
  animation: filmSettle 0.9s cubic-bezier(0.2, 0.9, 0.2, 1) both;
}

.film-track {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle, #fdfbf7 36%, transparent 39%) left 8px top 8px / 32px 18px repeat-x,
    radial-gradient(circle, #fdfbf7 36%, transparent 39%) left 8px bottom 8px / 32px 18px repeat-x,
    repeating-linear-gradient(90deg, rgb(255 248 232 / 12%) 0 1px, transparent 1px 56px);
  animation: filmRun 1.7s linear infinite;
  will-change: transform;
}

.top-band .film-track {
  animation-direction: reverse;
}

.top-band {
  top: 42px;
  rotate: -2deg;
}

.bottom-band {
  bottom: 48px;
  rotate: 2deg;
  animation-delay: 0.12s;
}

.paper-photo {
  position: absolute;
  z-index: 3;
  width: min(25vw, 270px);
  aspect-ratio: 4 / 5;
  border: 14px solid #fff7e4;
  border-bottom-width: 48px;
  background-image:
    linear-gradient(135deg, rgb(28 19 14 / 10%), rgb(255 196 94 / 14%)),
    url("/landing-window.jpg"),
    linear-gradient(160deg, #a7c7c2, #f3c27c 58%, #4f3828);
  background-size: cover, cover, cover;
  background-position: center;
  box-shadow: 0 20px 44px rgb(62 50 40 / 25%);
  animation: photoFloat 6s ease-in-out infinite;
}

.paper-photo::after {
  content: "";
  position: absolute;
  inset: 12px 12px 56px;
  background:
    linear-gradient(115deg, transparent 0 40%, rgb(255 255 255 / 34%) 48%, transparent 56%),
    radial-gradient(circle at 24% 20%, rgb(255 255 255 / 28%), transparent 24%);
  mix-blend-mode: screen;
  animation: photoGlint 4.5s ease-in-out infinite;
}

.paper-photo span {
  position: absolute;
  left: 16px;
  bottom: 16px;
  color: rgb(62 50 40 / 62%);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.photo-one {
  left: 9vw;
  top: 25vh;
  rotate: -8deg;
  animation-delay: 0.2s;
}

.photo-two {
  right: 8vw;
  bottom: 22vh;
  rotate: 7deg;
  animation-delay: 0.7s;
}

.stamp-mark {
  position: absolute;
  z-index: 5;
  right: 16vw;
  top: 22vh;
  padding: 12px 16px;
  border: 2px solid var(--journal-stamp);
  border-radius: 999px;
  color: var(--journal-stamp);
  font-weight: 700;
  rotate: -10deg;
  animation: stampIn 0.8s cubic-bezier(0.18, 1.5, 0.4, 1) both 0.45s;
}

.frame-counter {
  position: absolute;
  left: 15vw;
  bottom: 17vh;
  z-index: 5;
  width: 94px;
  height: 94px;
  display: grid;
  place-items: center;
  border: 2px solid rgb(62 50 40 / 30%);
  border-radius: 999px;
  color: var(--journal-ink);
  background: rgb(255 248 232 / 64%);
  box-shadow: 0 14px 28px rgb(62 50 40 / 14%);
  animation: counterTick 2.8s steps(2) infinite;
}

.frame-counter span,
.frame-counter strong {
  display: block;
  text-align: center;
}

.frame-counter span {
  align-self: end;
  color: var(--journal-stamp);
  font-size: 10px;
  font-weight: 700;
}

.frame-counter strong {
  align-self: start;
  font-size: 30px;
  line-height: 1;
}

.shutter-aperture {
  position: absolute;
  inset: 0;
  z-index: 30;
  pointer-events: none;
  opacity: 0;
}

.shutter-aperture i {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 160vmax;
  height: 160vmax;
  background: rgb(28 19 14 / 92%);
  transform-origin: 0 0;
  clip-path: polygon(0 0, 50% 0, 0 50%);
}

.shutter-aperture i:nth-child(1) { rotate: 0deg; }
.shutter-aperture i:nth-child(2) { rotate: 60deg; }
.shutter-aperture i:nth-child(3) { rotate: 120deg; }
.shutter-aperture i:nth-child(4) { rotate: 180deg; }
.shutter-aperture i:nth-child(5) { rotate: 240deg; }
.shutter-aperture i:nth-child(6) { rotate: 300deg; }

.landing-wrapper.exiting .shutter-aperture {
  opacity: 1;
}

.landing-wrapper.exiting .shutter-aperture i {
  animation: apertureClose 0.52s cubic-bezier(0.2, 0.8, 0.2, 1) both;
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
  animation: developCard 1s cubic-bezier(0.2, 0.9, 0.2, 1) both 0.2s;
  opacity: 1;
  filter: none;
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
  animation: tagSnap 0.62s cubic-bezier(0.18, 1.5, 0.4, 1) both 0.8s;
}

.title {
  font-family: "Dancing Script", "Brush Script MT", cursive;
  font-size: clamp(4rem, 10vw, 7.2rem);
  font-weight: 700;
  letter-spacing: 0;
  color: var(--journal-ink);
  text-shadow: 0 6px 0 rgb(232 195 108 / 22%);
  display: flex;
  justify-content: center;
  gap: 0.22em;
  margin: 10px 0 0;
  line-height: 1.1;
}

.title span {
  display: inline-block;
  opacity: 1;
  filter: blur(0) sepia(0);
  transform: translateY(0);
  animation: titleDevelop 0.9s ease forwards;
}

.title span:nth-child(2) {
  animation-delay: 0.18s;
}

.subtitle {
  font-size: clamp(1rem, 2.5vw, 1.4rem);
  font-weight: 700;
  color: var(--journal-muted);
  margin-top: 0.8rem;
  letter-spacing: 0.12em;
  opacity: 1;
  animation: fadeRise 0.8s ease both 0.92s;
}

.loading-rail {
  position: relative;
  overflow: hidden;
  width: min(320px, 72%);
  height: 8px;
  margin: 24px auto 0;
  border: 1px solid rgb(62 50 40 / 16%);
  border-radius: 999px;
  background: rgb(253 251 247 / 72%);
}

.loading-rail span {
  position: absolute;
  inset: 1px auto 1px 1px;
  width: 38%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--journal-stamp), var(--journal-kodak));
  animation: loadingRail 2.4s ease-in-out infinite;
}

.enter-hint {
  margin-top: 3rem;
  font-size: 0.85rem;
  color: var(--journal-stamp);
  font-weight: 700;
  letter-spacing: 0.1em;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes grainJitter {
  0% { transform: translate(0, 0); }
  20% { transform: translate(-1.4%, 0.8%); }
  40% { transform: translate(1%, -1.2%); }
  60% { transform: translate(1.3%, 0.8%); }
  80% { transform: translate(-0.8%, -0.7%); }
  100% { transform: translate(0, 0); }
}

@keyframes scanBeam {
  0%,
  20% { transform: translateX(-72%); opacity: 0; }
  34% { opacity: 0.68; }
  72%,
  100% { transform: translateX(72%); opacity: 0; }
}

@keyframes leakFloatOne {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); opacity: 0.34; }
  50% { transform: translate3d(8vw, -5vh, 0) scale(1.12); opacity: 0.52; }
}

@keyframes leakFloatTwo {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); opacity: 0.28; }
  50% { transform: translate3d(-7vw, 6vh, 0) scale(1.08); opacity: 0.46; }
}

@keyframes filmSettle {
  from { transform: translateY(-28px); opacity: 0; }
  to { transform: translateY(0); opacity: 0.94; }
}

@keyframes filmRun {
  from { transform: translateX(0); }
  to { transform: translateX(64px); }
}

@keyframes photoFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(1.2deg); }
}

@keyframes photoGlint {
  0%, 35% { transform: translateX(-90%); opacity: 0; }
  50% { opacity: 0.7; }
  75%, 100% { transform: translateX(90%); opacity: 0; }
}

@keyframes stampIn {
  0% { opacity: 0; transform: translateY(-22px) scale(1.55) rotate(8deg); filter: blur(5px); }
  70% { opacity: 1; transform: translateY(3px) scale(0.92) rotate(0); filter: blur(0); }
  100% { opacity: 1; transform: translateY(0) scale(1) rotate(0); }
}

@keyframes counterTick {
  0%, 100% { transform: rotate(-2deg); }
  50% { transform: rotate(2deg); }
}

@keyframes apertureClose {
  from { transform: scale(0.04) rotate(-18deg); opacity: 0; }
  to { transform: scale(1) rotate(0deg); opacity: 1; }
}

@keyframes developCard {
  from { transform: translateY(18px) scale(0.96); opacity: 0.9; filter: blur(2px) sepia(0.12); }
  to { transform: translateY(0) scale(1); opacity: 1; filter: blur(0) sepia(0); }
}

@keyframes tagSnap {
  from { transform: translateY(-10px) rotate(-4deg); opacity: 0.72; }
  to { transform: translateY(0) rotate(0); opacity: 1; }
}

@keyframes titleDevelop {
  from {
    opacity: 0.28;
    filter: blur(6px) sepia(0.28);
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    filter: blur(0) sepia(0);
    transform: translateY(0);
  }
}

@keyframes fadeRise {
  from { opacity: 0.62; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes loadingRail {
  0% { transform: translateX(-102%); }
  48% { transform: translateX(86%); }
  100% { transform: translateX(186%); }
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
  .stamp-mark,
  .frame-counter {
    display: none;
  }

  .title {
    display: block;
  }
}

@media (prefers-reduced-motion: reduce) {
  .landing-wrapper::before,
  .scan-beam,
  .light-leak,
  .film-band,
  .film-track,
  .paper-photo,
  .paper-photo::after,
  .stamp-mark,
  .frame-counter,
  .center,
  .kodak-tag,
  .title span,
  .subtitle,
  .loading-rail span,
  .enter-hint,
  .landing-wrapper.exiting .shutter-aperture i {
    animation: none !important;
  }

  .title span {
    opacity: 1;
    filter: none;
    transform: none;
  }
}
</style>
