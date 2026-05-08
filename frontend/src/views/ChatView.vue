<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <header class="bg-white shadow p-4 flex justify-between items-center">
      <h1 class="text-xl font-bold text-blue-600">🎓 学生情感语音Agent</h1>
      <span class="text-xs text-gray-500">会话: {{ sid.slice(0,8) }}</span>
    </header>

    <div ref="container" class="flex-1 overflow-y-auto p-4 space-y-4">
      <div v-for="m in msgs" :key="m.id" :class="['flex', m.role==='user'?'justify-end':'justify-start']">
        <div :class="['max-w-[75%] p-3 rounded-xl shadow', m.role==='user'?'bg-blue-100':'bg-white']">
          <p class="text-sm whitespace-pre-wrap">{{ m.content }}</p>
          <span v-if="m.emotion_label" class="text-xs text-gray-500 mt-1 block">🎭 {{ m.emotion_label }} ({{ (m.emotion_conf*100).toFixed(0) }}%)</span>
        </div>
      </div>
    </div>

    <div class="bg-white p-4 border-t flex gap-2">
      <button @click="toggleRec" :class="['px-4 py-2 rounded-lg text-white transition', rec?'bg-red-500 animate-pulse':'bg-gray-600']">
        {{ rec?'⏹ 停止':'🎤 录音' }}
      </button>
      <input v-model="txt" placeholder="输入文字..." class="flex-1 px-4 py-2 border rounded-lg" @keyup.enter="sendTxt" />
      <button @click="sendTxt" class="px-4 py-2 bg-blue-600 text-white rounded-lg">发送</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { sendChat, getHistory } from '../api/chat';

const msgs = ref<any[]>([]);
const txt = ref('');
const rec = ref(false);
const sid = ref(localStorage.getItem('sid') || crypto.randomUUID());
const container = ref<HTMLElement>();
let recorder: MediaRecorder | null = null;
let chunks: Blob[] = [];

onMounted(() => { localStorage.setItem('sid', sid.value); loadHistory(); });

const toggleRec = async () => {
  if (!rec.value) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    recorder.ondataavailable = e => chunks.push(e.data);
    recorder.onstop = () => { const b = new Blob(chunks, { type: 'audio/webm' }); chunks=[]; submitAudio(b); };
    recorder.start(); rec.value = true;
  } else { recorder?.stop(); rec.value = false; }
};

const sendTxt = () => { if(!txt.value) return; submitText(txt.value); txt.value=''; };
const submitAudio = async (b: Blob) => { const f=new FormData(); f.append('audio', b, 'rec.webm'); f.append('session_id', sid.value); await send(f); };
const submitText = async (t: string) => { const f=new FormData(); f.append('text', t); f.append('session_id', sid.value); await send(f); };

const send = async (f: FormData) => {
  const { data } = await sendChat(f);
  msgs.value.push({ role:'user', content: f.get('text') ? String(f.get('text')) : '🎤 语音', emotion_label: data.emotion.label, emotion_conf: data.emotion.confidence });
  msgs.value.push({ role:'assistant', content: data.text });
  scrollToBottom();
};

const loadHistory = async () => {
  const { data } = await getHistory(sid.value);
  msgs.value = data.reverse();
  scrollToBottom();
};

const scrollToBottom = async () => { await nextTick(); container.value?.scrollTo({ top: container.value.scrollHeight, behavior:'smooth' }); };
</script>