const TOWN_ITEM_IDS = [
  'sunflower_seed',
  'pumpkin_seed',
  'white_bell_seed',
  'green_star_seed',
  'purple_mushroom_spore',
  'blue_star_seed',
  'sunflower',
  'pumpkin',
  'white_bell',
  'green_star',
  'purple_mushroom',
  'blue_star',
] as const

export type ItemId = typeof TOWN_ITEM_IDS[number]
export type CropId =
  | 'sunflower'
  | 'pumpkin'
  | 'white_bell'
  | 'green_star'
  | 'purple_mushroom'
  | 'blue_star'
export type CropTextureId = 'natureObjects' | 'farmingPlants'

export interface InventoryItem {
  id: ItemId
  count: number
}

export interface FarmPlotState {
  id: string
  cropId: CropId
  plantedAt: number
  growMs: number
}

export interface TownState {
  inventory: InventoryItem[]
  farmPlots: FarmPlotState[]
  rewardLog: string[]
}

export interface TownReward {
  itemId: ItemId
  count: number
  label: string
}

const STORAGE_KEY = 'u-life-town-state-v1'
const DEFAULT_GROW_MS = 120_000

export interface CropDefinition {
  id: CropId
  label: string
  seedItemId: ItemId
  seedLabel: string
  harvestItemId: ItemId
  harvestLabel: string
  texture: CropTextureId
  frames: readonly number[]
  growMs: number
}

// Crop frames are zero-based indexes in 16x16 spritesheets.
// Add or change plants here first; scene rendering and farm UI read this table.
export const CROP_DEFINITIONS: Record<CropId, CropDefinition> = {
  sunflower: {
    id: 'sunflower',
    label: '向日葵',
    seedItemId: 'sunflower_seed',
    seedLabel: '向日葵种子',
    harvestItemId: 'sunflower',
    harvestLabel: '向日葵',
    texture: 'natureObjects',
    frames: [36, 37, 38, 39],
    growMs: DEFAULT_GROW_MS,
  },
  pumpkin: {
    id: 'pumpkin',
    label: '南瓜',
    seedItemId: 'pumpkin_seed',
    seedLabel: '南瓜种子',
    harvestItemId: 'pumpkin',
    harvestLabel: '南瓜',
    texture: 'farmingPlants',
    frames: [45, 46, 47, 48],
    growMs: DEFAULT_GROW_MS,
  },
  white_bell: {
    id: 'white_bell',
    label: '白铃花',
    seedItemId: 'white_bell_seed',
    seedLabel: '白铃花种子',
    harvestItemId: 'white_bell',
    harvestLabel: '白铃花',
    texture: 'farmingPlants',
    frames: [15, 16, 17, 18],
    growMs: DEFAULT_GROW_MS,
  },
  green_star: {
    id: 'green_star',
    label: '青星花',
    seedItemId: 'green_star_seed',
    seedLabel: '青星花种子',
    harvestItemId: 'green_star',
    harvestLabel: '青星花',
    texture: 'farmingPlants',
    frames: [30, 31, 32, 33],
    growMs: DEFAULT_GROW_MS,
  },
  purple_mushroom: {
    id: 'purple_mushroom',
    label: '紫蘑菇',
    seedItemId: 'purple_mushroom_spore',
    seedLabel: '紫蘑菇孢子',
    harvestItemId: 'purple_mushroom',
    harvestLabel: '紫蘑菇',
    texture: 'natureObjects',
    frames: [3, 4, 5, 6],
    growMs: DEFAULT_GROW_MS,
  },
  blue_star: {
    id: 'blue_star',
    label: '蓝星花',
    seedItemId: 'blue_star_seed',
    seedLabel: '蓝星花种子',
    harvestItemId: 'blue_star',
    harvestLabel: '蓝星花',
    texture: 'farmingPlants',
    frames: [65, 66, 67, 68],
    growMs: DEFAULT_GROW_MS,
  },
}

