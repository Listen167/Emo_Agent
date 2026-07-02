<script setup lang="ts">
import * as Phaser from 'phaser'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { GameTownScene, type TownEnterEvent, type TownInteractEvent } from '../game/town/GameTownScene'
import { townBuildings, type TownViewKey } from '../game/town/buildings'
import {
  CROP_DEFINITION_LIST,
  getCropDefinition,
  getCropStage,
  getFarmPlotState,
  getItemCount,
  harvestCrop,
  isFarmPlotMature,
  loadTownState,
  plantCrop,
  TOWN_INVENTORY_ITEMS,
  type CropId,
  type TownState,
} from '../game/town/townState'

const emit = defineEmits<{
  (event: 'enter-view', view: TownViewKey): void
}>()

const gameHost = ref<HTMLDivElement | null>(null)
const townState = ref<TownState>(loadTownState())
const selectedFarmPlotId = ref<string | null>(null)
const farmMessage = ref('')
let game: Phaser.Game | null = null

const inventoryRows = computed(() =>
  TOWN_INVENTORY_ITEMS.map(item => ({
    ...item,
    count: getItemCount(townState.value, item.id),
  }))
)
const seedCropRows = computed(() =>
  CROP_DEFINITION_LIST.map(crop => ({
    crop,
    seedCount: getItemCount(townState.value, crop.seedItemId),
  }))
)
const hasAnySeed = computed(() => seedCropRows.value.some(row => row.seedCount > 0))
const selectedFarmPlot = computed(() =>
  selectedFarmPlotId.value ? getFarmPlotState(townState.value, selectedFarmPlotId.value) : undefined
)
const selectedFarmCrop = computed(() =>
  selectedFarmPlot.value ? getCropDefinition(selectedFarmPlot.value.cropId) : undefined
)
const selectedFarmStage = computed(() => selectedFarmPlot.value ? getCropStage(selectedFarmPlot.value) + 1 : 0)
const selectedFarmStageTotal = computed(() => selectedFarmCrop.value?.frames.length ?? 4)
const selectedFarmMature = computed(() => selectedFarmPlot.value ? isFarmPlotMature(selectedFarmPlot.value) : false)
const selectedFarmTitle = computed(() => selectedFarmCrop.value ? `${selectedFarmCrop.value.label}农田` : '农田')
const selectedFarmStatus = computed(() => {
  if (!selectedFarmPlotId.value) return ''
  if (!selectedFarmPlot.value) {
    return hasAnySeed.value
      ? '这块地还空着，选择一种已有种子种下。'
      : '这块地还空着。和小曦聊天获得种子后，再回来种植。'
  }
  if (!selectedFarmCrop.value) return '这块地的作物配置不存在，请检查作物定义。'
  if (selectedFarmMature.value) return `${selectedFarmCrop.value.label}已经成熟，可以收获。`
  return `${selectedFarmCrop.value.label}正在成长：第 ${selectedFarmStage.value} / ${selectedFarmStageTotal.value} 阶段。`
})

const taskItems = computed(() => [
  '拜访小曦的家，完成一次情绪记录',
  '去胶片仓库保存一张生活照片',
  '到简历工坊检查一段项目经历',
])

const handleEnterView = (event: TownEnterEvent) => {
  emit('enter-view', event.building.view)
}

const refreshTownState = () => {
  townState.value = loadTownState()
}

const syncFarmScene = () => {
  game?.events.emit('town:farm-updated')
}

const handleTownInteract = (event: TownInteractEvent) => {
  if (event.type !== 'farm') return
  refreshTownState()
  selectedFarmPlotId.value = event.plotId
  farmMessage.value = ''
}

const closeFarmModal = () => {
  selectedFarmPlotId.value = null
  farmMessage.value = ''
}

const plantSelectedFarm = (cropId: CropId) => {
  if (!selectedFarmPlotId.value) return
  const crop = getCropDefinition(cropId)
  const result = plantCrop(selectedFarmPlotId.value, cropId)
  refreshTownState()
  syncFarmScene()

  if (result.ok) {
    farmMessage.value = `已种下${crop?.label ?? '作物'}。`
    return
  }

  if (result.reason === 'no_seed') {
    farmMessage.value = `没有${crop?.seedLabel ?? '这种种子'}。和小曦聊天时会按情绪获得不同种子。`
    return
  }

  farmMessage.value = result.reason === 'occupied'
    ? '这块地已经种过了。'
    : '没有找到这种作物配置。'
}

const harvestSelectedFarm = () => {
  if (!selectedFarmPlotId.value) return
  const crop = selectedFarmCrop.value
  const result = harvestCrop(selectedFarmPlotId.value)
  refreshTownState()
  syncFarmScene()

  if (result.ok) {
    farmMessage.value = `收获了 1 个${crop?.harvestLabel ?? '作物'}。`
    return
  }

  farmMessage.value = result.reason === 'growing'
    ? '还没有成熟。'
    : result.reason === 'unknown_crop'
      ? '作物配置不存在，暂时不能收获。'
      : '这块地还没有作物。'
}

