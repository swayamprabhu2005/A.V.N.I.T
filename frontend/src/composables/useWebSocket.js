import { ref, onMounted, onUnmounted } from 'vue'

export function useWebSocket() {
  const isConnected = ref(false)
  const isStreaming = ref(false)
  const currentFrame = ref(null)
  const telemetry = ref([])
  const activeRisk = ref(null)
  const isNightMode = ref(false)
  const edgeAlert = ref(null)
  const fps = ref(0)

  let ws = null
  let reconnectTimeout = null
  let frameCounter = 0
  let fpsTimer = null

  const getWsUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    // If dev server on 5173, point to backend on 8000
    if (host.includes(':5173')) {
      return `${protocol}//${window.location.hostname}:8000/ws/stream`
    }
    return `${protocol}//${host}/ws/stream`
  }

  const connect = () => {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    try {
      ws = new WebSocket(getWsUrl())

      ws.onopen = () => {
        isConnected.value = true
        console.log('[AVNIT WS] Connected to backend streaming service.')
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)

          if (msg.type === 'frame') {
            currentFrame.value = msg.image
            telemetry.value = msg.telemetry || []
            frameCounter++

            // Check if any telemetry contains active vehicle risk evaluation
            if (msg.telemetry && msg.telemetry.length > 0) {
              const latest = msg.telemetry[0]
              activeRisk.value = latest.risk_result || null
              if (typeof latest.is_night_mode === 'boolean') {
                isNightMode.value = latest.is_night_mode
              }
            }
          } else if (msg.type === 'edge_telemetry') {
            edgeAlert.value = msg.data
          }
        } catch (err) {
          console.error('[AVNIT WS] Error decoding frame message:', err)
        }
      }

      ws.onclose = () => {
        isConnected.value = false
        isStreaming.value = false
        reconnectTimeout = setTimeout(connect, 2500)
      }

      ws.onerror = (err) => {
        console.error('[AVNIT WS] WebSocket error:', err)
        ws.close()
      }
    } catch (e) {
      console.error('[AVNIT WS] Failed to initiate connection:', e)
      reconnectTimeout = setTimeout(connect, 3000)
    }
  }

  const startStream = (channel, simulatedPlate = null) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      connect()
    }

    const payload = {
      action: 'start',
      source: channel.type,
      filename: channel.filename || '',
      rtsp_url: channel.rtsp_url || '',
      simulated_plate: simulatedPlate
    }

    const sendStart = () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(payload))
        isStreaming.value = true
      } else {
        setTimeout(sendStart, 200)
      }
    }

    sendStart()
  }

  const stopStream = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: 'stop' }))
    }
    isStreaming.value = false
    currentFrame.value = null
    telemetry.value = []
  }

  const overridePlate = (plateText) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        action: 'override_plate',
        plate: plateText || null
      }))
    }
  }

  onMounted(() => {
    connect()
    fpsTimer = setInterval(() => {
      fps.value = frameCounter
      frameCounter = 0
    }, 1000)
  })

  onUnmounted(() => {
    if (fpsTimer) clearInterval(fpsTimer)
    if (reconnectTimeout) clearTimeout(reconnectTimeout)
    if (ws) {
      ws.close()
    }
  })

  return {
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
  }
}
