<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Play,
  Square,
  Moon,
  Sun,
  Camera,
  Upload,
  Sparkles,
  Maximize2
} from 'lucide-vue-next'
import { usePixiOverlay } from '../composables/usePixiOverlay'

const props = defineProps({
  currentFrame: {
    type: String,
    default: null
  },
  telemetry: {
    type: Array,
    default: () => []
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  isNightMode: {
    type: Boolean,
    default: false
  },
  fps: {
    type: Number,
    default: 0
  },
  activeChannel: {
    type: Object,
    default: () => ({ name: 'Camera Feed', location: 'Toll Checkpoint' })
  }
})

const emit = defineEmits(['start-stream', 'stop-stream', 'override-plate', 'upload-video'])

const pixiCanvas = ref(null)
const playerContainer = ref(null)
const simulatedPlateInput = ref('')
const { initPixi, updateOverlay, resizePixi, destroyPixi } = usePixiOverlay()

let resizeObserver = null

const handleToggleStream = () => {
  if (props.isStreaming) {
    emit('stop-stream')
  } else {
    emit('start-stream')
  }
}

const handleOverrideSubmit = () => {
  emit('override-plate', simulatedPlateInput.value.trim().toUpperCase())
}

const handleFileUpload = (e) => {
  const file = e.target.files?.[0]
  if (file) {
    emit('upload-video', file)
  }
}

// Watch incoming telemetry and trigger PixiJS WebGL canvas redraw
watch(
  () => props.telemetry,
  (newTelemetry) => {
    if (props.isStreaming && newTelemetry) {
      updateOverlay(newTelemetry, 640, 360)
    }
  },
  { deep: true }
)

watch(
  () => props.isStreaming,
  (streaming) => {
    if (!streaming) {
      updateOverlay([])
    }
  }
)

onMounted(async () => {
  await nextTick()
  if (pixiCanvas.value && playerContainer.value) {
    const rect = playerContainer.value.getBoundingClientRect()
    initPixi(pixiCanvas.value, rect.width, rect.height)

    resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect
        if (width && height) {
          resizePixi(width, height)
        }
      }
    })
    resizeObserver.observe(playerContainer.value)
  }
})

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect()
  destroyPixi()
})
</script>