onMounted(() => {
  if (!gameHost.value) return

  // Vue owns the shell and side panels; Phaser owns only the canvas inside gameHost.
  game = new Phaser.Game({
    type: Phaser.AUTO,
    parent: gameHost.value,
    width: 1040,
    height: 720,
    backgroundColor: '#7cab6f',
    pixelArt: true,
    physics: {
      default: 'arcade',
      arcade: {
        debug: false,
      },
    },
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    scene: GameTownScene,
  })

  game.events.on('town:enter-view', handleEnterView)
  game.events.on('town:interact', handleTownInteract)
  window.addEventListener('town-state-changed', refreshTownState)
})

onBeforeUnmount(() => {
  // Destroy Phaser when Vue unmounts this view to avoid duplicate canvases after hot reload.
  if (game) {
    game.events.off('town:enter-view', handleEnterView)
    game.events.off('town:interact', handleTownInteract)
    game.destroy(true)
    game = null
  }
  window.removeEventListener('town-state-changed', refreshTownState)
})
</script>

<template>
  <main class="game-town-view">
    <section class="town-topbar">
      <div>
        <span class="town-chip">Town Home</span>
        <h1>U-Life 小镇</h1>
        <p>移动角色靠近建筑，按 E 进入对应功能。</p>
      </div>
      <div class="player-status">
        <span>Lv. 1</span>
        <strong>胶片旅人</strong>
        <i aria-hidden="true"><b style="width: 36%"></b></i>
      </div>
    </section>

    <section class="town-layout">
      <div class="town-canvas-shell">
        <div ref="gameHost" class="town-canvas" />
      </div>

      <aside class="town-side-panel">
        <section class="town-card">
          <span class="town-card-label">Buildings</span>
          <button
            v-for="building in townBuildings"
            :key="building.id"
            class="building-shortcut"
            type="button"
            @click="emit('enter-view', building.view)"
          >
            <span>{{ building.name }}</span>
          </button>
        </section>

        <section class="town-card">
          <span class="town-card-label">Bag</span>
          <div
            v-for="item in inventoryRows"
            :key="item.id"
            class="inventory-row"
          >
            <span>{{ item.label }}</span>
            <strong>{{ item.count }}</strong>
          </div>
        </section>

        <section class="town-card">
          <span class="town-card-label">Today</span>
          <ul class="task-list">
            <li v-for="task in taskItems" :key="task">{{ task }}</li>
          </ul>
        </section>
      </aside>
    </section>

    <div v-if="selectedFarmPlotId" class="farm-modal-backdrop" @click.self="closeFarmModal">
      <section class="farm-modal" role="dialog" aria-modal="true" aria-labelledby="farm-modal-title">
        <div>
          <span class="town-card-label">Farm Plot</span>
          <h2 id="farm-modal-title">{{ selectedFarmTitle }}</h2>
          <p>{{ selectedFarmStatus }}</p>
        </div>

        <div class="farm-stage-strip" aria-label="作物成长阶段">
          <span
            v-for="stage in selectedFarmStageTotal"
            :key="stage"
            :class="{ active: selectedFarmPlot && stage <= selectedFarmStage, mature: selectedFarmMature }"
          >
            {{ stage }}
          </span>
        </div>

        <div v-if="!selectedFarmPlot" class="seed-choice-grid">
          <button
            v-for="row in seedCropRows"
            :key="row.crop.id"
            type="button"
            class="seed-choice"
            :disabled="row.seedCount <= 0"
            @click="plantSelectedFarm(row.crop.id)"
          >
            <strong>{{ row.crop.seedLabel }}</strong>
            <span>背包 {{ row.seedCount }}</span>
          </button>
        </div>

        <div class="farm-actions">
          <button
            v-if="selectedFarmPlot"
            class="primary-action"
            type="button"
            :disabled="!selectedFarmMature"
            @click="harvestSelectedFarm"
          >
            收获{{ selectedFarmCrop?.label || '作物' }}
          </button>
          <button type="button" @click="closeFarmModal">关闭</button>
        </div>

        <p v-if="farmMessage" class="farm-message">{{ farmMessage }}</p>
      </section>
    </div>
  </main>
</template>

<style scoped>
.game-town-view {
  min-height: 100vh;
  padding: 26px 30px 42px;
  color: var(--journal-ink);
}

.town-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px 24px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 78%);
  box-shadow: 0 16px 38px rgb(62 50 40 / 12%);
}

.town-chip,
.town-card-label {
  display: inline-block;
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 800;
}

.town-chip {
  padding: 5px 12px;
  color: var(--journal-ink);
  background: var(--journal-kodak);
}

.town-topbar h1 {
  margin: 8px 0 0;
  font-size: clamp(38px, 5vw, 64px);
  line-height: 0.92;
}

.town-topbar p {
  margin: 8px 0 0;
  color: var(--journal-muted);
  font-size: 14px;
}

.player-status {
  flex: 0 0 190px;
  display: grid;
  gap: 7px;
  padding: 14px;
  border: 1px dashed rgb(62 50 40 / 24%);
  background: rgb(253 251 247 / 72%);
}

.player-status span,
.player-status strong {
  display: block;
}

.player-status span {
  color: var(--journal-stamp);
  font-size: 12px;
  font-weight: 800;
}