export const CROP_DEFINITION_LIST = Object.values(CROP_DEFINITIONS)

export const TOWN_INVENTORY_ITEMS: Array<{ id: ItemId; label: string }> = [
  ...CROP_DEFINITION_LIST.map(crop => ({ id: crop.seedItemId, label: crop.seedLabel })),
  ...CROP_DEFINITION_LIST.map(crop => ({ id: crop.harvestItemId, label: crop.harvestLabel })),
]

const MOOD_CROP_REWARDS: Record<string, CropId> = {
  happy: 'sunflower',
  开心: 'sunflower',
  neutral: 'pumpkin',
  平静: 'pumpkin',
  sad: 'white_bell',
  难过: 'white_bell',
  悲伤: 'white_bell',
  anxious: 'green_star',
  焦虑: 'green_star',
  紧张: 'green_star',
  angry: 'purple_mushroom',
  生气: 'purple_mushroom',
  愤怒: 'purple_mushroom',
  surprised: 'blue_star',
  惊讶: 'blue_star',
  意外: 'blue_star',
}

const LEGACY_ITEM_ID_MAP: Record<string, ItemId> = {
  lavender_seed: 'pumpkin_seed',
  rain_lily_seed: 'white_bell_seed',
  moon_grass_seed: 'green_star_seed',
  pepper_seed: 'purple_mushroom_spore',
  star_bloom_seed: 'blue_star_seed',
}

const createDefaultState = (): TownState => ({
  inventory: TOWN_INVENTORY_ITEMS.map(item => ({ id: item.id, count: 0 })),
  farmPlots: [],
  rewardLog: [],
})

const isItemId = (value: unknown): value is ItemId =>
  typeof value === 'string' && (TOWN_ITEM_IDS as readonly string[]).includes(value)

export const getCropDefinition = (cropId: string | null | undefined) =>
  cropId && cropId in CROP_DEFINITIONS ? CROP_DEFINITIONS[cropId as CropId] : undefined

const normalizeInventory = (inventory: unknown): InventoryItem[] => {
  const counts = new Map<ItemId, number>(TOWN_INVENTORY_ITEMS.map(item => [item.id, 0]))
  if (!Array.isArray(inventory)) return createDefaultState().inventory

  inventory.forEach(entry => {
    if (!entry || typeof entry !== 'object') return
    const rawId = (entry as Partial<InventoryItem>).id
    const itemId = isItemId(rawId) ? rawId : LEGACY_ITEM_ID_MAP[String(rawId)]
    const count = Number((entry as Partial<InventoryItem>).count)
    if (!itemId || !Number.isFinite(count) || count <= 0) return
    counts.set(itemId, (counts.get(itemId) ?? 0) + count)
  })

  return TOWN_INVENTORY_ITEMS.map(item => ({
    id: item.id,
    count: counts.get(item.id) ?? 0,
  }))
}

const normalizeFarmPlots = (farmPlots: unknown): FarmPlotState[] => {
  if (!Array.isArray(farmPlots)) return []

  return farmPlots
    .map(entry => {
      if (!entry || typeof entry !== 'object') return null
      const raw = entry as Partial<FarmPlotState>
      const crop = getCropDefinition(raw.cropId)
      const plantedAt = Number(raw.plantedAt)
      const growMs = Number(raw.growMs)
      if (!raw.id || !crop || !Number.isFinite(plantedAt)) return null

      return {
        id: String(raw.id),
        cropId: crop.id,
        plantedAt,
        growMs: Number.isFinite(growMs) && growMs > 0 ? growMs : crop.growMs,
      }
    })
    .filter((plot): plot is FarmPlotState => Boolean(plot))
}

export const loadTownState = (): TownState => {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return createDefaultState()

  try {
    const parsed = JSON.parse(raw) as Partial<TownState>
    return {
      inventory: normalizeInventory(parsed.inventory),
      farmPlots: normalizeFarmPlots(parsed.farmPlots),
      rewardLog: Array.isArray(parsed.rewardLog) ? parsed.rewardLog : [],
    }
  } catch {
    return createDefaultState()
  }
}

