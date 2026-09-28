<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  Video,
  Database,
  FileSpreadsheet,
  FileText,
  Clock,
  Radio,
  ChevronDown,
  DownloadCloud
} from 'lucide-vue-next'

const props = defineProps({
  channels: {
    type: Array,
    default: () => []
  },
  selectedChannelId: {
    type: String,
    default: 'cam-01'
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  fps: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'select-channel',
  'open-vahan-modal',
  'open-camera-modal',
  'export-csv',
  'export-pdf'
])

// Live Shift Clock
const currentTime = ref('')
let timer = null

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Export Dropdown State
const showExportMenu = ref(false)

const handleExportCSV = () => {
  showExportMenu.value = false
  emit('export-csv')
}

const handleExportPDF = () => {
  showExportMenu.value = false
  emit('export-pdf')
}

onMounted(() => {
  updateClock()
  timer = setInterval(updateClock, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <header class="bg-white/90 backdrop-blur-md border-b border-zinc-200/90 shadow-sm sticky top-0 z-40 transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Brand Identity -->
      <div class="flex items-center space-x-3">
        <div class="relative flex items-center justify-center w-10 h-10 rounded-lg bg-zinc-900 shadow-sm border border-zinc-700/50">
          <img src="/AVNIT.png" alt="AVNIT Logo" class="w-7 h-7 object-contain drop-shadow" />
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-base font-bold text-zinc-900 tracking-tight font-sans">A.V.N.I.T.</h1>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70">
              OPERATIONAL
            </span>
          </div>
          <p class="text-[11px] text-zinc-500 font-medium tracking-wide">Automated Vehicle Identity & Tampering Detection</p>
        </div>
      </div>

      <!-- Center: Shift Clock & Camera Channel Selector -->
      <div class="hidden md:flex items-center space-x-4">
        
        <!-- Live Shift Clock -->
        <div class="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-zinc-100/80 border border-zinc-200/80 text-zinc-700">
          <Clock class="w-3.5 h-3.5 text-zinc-500" />
          <span class="text-xs font-mono font-semibold tracking-wider">{{ currentTime }} IST</span>
        </div>

        <!-- Camera Channel Selector -->
        <div class="relative flex items-center">
          <div class="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-white border border-zinc-300 shadow-sm hover:border-zinc-400 transition-colors">
            <Radio class="w-3.5 h-3.5" :class="isStreaming ? 'text-emerald-600 animate-pulse' : 'text-zinc-400'" />
            <select
              :value="selectedChannelId"
              @change="emit('select-channel', $event.target.value)"
              class="text-xs font-semibold text-zinc-800 bg-transparent focus:outline-none cursor-pointer pr-2"
            >
              <option v-for="ch in channels" :key="ch.id" :value="ch.id">
                {{ ch.name }}
              </option>
            </select>
          </div>
        </div>

      </div>

      <!-- Right Action Controls (Executive Zero-Blue Onyx/Emerald) -->
      <div class="flex items-center space-x-2.5">

        <!-- Connect IP Camera Button -->
        <button
          @click="emit('open-camera-modal')"
          type="button"
          class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-zinc-100 hover:bg-zinc-200 text-zinc-800 border border-zinc-300 transition-colors shadow-sm"
        >
          <Video class="w-3.5 h-3.5 text-zinc-600" />
          <span class="hidden sm:inline">Connect IP Camera</span>
        </button>

        <!-- VAHAN Registry Button -->
        <button
          @click="emit('open-vahan-modal')"
          type="button"
          class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-zinc-100 hover:bg-zinc-200 text-zinc-800 border border-zinc-300 transition-colors shadow-sm"
        >
          <Database class="w-3.5 h-3.5 text-zinc-600" />
          <span class="hidden sm:inline">VAHAN Registry</span>
        </button>

        <!-- Export Audit Dossier Dropdown -->
        <div class="relative">
          <button
            @click="showExportMenu = !showExportMenu"
            type="button"
            class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-zinc-900 hover:bg-zinc-800 text-white shadow-sm transition-all focus:outline-none"
          >
            <DownloadCloud class="w-3.5 h-3.5 text-zinc-200" />
            <span>Export Report</span>
            <ChevronDown class="w-3 h-3 text-zinc-400" />
          </button>

          <!-- Dropdown Menu -->
          <div
            v-if="showExportMenu"
            class="absolute right-0 mt-2 w-48 rounded-xl bg-white border border-zinc-200 shadow-modal py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-150"
          >
            <button
              @click="handleExportCSV"
              type="button"
              class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-700 hover:bg-zinc-50 flex items-center space-x-2 transition-colors"
            >
              <FileSpreadsheet class="w-4 h-4 text-emerald-600" />
              <div>
                <div class="font-semibold text-zinc-800">CSV Audit Data</div>
                <div class="text-[10px] text-zinc-400">Raw tabular spreadsheet</div>
              </div>
            </button>
            <button
              @click="handleExportPDF"
              type="button"
              class="w-full text-left px-3.5 py-2 text-xs font-medium text-zinc-700 hover:bg-zinc-50 flex items-center space-x-2 transition-colors border-t border-zinc-100"
            >
              <FileText class="w-4 h-4 text-rose-600" />
              <div>
                <div class="font-semibold text-zinc-800">PDF Law Dossier</div>
                <div class="text-[10px] text-zinc-400">Formatted official evidence</div>
              </div>
            </button>
          </div>
        </div>

      </div>

    </div>
  </header>
</template>
