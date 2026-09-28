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
  DownloadCloud,
  User,
  LogOut,
  ShieldCheck
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
  },
  operator: {
    type: Object,
    default: null
  }
})

const emit = defineEmits([
  'select-channel',
  'open-vahan-modal',
  'open-camera-modal',
  'export-csv',
  'export-pdf',
  'sign-out'
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
  <div class="h-1.5 w-full bg-gradient-to-r from-[#743E63] via-[#974A5E] via-[#BF5E65] via-[#E95350] to-[#F27951] z-50"></div>
  <header class="bg-white/92 backdrop-blur-xl border-b border-[#743E63]/25 shadow-md sticky top-0 z-40 transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Brand Identity -->
      <div class="flex items-center space-x-3">
        <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-stone-900 shadow-md border border-[#974A5E]/80">
          <img src="/AVNIT.png" alt="AVNIT Logo" class="w-7 h-7 object-contain drop-shadow" />
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-base font-black text-stone-900 tracking-tight font-sans">A.V.N.I.T.</h1>
            <span class="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
              <span>OPERATIONAL</span>
            </span>
          </div>
          <p class="text-[11px] text-stone-600 font-medium tracking-wide">Autonomous Vehicle Identity Verification</p>
        </div>
      </div>

      <!-- Center: Shift Clock & Camera Channel Selector -->
      <div class="hidden md:flex items-center space-x-4">
        
        <!-- Live Shift Clock -->
        <div class="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-stone-100/90 border border-stone-300 text-stone-800 shadow-inner">
          <Clock class="w-3.5 h-3.5 text-stone-600" />
          <span class="text-xs font-mono font-bold tracking-wider">{{ currentTime }} IST</span>
        </div>

        <!-- Camera Channel Selector -->
        <div class="relative flex items-center">
          <div class="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-white border border-stone-300 shadow-sm hover:border-stone-400 transition-colors">
            <Radio class="w-3.5 h-3.5" :class="isStreaming ? 'text-emerald-700 animate-pulse' : 'text-stone-400'" />
            <select
              :value="selectedChannelId"
              @change="emit('select-channel', $event.target.value)"
              class="text-xs font-semibold text-stone-800 bg-transparent focus:outline-none cursor-pointer pr-2"
            >
              <option v-for="ch in channels" :key="ch.id" :value="ch.id">
                {{ ch.name }}
              </option>
            </select>
          </div>
        </div>

      </div>

      <!-- Right Action Controls (Executive Zero-Blue Stone/Emerald/Amber) -->
      <div class="flex items-center space-x-2.5">

        <!-- Connect IP Camera Button -->
        <button
          @click="emit('open-camera-modal')"
          type="button"
          class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 transition-colors shadow-sm cursor-pointer"
        >
          <Video class="w-3.5 h-3.5 text-stone-600" />
          <span class="hidden sm:inline">Connect Camera</span>
        </button>

        <!-- VAHAN Registry Button -->
        <button
          @click="emit('open-vahan-modal')"
          type="button"
          class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 transition-colors shadow-sm cursor-pointer"
        >
          <Database class="w-3.5 h-3.5 text-stone-600" />
          <span class="hidden sm:inline">VAHAN DB</span>
        </button>

        <!-- Export Audit Dossier Dropdown -->
        <div class="relative">
          <button
            @click="showExportMenu = !showExportMenu"
            type="button"
            class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-black bg-gradient-to-r from-[#974A5E] via-[#E95350] to-[#F27951] hover:brightness-105 active:scale-[0.98] text-white shadow-md shadow-[#703A40]/30 transition-all focus:outline-none cursor-pointer"
          >
            <DownloadCloud class="w-3.5 h-3.5 text-white" />
            <span>Export</span>
            <ChevronDown class="w-3 h-3 text-white/80" />
          </button>

          <!-- Dropdown Menu -->
          <div
            v-if="showExportMenu"
            class="absolute right-0 mt-2 w-48 rounded-xl bg-white border border-stone-300 shadow-2xl py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-150"
          >
            <button
              @click="handleExportCSV"
              type="button"
              class="w-full text-left px-3.5 py-2 text-xs font-semibold text-stone-800 hover:bg-stone-100 flex items-center space-x-2 transition-colors cursor-pointer"
            >
              <FileSpreadsheet class="w-4 h-4 text-emerald-700" />
              <div>
                <div class="font-bold text-stone-900">CSV Audit Data</div>
                <div class="text-[10px] text-stone-500 font-normal">Raw tabular spreadsheet</div>
              </div>
            </button>
            <button
              @click="handleExportPDF"
              type="button"
              class="w-full text-left px-3.5 py-2 text-xs font-semibold text-stone-800 hover:bg-stone-100 flex items-center space-x-2 transition-colors border-t border-stone-200 cursor-pointer"
            >
              <FileText class="w-4 h-4 text-rose-700" />
              <div>
                <div class="font-bold text-stone-900">PDF Law Dossier</div>
                <div class="text-[10px] text-stone-500 font-normal">Formatted official dossier</div>
              </div>
            </button>
          </div>
        </div>

        <!-- Operator Badge / Logout Pill -->
        <div v-if="operator" class="flex items-center space-x-2 pl-2 border-l border-stone-300">
          <div class="hidden xl:flex flex-col text-right">
            <span class="text-xs font-bold text-stone-900 truncate max-w-[130px]">{{ operator.displayName }}</span>
            <span class="text-[10px] text-stone-500 font-mono">{{ operator.serialNumber || 'OFFICER' }}</span>
          </div>
          <button
            @click="emit('sign-out')"
            title="Sign out of Command Center"
            class="p-2 rounded-xl bg-stone-100 hover:bg-rose-100 text-stone-700 hover:text-rose-800 border border-stone-300 hover:border-rose-300 transition-colors shadow-sm cursor-pointer"
          >
            <LogOut class="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

    </div>
  </header>
</template>
