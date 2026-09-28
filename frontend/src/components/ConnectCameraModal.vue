<script setup>
import { ref } from 'vue'
import {
  X,
  Video,
  Radio,
  Download,
  Terminal,
  ShieldCheck,
  Cpu,
  Layers,
  Check
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'connect-rtsp'])

const activeTab = ref('rtsp') // 'rtsp' or 'edge'
const cameraName = ref('NH-48 Toll Lane 4')
const rtspUrl = ref('rtsp://admin:pass@192.168.1.100:554/ch1')
const location = ref('NH-48 Gurgaon Expressway KM 28')

const isCopied = ref(false)

const handleConnect = () => {
  if (!rtspUrl.value.trim()) {
    alert('Please enter a valid RTSP stream URL.')
    return
  }
  emit('connect-rtsp', {
    name: cameraName.value.trim() || 'RTSP IP Camera',
    url: rtspUrl.value.trim(),
    location: location.value.trim() || 'Highway Checkpoint'
  })
  emit('close')
}

const copyCommand = () => {
  navigator.clipboard.writeText('python avnit_edge_agent.py --config edge_config.json')
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 2000)
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/60 backdrop-blur-sm animate-in fade-in duration-150"
  >
    <div
      class="bg-white rounded-2xl border border-zinc-200 shadow-modal w-full max-w-xl overflow-hidden animate-in zoom-in-95 duration-150"
    >
      
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-zinc-100 flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded-lg bg-zinc-900 flex items-center justify-center text-white">
            <Video class="w-4 h-4" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-zinc-900 font-sans">Roadside & Highway Camera Integration</h3>
            <p class="text-[11px] text-zinc-500">Connect live surveillance streams or deploy field agents</p>
          </div>
        </div>

        <button
          @click="emit('close')"
          type="button"
          class="p-1 rounded-lg text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex border-b border-zinc-200 bg-zinc-50/70 px-6">
        <button
          @click="activeTab = 'rtsp'"
          type="button"
          class="py-3 px-3 text-xs font-semibold border-b-2 transition-all"
          :class="activeTab === 'rtsp'
            ? 'border-zinc-900 text-zinc-900'
            : 'border-transparent text-zinc-500 hover:text-zinc-800'"
        >
          Method 1: Direct RTSP Stream
        </button>
        <button
          @click="activeTab = 'edge'"
          type="button"
          class="py-3 px-3 text-xs font-semibold border-b-2 transition-all"
          :class="activeTab === 'edge'
            ? 'border-zinc-900 text-zinc-900'
            : 'border-transparent text-zinc-500 hover:text-zinc-800'"
        >
          Method 2: Autonomous Roadside Edge Agent
        </button>
      </div>

      <!-- Tab 1: Direct RTSP Stream Input -->
      <div v-if="activeTab === 'rtsp'" class="p-6 space-y-4">
        <div>
          <label class="block text-xs font-semibold text-zinc-700 mb-1">Camera Identifier Name</label>
          <input
            v-model="cameraName"
            type="text"
            placeholder="e.g. NH-48 Toll Lane 4"
            class="w-full text-xs px-3.5 py-2 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500 text-zinc-800 placeholder:text-zinc-400"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-zinc-700 mb-1">RTSP Stream URL / ONVIF Endpoint</label>
          <input
            v-model="rtspUrl"
            type="text"
            placeholder="rtsp://admin:password@192.168.1.50:554/live"
            class="w-full text-xs font-mono px-3.5 py-2 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500 text-zinc-800 placeholder:text-zinc-400"
          />
          <p class="text-[10px] text-zinc-400 mt-1">Supports H.264 / H.265 streams from Hikvision, Dahua, Axis, and Hanwha cameras.</p>
        </div>

        <div>
          <label class="block text-xs font-semibold text-zinc-700 mb-1">Physical Pole / Highway Location</label>
          <input
            v-model="location"
            type="text"
            placeholder="e.g. NH-48 Gurgaon Expressway KM 28"
            class="w-full text-xs px-3.5 py-2 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500 text-zinc-800 placeholder:text-zinc-400"
          />
        </div>

        <div class="pt-2 flex items-center justify-end space-x-2">
          <button
            @click="emit('close')"
            type="button"
            class="px-4 py-2 rounded-lg text-xs font-medium text-zinc-600 hover:bg-zinc-100 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleConnect"
            type="button"
            class="px-4 py-2 rounded-lg text-xs font-semibold bg-zinc-900 hover:bg-zinc-800 text-white shadow-sm transition-colors"
          >
            Connect Camera Stream
          </button>
        </div>
      </div>

      <!-- Tab 2: Autonomous Roadside Edge Agent -->
      <div v-else class="p-6 space-y-4">
        
        <div class="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 text-xs text-zinc-700 space-y-2">
          <div class="flex items-center space-x-2 font-bold text-zinc-900">
            <Cpu class="w-4 h-4 text-emerald-600" />
            <span>Low-Bandwidth Highway Deployment</span>
          </div>
          <p class="text-[11px] text-zinc-600 leading-relaxed">
            Deploy this autonomous agent on roadside pole PCs (NVIDIA Jetson, Industrial IPCs, or Raspberry Pi 5).
            Inference executes locally; only <strong>2 KB JSON telemetry events</strong> are transmitted over cellular backhauls,
            with high-risk tamper evidence snapshots attached automatically.
          </p>
        </div>

        <!-- Download Buttons -->
        <div class="grid grid-cols-2 gap-3 pt-1">
          <a
            href="/api/edge/agent-script"
            download="avnit_edge_agent.py"
            class="flex items-center justify-center space-x-2 px-3.5 py-2.5 rounded-lg text-xs font-semibold bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-800 shadow-sm transition-colors text-center"
          >
            <Download class="w-4 h-4 text-emerald-600" />
            <span>Download Agent (.py)</span>
          </a>

          <a
            href="/api/edge/default-config"
            download="edge_config.json"
            class="flex items-center justify-center space-x-2 px-3.5 py-2.5 rounded-lg text-xs font-semibold bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-800 shadow-sm transition-colors text-center"
          >
            <Download class="w-4 h-4 text-amber-600" />
            <span>Download Config (.json)</span>
          </a>
        </div>

        <!-- Quick Start Command Block -->
        <div>
          <div class="flex items-center justify-between text-[11px] font-semibold text-zinc-500 mb-1">
            <span>Terminal Execution Command</span>
            <button
              @click="copyCommand"
              type="button"
              class="text-emerald-700 hover:underline flex items-center space-x-1"
            >
              <Check v-if="isCopied" class="w-3 h-3 text-emerald-600" />
              <span>{{ isCopied ? 'Copied' : 'Copy' }}</span>
            </button>
          </div>
          <div class="p-3 bg-zinc-900 text-zinc-100 rounded-lg font-mono text-xs flex items-center justify-between">
            <code>python avnit_edge_agent.py --config edge_config.json</code>
          </div>
        </div>

        <div class="pt-2 flex justify-end">
          <button
            @click="emit('close')"
            type="button"
            class="px-4 py-2 rounded-lg text-xs font-semibold bg-zinc-900 hover:bg-zinc-800 text-white transition-colors"
          >
            Done
          </button>
        </div>

      </div>

    </div>
  </div>
</template>