.player-status strong {
  font-size: 17px;
}

.player-status i {
  overflow: hidden;
  height: 8px;
  border-radius: 999px;
  background: rgb(62 50 40 / 12%);
}

.player-status b {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--journal-stamp), var(--journal-kodak));
}

.town-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 286px;
  gap: 22px;
  padding-top: 24px;
}

.town-canvas-shell {
  position: relative;
  overflow: hidden;
  min-height: 720px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: #7cab6f;
  box-shadow: 0 20px 46px rgb(62 50 40 / 17%);
}

.town-canvas {
  width: 100%;
  height: 720px;
  min-height: 720px;
}

.town-canvas :deep(canvas) {
  display: block;
}

.town-side-panel {
  position: sticky;
  top: 24px;
  display: grid;
  gap: 16px;
  align-self: start;
}

.town-card {
  display: grid;
  gap: 10px;
  padding: 18px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 82%);
  box-shadow: 0 16px 34px rgb(62 50 40 / 12%);
}

.building-shortcut {
  display: grid;
  gap: 3px;
  min-height: 54px;
  padding: 10px 12px;
  border: 1px solid rgb(62 50 40 / 14%);
  border-radius: 12px;
  color: var(--journal-ink);
  text-align: left;
  background: rgb(253 251 247 / 72%);
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.building-shortcut:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgb(62 50 40 / 12%);
}

.building-shortcut span {
  font-size: 13px;
  font-weight: 900;
}

.inventory-row {
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid rgb(62 50 40 / 14%);
  background: rgb(253 251 247 / 72%);
}

.inventory-row span {
  color: var(--journal-muted);
  font-size: 13px;
}

.inventory-row strong {
  min-width: 28px;
  text-align: right;
  font-size: 18px;
}

.task-list {
  display: grid;
  gap: 9px;
  margin: 0;
  padding-left: 18px;
  color: var(--journal-muted);
  font-size: 13px;
  line-height: 1.55;
}

.farm-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 22px;
  background: rgb(28 19 14 / 32%);
  backdrop-filter: blur(6px);
}

.farm-modal {
  width: min(420px, 100%);
  display: grid;
  gap: 16px;
  padding: 22px;
  border: 1px solid rgb(62 50 40 / 16%);
  background: rgb(255 248 232 / 96%);
  box-shadow: 0 24px 58px rgb(28 19 14 / 26%);
}

.farm-modal h2 {
  margin: 6px 0 0;
  font-size: 28px;
  line-height: 1;
}

.farm-modal p {
  margin: 8px 0 0;
  color: var(--journal-muted);
  font-size: 14px;
  line-height: 1.55;
}

.farm-stage-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.farm-stage-strip span {
  min-height: 38px;
  display: grid;
  place-items: center;
  border: 1px solid rgb(62 50 40 / 12%);
  color: rgb(62 50 40 / 44%);
  background: rgb(253 251 247 / 62%);
  font-weight: 900;
}

.farm-stage-strip span.active {
  color: var(--journal-ink);
  background: rgb(232 195 108 / 48%);
}

.farm-stage-strip span.mature {
  background: rgb(135 167 119 / 42%);
}

.seed-choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.seed-choice {
  min-height: 58px;
  display: grid;
  gap: 4px;
  align-content: center;
  padding: 9px 11px;
  border: 1px solid rgb(62 50 40 / 14%);
  color: var(--journal-ink);
  text-align: left;
  background: rgb(253 251 247 / 78%);
  cursor: pointer;
}

.seed-choice strong,
.seed-choice span {
  display: block;
}

.seed-choice strong {
  font-size: 13px;
}

.seed-choice span {
  color: var(--journal-muted);
  font-size: 12px;
}

.seed-choice:not(:disabled):hover {
  border-color: rgb(135 167 119 / 48%);
  background: rgb(232 195 108 / 26%);
}

.seed-choice:disabled {
  opacity: 0.46;
  cursor: not-allowed;
}

.farm-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.farm-actions button {
  min-height: 42px;
  padding: 0 14px;
  border: 1px solid rgb(62 50 40 / 16%);
  color: var(--journal-ink);
  background: rgb(253 251 247 / 84%);
  cursor: pointer;
  font-weight: 900;
}

.farm-actions button.primary-action {
  background: var(--journal-kodak);
}

.farm-actions button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}

.farm-message {
  padding: 10px 12px;
  border: 1px dashed rgb(62 50 40 / 20%);
  background: rgb(253 251 247 / 72%);
}

@media (max-width: 1080px) {
  .town-layout {
    display: block;
  }

  .town-side-panel {
    position: relative;
    top: auto;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin-top: 18px;
  }
}

@media (max-width: 720px) {
  .game-town-view {
    padding: 16px 14px 110px;
  }

  .town-topbar {
    display: block;
    padding: 20px;
  }

  .player-status {
    margin-top: 16px;
  }

  .town-canvas-shell,
  .town-canvas {
    min-height: 520px;
  }

  .town-canvas {
    height: 520px;
  }

  .town-side-panel {
    grid-template-columns: 1fr;
  }
}
</style>
