import * as Phaser from 'phaser'

import { townAssetKeys, townAssetPaths, townTilesets } from './assetKeys'
import type { TownBuilding, TownViewKey } from './buildings'
import {
  type CropTextureId,
  getCropDefinition,
  getCropStage,
  getFarmPlotState,
  isFarmPlotMature,
  loadTownState,
} from './townState'

type TiledObject = Phaser.Types.Tilemaps.TiledObject

interface TownEntrance {
  building: TownBuilding
  zone: Phaser.GameObjects.Zone
}

interface TownAnimal {
  sprite: Phaser.Types.Physics.Arcade.SpriteWithDynamicBody
  bounds: Phaser.Geom.Rectangle
  kind: 'chicken' | 'cow'
  speed: number
  nextTurnAt: number
}

interface TownFarmPlot {
  id: string
  zone: Phaser.GameObjects.Zone
  x: number
  y: number
}

export interface TownEnterEvent {
  building: TownBuilding
}

export interface TownInteractEvent {
  type: 'farm'
  plotId: string
}

const TILE_SIZE = 16
const PLAYER_FRAME_SIZE = 48
const CHICKEN_FRAME_SIZE = 16
const COW_FRAME_SIZE = 32
const COW_IDLE_FRAME = 8
const PLAYER_SPEED = 168
const ENTRANCE_DISTANCE = 42
const FARM_DISTANCE = 34
const TILESET_PATH_BY_NAME = new Map<string, string>(townTilesets.map(tileset => [tileset.name, tileset.path]))
const CROP_TEXTURE_KEY_BY_ID: Record<CropTextureId, string> = {
  natureObjects: townAssetKeys.sunflowerStages,
  farmingPlants: townAssetKeys.farmingPlants,
}

export class GameTownScene extends Phaser.Scene {
  private cursors?: Phaser.Types.Input.Keyboard.CursorKeys
  private wasd?: Record<'W' | 'A' | 'S' | 'D' | 'E', Phaser.Input.Keyboard.Key>
  private player?: Phaser.Types.Physics.Arcade.SpriteWithDynamicBody
  private collisionGroup?: Phaser.Physics.Arcade.StaticGroup
  private activeEntrance: TownEntrance | null = null
  private activeFarmPlot: TownFarmPlot | null = null
  private entrances: TownEntrance[] = []
  private farmPlots: TownFarmPlot[] = []
  private cropSprites = new Map<string, Phaser.GameObjects.Image>()
  private animals: TownAnimal[] = []
  private enterLabel?: Phaser.GameObjects.Text
  private lastEnterAt = 0

  constructor() {
    super('GameTownScene')
  }

  preload() {
    this.load.tilemapTiledJSON(townAssetKeys.map, townAssetPaths.map)

    // Tiled stores tileset names in the map; Phaser separately needs the image textures loaded here.
    townTilesets.forEach(tileset => {
      this.load.image(tileset.key, tileset.path)
    })

    this.load.spritesheet(townAssetKeys.player, townAssetPaths.player, {
      frameWidth: PLAYER_FRAME_SIZE,
      frameHeight: PLAYER_FRAME_SIZE,
    })
    this.load.spritesheet(townAssetKeys.chicken, townAssetPaths.chicken, {
      frameWidth: CHICKEN_FRAME_SIZE,
      frameHeight: CHICKEN_FRAME_SIZE,
    })
    this.load.spritesheet(townAssetKeys.cow, townAssetPaths.cow, {
      frameWidth: COW_FRAME_SIZE,
      frameHeight: COW_FRAME_SIZE,
    })
    this.load.spritesheet(townAssetKeys.sunflowerStages, townAssetPaths.sunflowerStages, {
      frameWidth: TILE_SIZE,
      frameHeight: TILE_SIZE,
    })
    this.load.spritesheet(townAssetKeys.farmingPlants, townAssetPaths.farmingPlants, {
      frameWidth: TILE_SIZE,
      frameHeight: TILE_SIZE,
    })
  }

