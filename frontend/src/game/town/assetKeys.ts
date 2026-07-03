export const townAssetKeys = {
  map: 'town-tiled-map',
  grass: 'town-grass',
  path: 'town-path',
  stonePath: 'town-stone-path',
  houseWalls: 'town-house-walls',
  houseRoof: 'town-house-roof',
  treeObjects: 'town-tree-objects',
  natureObjects: 'town-nature-objects',
  signObjects: 'town-sign-objects',
  waterWell: 'town-water-well',
  workStation: 'town-work-station',
  player: 'town-player',
  chicken: 'town-chicken',
  cow: 'town-cow',
  sunflowerStages: 'town-sunflower-stages',
  farmingPlants: 'town-farming-plants',
} as const

const GAME_ASSET_VERSION = '20260703-nginx-fixed'
const gameAsset = (path: string) => `${path}?v=${GAME_ASSET_VERSION}`

// These files live under frontend/public, so Phaser can load them with absolute URLs.
export const townAssetPaths = {
  map: gameAsset('/game/maps/town.backup.tmj'),
  grass: gameAsset('/game/sprout_lands/tilesets/Grass_tiles_v2.png'),
  path: gameAsset('/game/sprout_lands/tilesets/Paths.png'),
  stonePath: gameAsset('/game/sprout_lands/tilesets/Stone_Path.png'),
  houseWalls: gameAsset('/game/sprout_lands/tilesets/Wooden_House_Walls_Tilset.png'),
  houseRoof: gameAsset('/game/sprout_lands/tilesets/Wooden_House_Roof_Tilset.png'),
  treeObjects: gameAsset('/game/sprout_lands/objects/Trees_stumps_bushes.png'),
  natureObjects: gameAsset('/game/sprout_lands/objects/Mushrooms_Flowers_Stones.png'),
  signObjects: gameAsset('/game/sprout_lands/objects/signs.png'),
  waterWell: gameAsset('/game/sprout_lands/objects/Water_well.png'),
  workStation: gameAsset('/game/sprout_lands/objects/work_station.png'),
  player: gameAsset('/game/sprout_lands/characters/Basic_Charakter_Spritesheet.png'),
  chicken: gameAsset('/game/sprout_lands/animals/Chicken_Baby.png'),
  cow: gameAsset('/game/sprout_lands/animals/Green cow animation sprites.png'),
  sunflowerStages: gameAsset('/game/sprout_lands/objects/Mushrooms_Flowers_Stones.png'),
  farmingPlants: gameAsset('/game/sprout_lands/objects/Farming_Plants.png'),
} as const

export const townTilesets = [
  { name: 'Grass_tiles_v2', key: 'tileset-Grass_tiles_v2', path: gameAsset('/game/sprout_lands/tilesets/Grass_tiles_v2.png') },
  { name: 'Tilled_Dirt', key: 'tileset-Tilled_Dirt', path: gameAsset('/game/sprout_lands/tilesets/Tilled_Dirt.png') },
  { name: 'Basic_Furniture', key: 'tileset-Basic_Furniture', path: gameAsset('/game/sprout_lands/tilesets/Basic_Furniture.png') },
  { name: 'door_animation_sprites', key: 'tileset-door_animation_sprites', path: gameAsset('/game/sprout_lands/tilesets/door_animation_sprites.png') },
  { name: 'Paths', key: 'tileset-Paths', path: gameAsset('/game/sprout_lands/tilesets/Paths.png') },
  { name: 'Water Objects', key: 'tileset-Water_Objects', path: gameAsset('/game/sprout_lands/objects/Water_Objects.png') },
  { name: 'Bitmask references gif', key: 'tileset-Bitmask_references_gif', path: gameAsset('/game/sprout_lands/tilesets/Bitmask_references_gif.gif') },
  { name: 'TILES PREVIEW v.2', key: 'tileset-TILES_PREVIEW_v2', path: gameAsset('/game/sprout_lands/tilesets/TILES_PREVIEW_v2.png') },
  { name: 'Mailbox Animation Frames', key: 'tileset-Mailbox_Animation_Frames', path: gameAsset('/game/sprout_lands/tilesets/Mailbox_Animation_Frames.png') },
  { name: 'Mushrooms, Flowers, Stones', key: 'tileset-Mushrooms_Flowers_Stones', path: gameAsset('/game/sprout_lands/objects/Mushrooms_Flowers_Stones.png') },
  { name: 'Trees, stumps and bushes', key: 'tileset-Trees_stumps_bushes', path: gameAsset('/game/sprout_lands/objects/Trees_stumps_bushes.png') },
  { name: 'Farming Plants', key: 'tileset-Farming_Plants', path: gameAsset('/game/sprout_lands/objects/Farming_Plants.png') },
  { name: 'signs', key: 'tileset-signs', path: gameAsset('/game/sprout_lands/objects/signs.png') },
  { name: 'Fences', key: 'tileset-Fences', path: gameAsset('/game/sprout_lands/tilesets/Fences.png') },
  { name: 'Grass_Hill_Tiles_v2', key: 'tileset-Grass_Hill_Tiles_v2', path: gameAsset('/game/sprout_lands/tilesets/Grass_Hill_Tiles_v2.png') },
  { name: 'houses_96_spritesheet', key: 'tileset-houses_96_spritesheet', path: gameAsset('/game/sprout_lands/house/houses_96_spritesheet.png') },
  { name: 'Boats', key: 'tileset-Boats', path: gameAsset('/game/sprout_lands/objects/Boats.png') },
  { name: 'Wooden_Bridge', key: 'tileset-Wooden_Bridge', path: gameAsset('/game/sprout_lands/tilesets/Wooden_Bridge.png') },
] as const