<template>
  <div class="bg-white/92 backdrop-blur-xl rounded-2xl border border-[#743E63]/25 shadow-xl overflow-hidden flex flex-col relative">
    <div class="h-1 w-full bg-gradient-to-r from-[#743E63] via-[#974A5E] via-[#BF5E65] via-[#E95350] to-[#F27951]"></div>
    
    <!-- Top Player Meta Bar -->
    <div class="px-4 py-2.5 bg-stone-50/90 border-b border-stone-200/80 flex items-center justify-between">
      <div class="flex items-center space-x-2.5">
        <span class="relative flex h-2.5 w-2.5">
          <span
            v-if="isStreaming"
            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
          ></span>
          <span
            class="relative inline-flex rounded-full h-2.5 w-2.5"
            :class="isStreaming ? 'bg-emerald-600' : 'bg-zinc-400'"
          ></span>
        </span>
        <span class="text-xs font-semibold text-zinc-800 tracking-wide font-sans">
          {{ activeChannel?.name || 'Live Traffic Stream' }}
        </span>
        <span class="text-[11px] text-zinc-400">|</span>
        <span class="text-[11px] text-zinc-500 font-medium">
          {{ activeChannel?.location || 'NH-48 Corridor' }}
        </span>
      </div>

      <!-- Right Meta Badges: Night Mode & FPS -->
      <div class="flex items-center space-x-2">
        <!-- Automatic Night Mode Indicator -->
        <div
          v-if="isNightMode"
          class="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-300 animate-pulse"
        >
          <Moon class="w-3 h-3 text-amber-600" />
          <span>IR NIGHT VISION (CLAHE 3.5x)</span>
        </div>
        <div
          v-else
          class="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium bg-zinc-100 text-zinc-600 border border-zinc-200"
        >
          <Sun class="w-3 h-3 text-amber-500" />
          <span>DAYLIGHT</span>
        </div>

        <!-- FPS Counter -->
        <span class="font-mono text-[10px] font-semibold text-zinc-500 bg-zinc-100 px-2 py-0.5 rounded border border-zinc-200">
          {{ fps }} FPS
        </span>
      </div>
    </div>

    <!-- Video Canvas Viewport -->
    <div
      ref="playerContainer"
      class="relative w-full aspect-video bg-zinc-950 flex items-center justify-center overflow-hidden select-none"
    >
      <!-- Base Video Frame -->
      <img
        v-if="currentFrame"
        :src="currentFrame"
        alt="Live Camera Frame"
        class="w-full h-full object-contain pointer-events-none"
      />

      <!-- Offline / Standby State -->
      <div
        v-else
        class="flex flex-col items-center justify-center text-center p-6 text-zinc-400"
      >
        <div class="w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-3 text-zinc-500 shadow-inner">
          <Camera class="w-7 h-7" />
        </div>
        <p class="text-sm font-semibold text-zinc-200 font-sans">Stream Inactive</p>
        <p class="text-xs text-zinc-400 max-w-xs mt-1">
          Click Start Stream below to engage AI-assisted vehicle identity inspection.
        </p>
      </div>

      <!-- PixiJS WebGL HUD Overlay (Layered on top of video) -->
      <canvas
        ref="pixiCanvas"
        class="absolute inset-0 w-full h-full pointer-events-none z-10"
      ></canvas>

      <!-- Night Mode Subtle Glare Reticle (Zero Blue) -->
      <div
        v-if="isNightMode && isStreaming"
        class="absolute inset-0 pointer-events-none border border-amber-500/20 mix-blend-screen"
      ></div>
    </div>

    <!-- Video Player Control Bar -->
    <div class="px-4 py-3 bg-zinc-50/70 border-t border-zinc-200 flex flex-wrap items-center justify-between gap-3">
      
      <!-- Primary Playback Controls -->
      <div class="flex items-center space-x-2">
          <button
          @click="handleToggleStream"
          type="button"
          class="inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-black shadow-md transition-all focus:outline-none cursor-pointer"
          :class="isStreaming
            ? 'bg-rose-600 hover:bg-rose-700 text-white'
            : 'bg-gradient-to-r from-[#974A5E] via-[#E95350] to-[#F27951] hover:brightness-105 active:scale-[0.98] text-white shadow-md shadow-[#703A40]/30'"
        >
          <Square v-if="isStreaming" class="w-3.5 h-3.5 fill-current" />
          <Play v-else class="w-3.5 h-3.5 fill-current text-white" />
          <span>{{ isStreaming ? 'Halt Feed' : 'Start Feed' }}</span>
        </button>

        <!-- Custom Video File Upload -->
        <label
          class="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-white hover:bg-stone-50 text-stone-700 border border-stone-300 shadow-sm cursor-pointer transition-colors"
        >
          <Upload class="w-3.5 h-3.5 text-stone-500" />
          <span>Upload File</span>
          <input
            type="file"
            accept="video/mp4,video/avi"
            class="hidden"
            @change="handleFileUpload"
          />
        </label>
      </div>

      <!-- Plate Simulator Override Control -->
      <div class="flex items-center space-x-2">
        <div class="flex items-center bg-white border border-stone-300 rounded-xl px-2.5 py-1.5 shadow-sm focus-within:border-[#F27951] transition-colors">
          <Sparkles class="w-3.5 h-3.5 text-[#F27951] mr-2" />
          <input
            v-model="simulatedPlateInput"
            @keyup.enter="handleOverrideSubmit"
            placeholder="Override Plate (e.g. MH12DE1433)"
            class="text-xs font-mono font-semibold uppercase text-stone-800 placeholder:text-stone-400 focus:outline-none w-44 sm:w-52"
          />
        </div>
        <button
          @click="handleOverrideSubmit"
          type="button"
          class="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#F27951]/15 hover:bg-[#F27951]/25 text-[#703A40] border border-[#F27951]/40 transition-colors cursor-pointer shadow-xs"
        >
          Apply
        </button>
      </div>

    </div>

  </div>
</template>
