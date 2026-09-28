<script setup>
import { ref, onMounted, watch } from 'vue'
import HomePage from './views/HomePage.vue'
import AppHeader from './components/AppHeader.vue'
import VideoPlayer from './components/VideoPlayer.vue'
import RiskGauge from './components/RiskGauge.vue'
import AttributeMatrix from './components/AttributeMatrix.vue'
import DetectionHistory from './components/DetectionHistory.vue'
import ConnectCameraModal from './components/ConnectCameraModal.vue'
import VehicleModal from './components/VehicleModal.vue'
import StatusBanner from './components/StatusBanner.vue'

import { useCameraChannels } from './composables/useCameraChannels'
import { useWebSocket } from './composables/useWebSocket'
import { useExportReports } from './composables/useExportReports'
import { getSavedOperator, signOutOperator } from './services/firebase'

// Operator Authentication Session State
const currentOperator = ref(getSavedOperator())

const handleLoginSuccess = (user) => {
  currentOperator.value = user
  fetchAlerts()
  fetchStats()
  startStream(getSelectedChannel())
}

const handleSignOut = async () => {
  stopStream()
  await signOutOperator()
  currentOperator.value = null
}

// Composables
const { channels, selectedChannelId, getSelectedChannel, addRTSPChannel } = useCameraChannels()
const {
  isConnected,
  isStreaming,
  currentFrame,
  telemetry,
  activeRisk,
  isNightMode,
  edgeAlert,
  fps,
  startStream,
  stopStream,
  overridePlate
} = useWebSocket()
const { exportToCSV, exportToPDF } = useExportReports()

// UI Modal States
const isCameraModalOpen = ref(false)
const isVahanModalOpen = ref(false)
const isAlertBannerVisible = ref(true)

// History & Stats
const alertsList = ref([])
const stats = ref({})

// Fetch alerts history from SQLite database
const fetchAlerts = async () => {
  try {
    const res = await fetch('/api/alerts?limit=100')
    if (res.ok) {
      alertsList.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to fetch alerts:', e)
  }
}

const fetchStats = async () => {
  try {
    const res = await fetch('/api/stats')
    if (res.ok) {
      stats.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  }
}

// Handlers
const handleSelectChannel = (channelId) => {
  selectedChannelId.value = channelId
  const ch = getSelectedChannel()
  if (isStreaming.value) {
    startStream(ch)
  }
}

const handleStartStream = () => {
  startStream(getSelectedChannel())
}

const handleStopStream = () => {
  stopStream()
}

const handleOverridePlate = (plate) => {
  overridePlate(plate)
}

const handleConnectRTSP = (cameraData) => {
  const newId = addRTSPChannel(cameraData.name, cameraData.url, cameraData.location)
  startStream(getSelectedChannel())
}

const handleUploadVideo = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await fetch('/api/upload-video', {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      const data = await res.json()
      channels.value.push({
        id: `upload-${Date.now()}`,
        name: `Uploaded: ${file.name}`,
        type: 'scenario',
        filename: data.filename,
        location: 'Custom Inspection Clip',
        status: 'ONLINE'
      })
      selectedChannelId.value = channels.value[channels.value.length - 1].id
      startStream(getSelectedChannel())
    }
  } catch (e) {
    alert('Failed to upload video clip.')
  }
}

// Watch edge alert pings from roadside poles
watch(
  () => edgeAlert.value,
  (newAlert) => {
    if (newAlert) {
      isAlertBannerVisible.value = true
      fetchAlerts()
      fetchStats()
    }
  }
)

// Watch active risk to refresh alerts feed periodically
watch(
  () => activeRisk.value,
  (newRisk) => {
    if (newRisk) {
      isAlertBannerVisible.value = true
      fetchAlerts()
      fetchStats()
    }
  }
)

onMounted(() => {
  if (currentOperator.value) {
    fetchAlerts()
    fetchStats()
    startStream(getSelectedChannel())
  }
})
</script>

<template>
  <!-- 1. Home & Authentication Portal (Shown if not signed in) -->
  <HomePage
    v-if="!currentOperator"
    @login-success="handleLoginSuccess"
  />

  <!-- 2. Live Command Center Dashboard (Shown once authenticated) -->
  <div v-else class="min-h-screen bg-gradient-to-r from-[#be123c] via-[#d97706] to-[#fbbf24] text-stone-900 flex flex-col font-sans selection:bg-rose-200 selection:text-rose-950 relative">
    
    <!-- Subtle Ambient Dark Film (Maintains High-Contrast Readability) -->
    <div class="fixed inset-0 bg-stone-950/12 pointer-events-none z-0"></div>

    <!-- Top Executive Header -->
    <AppHeader
      :channels="channels"
      :selected-channel-id="selectedChannelId"
      :is-streaming="isStreaming"
      :fps="fps"
      :operator="currentOperator"
      @select-channel="handleSelectChannel"
      @open-camera-modal="isCameraModalOpen = true"
      @open-vahan-modal="isVahanModalOpen = true"
      @export-csv="exportToCSV(alertsList)"
      @export-pdf="exportToPDF(alertsList, stats)"
      @sign-out="handleSignOut"
    />

    <!-- Main Content Container with Warm Ambient Gradients (Zero Blue) -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 relative z-10">

      <!-- Dynamic High-Risk Status Banner -->
      <StatusBanner
        :risk-result="activeRisk"
        :visible="isAlertBannerVisible"
        @dismiss="isAlertBannerVisible = false"
      />

      <!-- Operational Grid Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left Column: Video Player & Chronological Audit Feed (7 cols) -->
        <div class="lg:col-span-7 space-y-6">
          
          <!-- PixiJS Video Stream Player -->
          <VideoPlayer
            :current-frame="currentFrame"
            :telemetry="telemetry"
            :is-streaming="isStreaming"
            :is-night-mode="isNightMode"
            :fps="fps"
            :active-channel="getSelectedChannel()"
            @start-stream="handleStartStream"
            @stop-stream="handleStopStream"
            @override-plate="handleOverridePlate"
            @upload-video="handleUploadVideo"
          />

          <!-- Audit Detection History Feed -->
          <DetectionHistory
            :alerts="alertsList"
            @export-csv="exportToCSV(alertsList)"
            @export-pdf="exportToPDF(alertsList, stats)"
            @select-alert="(alert) => activeRisk = alert"
          />

        </div>

        <!-- Right Column: Bayesian Risk Gauge & Attribute Matrix (5 cols) -->
        <div class="lg:col-span-5 space-y-6">

          <!-- Radial Risk Gauge with Physics Animation -->
          <RiskGauge
            :risk-result="activeRisk"
            :is-night-mode="isNightMode"
          />

          <!-- Side-by-Side Visual Attribute Cross-Verification Matrix & Snapshot Evidence -->
          <AttributeMatrix
            :telemetry="telemetry?.[0]"
            :risk-result="activeRisk"
          />

        </div>

      </div>

    </main>

    <!-- Connect Camera / Download Edge Agent Modal -->
    <ConnectCameraModal
      :is-open="isCameraModalOpen"
      @close="isCameraModalOpen = false"
      @connect-rtsp="handleConnectRTSP"
    />

    <!-- VAHAN Database CRUD Management Modal -->
    <VehicleModal
      :is-open="isVahanModalOpen"
      @close="isVahanModalOpen = false"
      @refresh="fetchAlerts"
    />

  </div>
</template>