  create() {
    const map = this.make.tilemap({ key: townAssetKeys.map })
    const tilesets = this.createTilesets(map)

    map.layers.forEach(layerData => {
      const layer = map.createLayer(layerData.name, tilesets, 0, 0)
      layer?.setDepth(layerData.name === 'house' ? 20 : 1)
    })

    this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels)
    this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels)

    this.createAnimations()
    this.createCollision(map)
    this.createEntrances(map)
    this.createFarmPlots(map)
    this.createPlayer(map)
    this.createAnimals(map)
    this.createKeyboard()
    this.createHudLabels()
    this.refreshFarmCrops()
    this.time.addEvent({
      delay: 1000,
      loop: true,
      callback: this.refreshFarmCrops,
      callbackScope: this,
    })
    this.game.events.on('town:farm-updated', this.refreshFarmCrops, this)
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.game.events.off('town:farm-updated', this.refreshFarmCrops, this)
    })

    if (this.player && this.collisionGroup) {
      this.physics.add.collider(this.player, this.collisionGroup)
    }
  }

  update() {
    this.movePlayer()
    this.moveAnimals()
    this.updateActiveTargets()

    if (!this.wasd || !Phaser.Input.Keyboard.JustDown(this.wasd.E)) return

    if (this.activeFarmPlot) {
      this.interactFarmPlot(this.activeFarmPlot)
      return
    }

    if (this.activeEntrance) {
      this.enterBuilding(this.activeEntrance.building)
    }
  }

  private createTilesets(map: Phaser.Tilemaps.Tilemap) {
    return map.tilesets
      .map(tileset => {
        const path = TILESET_PATH_BY_NAME.get(tileset.name)
        if (!path) {
          console.warn(`Missing tileset config for ${tileset.name}`)
          return null
        }

        const config = townTilesets.find(item => item.path === path)
        if (!config) return null

        // Set the texture on the parsed Tileset object directly, so duplicate Tiled names still work.
        tileset.setImage(this.textures.get(config.key))
        return tileset
      })
      .filter((tileset): tileset is Phaser.Tilemaps.Tileset => Boolean(tileset))
  }

  private createAnimations() {
    this.anims.create({
      key: 'town-player-idle',
      frames: [{ key: townAssetKeys.player, frame: 0 }],
      frameRate: 1,
    })
    this.anims.create({
      key: 'town-player-walk',
      frames: this.anims.generateFrameNumbers(townAssetKeys.player, { start: 0, end: 3 }),
      frameRate: 7,
      repeat: -1,
    })
    this.anims.create({
      key: 'town-chicken-walk',
      frames: this.anims.generateFrameNumbers(townAssetKeys.chicken, { start: 0, end: 3 }),
      frameRate: 4,
      repeat: -1,
    })
    this.anims.create({
      key: 'town-cow-walk',
      // The cow spritesheet has transparent padding in the first row.
      // Use a full non-empty walking row, otherwise the cow flashes invisible.
      frames: this.anims.generateFrameNumbers(townAssetKeys.cow, { start: 8, end: 15 }),
      frameRate: 4,
      repeat: -1,
    })
  }

  private createCollision(map: Phaser.Tilemaps.Tilemap) {
    const collisionObjects = this.getObjects(map, 'Collision')
    this.collisionGroup = this.physics.add.staticGroup()

    collisionObjects.forEach(object => {
      const width = object.width ?? TILE_SIZE
      const height = object.height ?? TILE_SIZE
      const x = (object.x ?? 0) + width / 2
      const y = (object.y ?? 0) + height / 2

      const blocker = this.add.zone(x, y, width, height)
      this.physics.add.existing(blocker, true)
      this.collisionGroup?.add(blocker)
    })
  }

  private createEntrances(map: Phaser.Tilemaps.Tilemap) {
    this.entrances = this.getObjects(map, 'Entrances')
      .map(object => {
        const targetView = this.getObjectProperty(object, 'targetView')
        if (!targetView || !isTownViewKey(targetView)) return null

        const width = object.width ?? TILE_SIZE
        const height = object.height ?? TILE_SIZE
        const x = (object.x ?? 0) + width / 2
        const y = (object.y ?? 0) + height / 2
        const label = this.getObjectProperty(object, 'label') ?? object.name ?? targetView
        const id = this.getObjectProperty(object, 'name') ?? `${targetView}-entrance`
        const building: TownBuilding = {
          id,
          name: label,
          view: targetView,
          x,
          y,
          accent: 0x87a777,
        }
        const zone = this.add.zone(x, y, Math.max(width, 32), Math.max(height, 32))

        this.physics.add.existing(zone, true)
        zone.setInteractive()
        zone.on('pointerdown', () => this.enterBuilding(building))

        return { building, zone }
      })
      .filter((entrance): entrance is TownEntrance => Boolean(entrance))
  }

  private createFarmPlots(map: Phaser.Tilemaps.Tilemap) {
    const usedIds = new Set<string>()

    this.farmPlots = this.getObjects(map, 'FarmPlots')
      .map(object => {
        const customId = this.getObjectProperty(object, 'id')
        const plotId = customId || `farm_${object.id}`
        if (usedIds.has(plotId)) {
          console.warn(`Duplicate farm plot id skipped: ${plotId}`)
          return null
        }
        usedIds.add(plotId)

        const width = object.width ?? TILE_SIZE
        const height = object.height ?? TILE_SIZE
        const x = (object.x ?? 0) + width / 2
        const y = (object.y ?? 0) + height / 2
        const zone = this.add.zone(x, y, Math.max(width, 28), Math.max(height, 28))

        this.physics.add.existing(zone, true)
        zone.setInteractive()
        zone.on('pointerdown', () => this.interactFarmPlot({ id: plotId, zone, x, y }))

        return { id: plotId, zone, x, y }
      })
      .filter((plot): plot is TownFarmPlot => Boolean(plot))
  }

  private createPlayer(map: Phaser.Tilemaps.Tilemap) {
    const spawn = this.getObjects(map, 'PlayerSpawn')[0]
    const spawnX = spawn?.x ?? map.widthInPixels / 2
    const spawnY = spawn?.y ?? map.heightInPixels / 2

    this.player = this.physics.add.sprite(spawnX, spawnY, townAssetKeys.player, 0)
    this.player.setCollideWorldBounds(true)
    this.player.setDepth(30)
    this.player.setScale(1.12)
    this.player.setSize(24, 28)
    this.player.setOffset(12, 18)
    this.player.play('town-player-idle')
    this.cameras.main.startFollow(this.player, true, 0.12, 0.12)
  }

  private createAnimals(map: Phaser.Tilemaps.Tilemap) {
    const usedAnimalKeys = new Set<string>()

    this.animals = this.getObjects(map, 'Animals')
      .map(object => {
        const spriteKey = this.getObjectProperty(object, 'spriteKey')
        const kind = spriteKey === 'cow' ? 'cow' : 'chicken'
        const objectName = this.getObjectProperty(object, 'name') || object.name || `${kind}_${object.id}`
        const texture = kind === 'cow' ? townAssetKeys.cow : townAssetKeys.chicken
        const animation = kind === 'cow' ? 'town-cow-walk' : 'town-chicken-walk'
        const width = object.width ?? TILE_SIZE * 4
        const height = object.height ?? TILE_SIZE * 4
        const bounds = new Phaser.Geom.Rectangle(object.x ?? 0, object.y ?? 0, width, height)
        const animalKey = `${kind}:${objectName}:${Math.round(bounds.x)}:${Math.round(bounds.y)}`
        if (usedAnimalKeys.has(animalKey)) {
          console.warn(`Duplicate animal skipped: ${animalKey}`)
          return null
        }
        usedAnimalKeys.add(animalKey)

        const initialFrame = kind === 'cow' ? COW_IDLE_FRAME : 0
        const sprite = this.physics.add.sprite(bounds.centerX, bounds.centerY, texture, initialFrame)
        const configuredSpeed = this.getNumberProperty(object, 'speed', kind === 'cow' ? 10 : 14)
        const speed = Math.max(0, Math.min(configuredSpeed, kind === 'cow' ? 12 : 18))

        sprite.setDepth(25)
        sprite.setScale(kind === 'cow' ? 1.08 : 1.3)
        sprite.setCollideWorldBounds(true)
        sprite.play(animation)

        if (this.collisionGroup) {
          this.physics.add.collider(sprite, this.collisionGroup)
        }

        return {
          sprite,
          bounds,
          kind,
          speed,
          nextTurnAt: 0,
        }
      })
      .filter((animal): animal is TownAnimal => Boolean(animal))
  }

  private createKeyboard() {
    if (!this.input.keyboard) return
    this.cursors = this.input.keyboard.createCursorKeys()
    this.wasd = this.input.keyboard.addKeys('W,A,S,D,E') as Record<'W' | 'A' | 'S' | 'D' | 'E', Phaser.Input.Keyboard.Key>
  }

  private createHudLabels() {
    const panel = this.add.rectangle(22, 20, 254, 74, 0xfff8e8, 0.9)
      .setOrigin(0, 0)
      .setScrollFactor(0)
      .setDepth(90)
      .setStrokeStyle(2, 0x3e3228, 0.14)
    const title = this.add.text(42, 34, 'U-Life 小镇', {
      fontFamily: 'Microsoft YaHei, sans-serif',
      fontSize: '18px',
      fontStyle: 'bold',
      color: '#3e3228',
    }).setScrollFactor(0).setDepth(91)
    const help = this.add.text(42, 60, 'Ctrl+方向键，靠近入口按 E', {
      fontFamily: 'Microsoft YaHei, sans-serif',
      fontSize: '12px',
      color: '#6b5b4c',
    }).setScrollFactor(0).setDepth(91)

    this.enterLabel = this.add.text(520, 662, '', {
      fontFamily: 'Microsoft YaHei, sans-serif',
      fontSize: '15px',
      fontStyle: 'bold',
      color: '#3e3228',
      backgroundColor: '#fff8e8',
      padding: { x: 12, y: 7 },
    }).setOrigin(0.5).setScrollFactor(0).setDepth(92).setVisible(false)

    panel.setInteractive()
    title.setInteractive()
    help.setInteractive()
  }

  private movePlayer() {
    if (!this.player || !this.cursors || !this.wasd) return

    let velocityX = 0
    let velocityY = 0

    if (this.cursors.left.isDown || this.wasd.A.isDown) velocityX -= PLAYER_SPEED
    if (this.cursors.right.isDown || this.wasd.D.isDown) velocityX += PLAYER_SPEED
    if (this.cursors.up.isDown || this.wasd.W.isDown) velocityY -= PLAYER_SPEED
    if (this.cursors.down.isDown || this.wasd.S.isDown) velocityY += PLAYER_SPEED

    if (velocityX !== 0 && velocityY !== 0) {
      velocityX *= 0.707
      velocityY *= 0.707
    }

    this.player.setVelocity(velocityX, velocityY)
    if (velocityX < 0) this.player.setFlipX(true)
    if (velocityX > 0) this.player.setFlipX(false)

    if (velocityX !== 0 || velocityY !== 0) {
      this.player.play('town-player-walk', true)
    } else {
      this.player.play('town-player-idle', true)
    }
  }

  private moveAnimals() {
    this.animals.forEach(animal => {
      if (this.time.now >= animal.nextTurnAt || !animal.bounds.contains(animal.sprite.x, animal.sprite.y)) {
        this.pickAnimalDirection(animal)
      }

      if (animal.sprite.x <= animal.bounds.left || animal.sprite.x >= animal.bounds.right) {
        animal.sprite.setVelocityX(-animal.sprite.body.velocity.x)
      }
      if (animal.sprite.y <= animal.bounds.top || animal.sprite.y >= animal.bounds.bottom) {
        animal.sprite.setVelocityY(-animal.sprite.body.velocity.y)
      }

      if (animal.sprite.body.velocity.x < 0) animal.sprite.setFlipX(true)
      if (animal.sprite.body.velocity.x > 0) animal.sprite.setFlipX(false)
    })
  }

  private pickAnimalDirection(animal: TownAnimal) {
    const angle = Phaser.Math.FloatBetween(0, Math.PI * 2)
    const shouldRest = Phaser.Math.Between(0, animal.kind === 'cow' ? 2 : 3) === 0
    const speed = shouldRest ? 0 : animal.speed
    const minDelay = animal.kind === 'cow' ? 3600 : 1800
    const maxDelay = animal.kind === 'cow' ? 7200 : 4200

    animal.sprite.setVelocity(Math.cos(angle) * speed, Math.sin(angle) * speed)
    animal.nextTurnAt = this.time.now + Phaser.Math.Between(minDelay, maxDelay)
  }

  private updateActiveTargets() {
    if (!this.player) return

    let closest: TownEntrance | null = null
    let closestDistance = Number.POSITIVE_INFINITY

    for (const entrance of this.entrances) {
      const distance = Phaser.Math.Distance.Between(
        this.player.x,
        this.player.y,
        entrance.zone.x,
        entrance.zone.y,
      )

      if (distance < ENTRANCE_DISTANCE && distance < closestDistance) {
        closest = entrance
        closestDistance = distance
      }
    }

    this.activeEntrance = closest

    let closestFarm: TownFarmPlot | null = null
    let closestFarmDistance = Number.POSITIVE_INFINITY

    for (const plot of this.farmPlots) {
      const distance = Phaser.Math.Distance.Between(this.player.x, this.player.y, plot.zone.x, plot.zone.y)
      if (distance < FARM_DISTANCE && distance < closestFarmDistance) {
        closestFarm = plot
        closestFarmDistance = distance
      }
    }

    this.activeFarmPlot = closestFarm
    this.updateInteractionLabel()
  }

  private updateInteractionLabel() {
    if (this.activeFarmPlot) {
      this.enterLabel?.setText(this.getFarmPrompt(this.activeFarmPlot.id)).setVisible(true)
      return
    }

    if (this.activeEntrance) {
      this.enterLabel?.setText(`按 E 进入 ${this.activeEntrance.building.name}`).setVisible(true)
      return
    }

    this.enterLabel?.setText('').setVisible(false)
  }

  private getFarmPrompt(plotId: string) {
    const state = loadTownState()
    const plot = getFarmPlotState(state, plotId)
    if (!plot) return '按 E 打开农田'

    const crop = getCropDefinition(plot.cropId)
    if (!crop) return '按 E 查看农田'
    if (isFarmPlotMature(plot)) return `按 E 收获${crop.label}`

    return `${crop.label}成长中 ${getCropStage(plot) + 1}/${crop.frames.length}`
  }

  private refreshFarmCrops() {
    const state = loadTownState()

    this.farmPlots.forEach(plot => {
      const plotState = getFarmPlotState(state, plot.id)
      const existing = this.cropSprites.get(plot.id)

      if (!plotState) {
        existing?.destroy()
        this.cropSprites.delete(plot.id)
        return
      }

      const crop = getCropDefinition(plotState.cropId)
      if (!crop) {
        existing?.destroy()
        this.cropSprites.delete(plot.id)
        return
      }

      const textureKey = CROP_TEXTURE_KEY_BY_ID[crop.texture]
      const frame = crop.frames[getCropStage(plotState)]
      if (existing) {
        if (existing.texture.key !== textureKey) {
          existing.setTexture(textureKey, frame)
        } else {
          existing.setFrame(frame)
        }
        return
      }

      // Farm plots come from the Tiled object layer; this sprite is only the crop overlay.
      const sprite = this.add.image(plot.x, plot.y, textureKey, frame)
        .setDepth(24)
        .setScale(1.12)
      this.cropSprites.set(plot.id, sprite)
    })

    this.updateInteractionLabel()
  }

  private interactFarmPlot(plot: TownFarmPlot) {
    const now = this.time.now
    if (now - this.lastEnterAt < 240) return
    this.lastEnterAt = now
    this.game.events.emit('town:interact', {
      type: 'farm',
      plotId: plot.id,
    } satisfies TownInteractEvent)
  }

  private enterBuilding(building: TownBuilding) {
    const now = this.time.now
    if (now - this.lastEnterAt < 420) return
    this.lastEnterAt = now
    this.game.events.emit('town:enter-view', {
      building,
    } satisfies TownEnterEvent)
  }

  private getObjects(map: Phaser.Tilemaps.Tilemap, layerName: string) {
    const layer = map.getObjectLayer(layerName)
    return layer?.objects ?? []
  }

  private getObjectProperty(object: TiledObject, key: string) {
    if (!object.properties) return undefined

    if (Array.isArray(object.properties)) {
      const property = object.properties.find((item: { name?: string }) => item.name === key)
      return property?.value?.toString().trim()
    }

    const value = (object.properties as Record<string, unknown>)[key]
    return value == null ? undefined : value.toString().trim()
  }

  private getNumberProperty(object: TiledObject, key: string, fallback: number) {
    const value = this.getObjectProperty(object, key)
    if (!value) return fallback

    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : fallback
  }
}

export const isTownViewKey = (value: string): value is TownViewKey =>
  ['chat', 'life', 'mood', 'resume', 'growth', 'ebti', 'plaza'].includes(value)
