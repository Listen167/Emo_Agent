<script setup lang="ts">
import { ref } from 'vue'

import ChatView from './views/ChatView.vue'
import LifeRecordView from './views/LifeRecordView.vue'

const activeView = ref<'chat' | 'life'>('chat')
</script>

<template>
  <div>
    <nav class="fixed right-4 top-4 z-50 flex gap-2 rounded-full bg-white/90 p-1 shadow">
      <button
        :class="['px-4 py-2 rounded-full text-sm', activeView === 'chat' ? 'bg-sky-600 text-white' : 'text-slate-600']"
        @click="activeView = 'chat'"
      >
        对话
      </button>
      <button
        :class="['px-4 py-2 rounded-full text-sm', activeView === 'life' ? 'bg-stone-800 text-white' : 'text-slate-600']"
        @click="activeView = 'life'"
      >
        生活记录
      </button>
    </nav>
    <ChatView v-if="activeView === 'chat'" />
    <LifeRecordView v-else />
  </div>
</template>
