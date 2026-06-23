<template>
  <div class="ambient-film-layer" aria-hidden="true">
    <span class="light-leak leak-one"></span>
    <span class="light-leak leak-two"></span>
    <span class="liquid-ribbon ribbon-one"></span>
    <span class="liquid-ribbon ribbon-two"></span>
    <span class="prism-sheet sheet-one"></span>
    <span class="prism-sheet sheet-two"></span>
    <span class="liquid-refraction refraction-one"></span>
    <span class="liquid-refraction refraction-two"></span>
    <span class="glass-caustic caustic-one"></span>
    <span class="glass-caustic caustic-two"></span>
    <span class="glass-caustic caustic-three"></span>
    <span class="film-scratch scratch-one"></span>
    <span class="film-scratch scratch-two"></span>
  </div>
</template>

<style scoped>
.ambient-film-layer {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  opacity: 0.78;
}

.ambient-film-layer::before,
.ambient-film-layer::after {
  content: "";
  position: absolute;
  inset: -20%;
}

.ambient-film-layer::before {
  background:
    repeating-radial-gradient(circle at 18% 24%, rgb(62 50 40 / 8%) 0 1px, transparent 1px 6px),
    repeating-radial-gradient(circle at 78% 68%, rgb(62 50 40 / 5%) 0 1px, transparent 1px 7px);
  mix-blend-mode: multiply;
  animation: filmGrainDrift 8s steps(8) infinite;
}

.ambient-film-layer::after {
  background:
    linear-gradient(90deg, transparent 0 48%, rgb(255 255 255 / 7%) 49%, transparent 50%),
    linear-gradient(180deg, transparent 0 82%, rgb(62 50 40 / 5%) 83%, transparent 85%);
  opacity: 0.45;
  animation: filmGateWeave 9s ease-in-out infinite;
}

.light-leak {
  position: absolute;
  width: 42vw;
  min-width: 320px;
  aspect-ratio: 1;
  border-radius: 999px;
  filter: blur(36px);
  mix-blend-mode: screen;
  opacity: 0.38;
}

.liquid-ribbon {
  position: absolute;
  height: 26vh;
  min-height: 180px;
  border-radius: 999px;
  filter: blur(28px);
  mix-blend-mode: screen;
  opacity: 0.2;
}

.ribbon-one {
  left: 8vw;
  right: 16vw;
  top: 12vh;
  background:
    linear-gradient(105deg, transparent 0 18%, rgb(255 255 255 / 48%) 35%, rgb(232 195 108 / 24%) 50%, transparent 74%);
  transform: rotate(-8deg);
  animation: ribbonDriftOne 19s ease-in-out infinite;
}

.ribbon-two {
  left: 18vw;
  right: 4vw;
  bottom: 8vh;
  background:
    linear-gradient(110deg, transparent 0 20%, rgb(200 90 84 / 18%) 36%, rgb(255 248 232 / 42%) 52%, transparent 78%);
  transform: rotate(9deg);
  animation: ribbonDriftTwo 21s ease-in-out infinite;
}

.prism-sheet {
  position: absolute;
  height: 30vh;
  min-height: 190px;
  border: 1px solid rgb(255 255 255 / 18%);
  border-radius: 44% 56% 50% 50% / 32% 38% 62% 68%;
  background:
    linear-gradient(112deg, transparent 0 18%, rgb(255 255 255 / 28%) 36%, rgb(232 195 108 / 13%) 50%, transparent 76%),
    repeating-linear-gradient(90deg, transparent 0 48px, rgb(255 255 255 / 10%) 49px 51px, transparent 52px 96px);
  filter: blur(9px);
  mix-blend-mode: screen;
  opacity: 0.18;
}

.sheet-one {
  left: 18vw;
  right: -10vw;
  top: 4vh;
  transform: rotate(-9deg);
  animation: prismSheetOne 24s ease-in-out infinite;
}

.sheet-two {
  left: -8vw;
  right: 24vw;
  bottom: 9vh;
  transform: rotate(7deg);
  background:
    linear-gradient(112deg, transparent 0 20%, rgb(255 255 255 / 24%) 38%, rgb(154 122 168 / 12%) 52%, transparent 78%),
    repeating-linear-gradient(90deg, transparent 0 52px, rgb(255 255 255 / 9%) 53px 55px, transparent 56px 104px);
  animation: prismSheetTwo 27s ease-in-out infinite;
}

