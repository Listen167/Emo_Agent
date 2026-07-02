export type TownViewKey = 'chat' | 'life' | 'mood' | 'resume' | 'growth' | 'ebti' | 'plaza'

export interface TownBuilding {
  id: string
  name: string
  view: TownViewKey
  x: number
  y: number
  accent: number
}

// Navigation map for the town. Move buildings here; App.vue only receives the target view.
export const townBuildings: TownBuilding[] = [
  {
    id: 'chat',
    name: '小曦的家',
    view: 'chat',
    x: 230,
    y: 168,
    accent: 0xc85a54,
  },
  {
    id: 'resume',
    name: '简历工坊',
    view: 'resume',
    x: 540,
    y: 160,
    accent: 0x3a524e,
  },
  {
    id: 'life',
    name: '胶片仓库',
    view: 'life',
    x: 214,
    y: 430,
    accent: 0xe8c36c,
  },
  {
    id: 'plaza',
    name: '小镇广场',
    view: 'plaza',
    x: 560,
    y: 424,
    accent: 0x6f91a8,
  },
  {
    id: 'growth',
    name: '成长档案馆',
    view: 'growth',
    x: 842,
    y: 260,
    accent: 0x87a777,
  },
  {
    id: 'ebti',
    name: '我的暗房',
    view: 'ebti',
    x: 834,
    y: 508,
    accent: 0x9a7aa8,
  },
  {
    id: 'mood',
    name: '心情花园',
    view: 'mood',
    x: 400,
    y: 540,
    accent: 0xd9894d,
  },
]
