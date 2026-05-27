<script setup lang="ts">
import { ref } from 'vue'

import ChatView from './views/ChatView.vue'
import LifeRecordView from './views/LifeRecordView.vue'
import MoodCalendarView from './views/MoodCalendarView.vue'

const activeView = ref<'chat' | 'life' | 'mood' | 'ebti'>('chat')
</script>

<template>
  <div>
    <nav class="fixed right-4 top-4 z-50 flex gap-2 rounded-full bg-white/90 p-1 shadow">
      <button
        :class="['px-4 py-2 rounded-full text-sm', activeView === 'chat' ? 'bg-sky-600 text-white' : 'text-slate-600']"
        @click="activeView = 'chat'"
      >
        和小曦对话
      </button>
      <button
        :class="['px-4 py-2 rounded-full text-sm', activeView === 'life' ? 'bg-stone-800 text-white' : 'text-slate-600']"
        @click="activeView = 'life'"
      >
        生活记录
      </button>
      <button
        :class="['px-4 py-2 rounded-full text-sm', activeView === 'mood' ? 'bg-emerald-700 text-white' : 'text-slate-600']"
        @click="activeView = 'mood'"
      >
        心情日历
      </button>
      <button
        :class="['px-4 py-2 rounded-full text-sm', activeView === 'ebti' ? 'bg-amber-500 text-white' : 'text-slate-600 hover:bg-amber-100 hover:text-amber-800']"
        @click="activeView = 'ebti'"
      >
        EBTI 测试
      </button>
    </nav>

    <ChatView v-if="activeView === 'chat'" />
    <LifeRecordView v-else-if="activeView === 'life'" />
    <MoodCalendarView v-else-if="activeView === 'mood'" />
    <main v-else class="h-screen bg-[#0f172a] pt-16">
      <iframe
        src="/ebti-test/index.html"
        title="EBTI 测试"
        class="h-full w-full border-0"
      ></iframe>
    </main>
  </div>
</template>