export const saveTownState = (state: TownState) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  window.dispatchEvent(new CustomEvent('town-state-changed'))
}

export const getItemCount = (state: TownState, itemId: ItemId) =>
  state.inventory.find(item => item.id === itemId)?.count ?? 0

export const addItem = (itemId: ItemId, count = 1) => {
  const state = loadTownState()
  const item = state.inventory.find(entry => entry.id === itemId)
  if (item) item.count += count
  else state.inventory.push({ id: itemId, count })
  saveTownState(state)
}

const consumeItem = (state: TownState, itemId: ItemId, count = 1) => {
  const item = state.inventory.find(entry => entry.id === itemId)
  if (!item || item.count < count) return false
  item.count -= count
  return true
}

export const getFarmPlotState = (state: TownState, plotId: string) =>
  state.farmPlots.find(plot => plot.id === plotId)

export const getCropStage = (plot: FarmPlotState, now = Date.now()) => {
  const crop = getCropDefinition(plot.cropId) ?? CROP_DEFINITIONS.sunflower
  if (isFarmPlotMature(plot, now)) return crop.frames.length - 1

  const progress = Math.max(0, Math.min(1, (now - plot.plantedAt) / plot.growMs))
  return Math.min(crop.frames.length - 2, Math.floor(progress * (crop.frames.length - 1)))
}

export const isFarmPlotMature = (plot: FarmPlotState, now = Date.now()) =>
  now - plot.plantedAt >= plot.growMs

export const plantCrop = (plotId: string, cropId: CropId) => {
  const crop = getCropDefinition(cropId)
  if (!crop) return { ok: false, reason: 'unknown_crop' as const }

  const state = loadTownState()
  if (getFarmPlotState(state, plotId)) return { ok: false, reason: 'occupied' as const }
  if (!consumeItem(state, crop.seedItemId, 1)) return { ok: false, reason: 'no_seed' as const }

  state.farmPlots.push({
    id: plotId,
    cropId: crop.id,
    plantedAt: Date.now(),
    growMs: crop.growMs,
  })
  saveTownState(state)
  return { ok: true as const, crop }
}

export const harvestCrop = (plotId: string) => {
  const state = loadTownState()
  const plot = getFarmPlotState(state, plotId)
  if (!plot) return { ok: false, reason: 'empty' as const }
  const cropDefinition = getCropDefinition(plot.cropId)
  if (!cropDefinition) return { ok: false, reason: 'unknown_crop' as const }
  if (!isFarmPlotMature(plot)) return { ok: false, reason: 'growing' as const }

  state.farmPlots = state.farmPlots.filter(item => item.id !== plotId)
  const cropItem = state.inventory.find(item => item.id === cropDefinition.harvestItemId)
  if (cropItem) cropItem.count += 1
  else state.inventory.push({ id: cropDefinition.harvestItemId, count: 1 })
  saveTownState(state)
  return { ok: true as const, crop: cropDefinition }
}

export const grantMoodReward = (emotionLabel: string | null, sourceId: string): TownReward | null => {
  const crop = emotionLabel ? getCropDefinition(MOOD_CROP_REWARDS[emotionLabel]) : undefined
  if (!crop) return null

  const state = loadTownState()
  const rewardKey = `chat-${emotionLabel}:${sourceId}`
  if (state.rewardLog.includes(rewardKey)) return null

  const item = state.inventory.find(entry => entry.id === crop.seedItemId)
  if (item) item.count += 1
  else state.inventory.push({ id: crop.seedItemId, count: 1 })
  state.rewardLog.push(rewardKey)
  saveTownState(state)

  return {
    itemId: crop.seedItemId,
    count: 1,
    label: crop.seedLabel,
  }
}