.liquid-refraction {
  position: absolute;
  left: -10vw;
  width: 120vw;
  height: 18vh;
  min-height: 120px;
  border-top: 1px solid rgb(255 255 255 / 16%);
  border-bottom: 1px solid rgb(255 255 255 / 12%);
  background:
    repeating-linear-gradient(90deg, transparent 0 40px, rgb(255 255 255 / 12%) 44px 46px, transparent 50px 86px),
    linear-gradient(100deg, transparent, rgb(255 248 232 / 18%) 42%, transparent 70%);
  filter: blur(0.4px);
  mix-blend-mode: screen;
  opacity: 0.16;
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 16%, #000 84%, transparent);
  mask-image: linear-gradient(90deg, transparent, #000 16%, #000 84%, transparent);
}

.refraction-one {
  top: 30vh;
  transform: rotate(-5deg);
  animation: refractionFlowOne 18s ease-in-out infinite;
}

.refraction-two {
  bottom: 20vh;
  transform: rotate(4deg);
  animation: refractionFlowTwo 22s ease-in-out infinite;
}

.glass-caustic {
  position: absolute;
  width: 260px;
  height: 260px;
  border-radius: 38% 62% 54% 46%;
  border: 1px solid rgb(255 255 255 / 22%);
  background:
    radial-gradient(circle at 38% 32%, rgb(255 255 255 / 32%), transparent 25%),
    linear-gradient(135deg, rgb(255 255 255 / 16%), transparent 60%);
  filter: blur(1px);
  mix-blend-mode: screen;
  opacity: 0.24;
}

.caustic-one {
  left: 34vw;
  top: 18vh;
  animation: causticFloat 15s ease-in-out infinite;
}

.caustic-two {
  right: 10vw;
  top: 52vh;
  animation: causticFloat 17s ease-in-out infinite reverse;
}

.caustic-three {
  left: 58vw;
  top: 10vh;
  width: 340px;
  height: 210px;
  border-radius: 62% 38% 56% 44% / 46% 54% 46% 54%;
  opacity: 0.18;
  animation: causticFloat 19s ease-in-out infinite;
}

.leak-one {
  left: -14vw;
  top: 8vh;
  background: radial-gradient(circle, rgb(255 196 94 / 62%), rgb(200 90 84 / 24%) 42%, transparent 70%);
  animation: lightLeakOne 16s ease-in-out infinite;
}

.leak-two {
  right: -18vw;
  bottom: -18vh;
  background: radial-gradient(circle, rgb(255 241 205 / 58%), rgb(154 122 168 / 18%) 44%, transparent 72%);
  animation: lightLeakTwo 18s ease-in-out infinite;
}

.film-scratch {
  position: absolute;
  top: -20vh;
  bottom: -20vh;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgb(255 255 255 / 36%), transparent);
  opacity: 0.38;
}

.scratch-one {
  left: 21vw;
  animation: scratchDrift 7s ease-in-out infinite;
}

.scratch-two {
  right: 16vw;
  animation: scratchDrift 8.5s ease-in-out infinite reverse;
}

@keyframes filmGrainDrift {
  0% { transform: translate(0, 0); }
  20% { transform: translate(-2%, 1%); }
  40% { transform: translate(1%, -2%); }
  60% { transform: translate(2%, 1%); }
  80% { transform: translate(-1%, -1%); }
  100% { transform: translate(0, 0); }
}

@keyframes filmGateWeave {
  0%,
  100% {
    transform: translateX(0);
    opacity: 0.36;
  }
  50% {
    transform: translateX(8px);
    opacity: 0.52;
  }
}

@keyframes lightLeakOne {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
    opacity: 0.28;
  }
  50% {
    transform: translate3d(7vw, 6vh, 0) scale(1.12);
    opacity: 0.46;
  }
}

@keyframes lightLeakTwo {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
    opacity: 0.24;
  }
  50% {
    transform: translate3d(-6vw, -5vh, 0) scale(1.08);
    opacity: 0.42;
  }
}

@keyframes scratchDrift {
  0%,
  100% {
    transform: translateX(0) rotate(1deg);
    opacity: 0.16;
  }
  45% {
    transform: translateX(22px) rotate(-1deg);
    opacity: 0.38;
  }
}

@keyframes ribbonDriftOne {
  0%,
  100% {
    transform: translate3d(-4vw, 0, 0) rotate(-8deg) scale(0.96);
    opacity: 0.14;
  }
  50% {
    transform: translate3d(5vw, 6vh, 0) rotate(-4deg) scale(1.05);
    opacity: 0.28;
  }
}

@keyframes ribbonDriftTwo {
  0%,
  100% {
    transform: translate3d(4vw, 0, 0) rotate(9deg) scale(0.98);
    opacity: 0.12;
  }
  50% {
    transform: translate3d(-6vw, -5vh, 0) rotate(5deg) scale(1.08);
    opacity: 0.25;
  }
}

@keyframes causticFloat {
  0%,
  100% {
    transform: translate3d(0, 0, 0) rotate(0deg);
    border-radius: 38% 62% 54% 46%;
  }
  50% {
    transform: translate3d(22px, -18px, 0) rotate(12deg);
    border-radius: 58% 42% 44% 56%;
  }
}

@keyframes prismSheetOne {
  0%,
  100% {
    transform: translate3d(-3vw, 0, 0) rotate(-9deg) scale(0.98);
    opacity: 0.12;
  }
  50% {
    transform: translate3d(5vw, 5vh, 0) rotate(-6deg) scale(1.04);
    opacity: 0.24;
  }
}

@keyframes prismSheetTwo {
  0%,
  100% {
    transform: translate3d(4vw, 1vh, 0) rotate(7deg) scale(1);
    opacity: 0.11;
  }
  50% {
    transform: translate3d(-4vw, -4vh, 0) rotate(4deg) scale(1.06);
    opacity: 0.22;
  }
}

@keyframes refractionFlowOne {
  0%,
  100% {
    background-position: 0 0, 0 0;
    opacity: 0.1;
  }
  50% {
    background-position: 120px 0, 16vw 0;
    opacity: 0.22;
  }
}

@keyframes refractionFlowTwo {
  0%,
  100% {
    background-position: 80px 0, 0 0;
    opacity: 0.09;
  }
  50% {
    background-position: -100px 0, -14vw 0;
    opacity: 0.2;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ambient-film-layer::before,
  .ambient-film-layer::after,
  .light-leak,
  .liquid-ribbon,
  .prism-sheet,
  .liquid-refraction,
  .glass-caustic,
  .film-scratch {
    animation: none !important;
  }
}
</style>
