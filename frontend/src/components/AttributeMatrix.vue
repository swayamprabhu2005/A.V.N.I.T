<script setup>
import { computed } from 'vue'
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Car,
  Palette,
  CreditCard,
  Shield,
  Layers
} from 'lucide-vue-next'

const props = defineProps({
  telemetry: {
    type: Object,
    default: null
  },
  riskResult: {
    type: Object,
    default: null
  }
})

// Observed values from computer vision models
const observed = computed(() => {
  return {
    plate: props.telemetry?.plate_number || 'UNKNOWN',
    type: props.telemetry?.vehicle_type || 'N/A',
    color: props.telemetry?.observed_color || 'N/A',
    confidence: props.telemetry?.ocr_confidence
      ? Math.round(props.telemetry.ocr_confidence * 100)
      : 95
  }
})

// Registered values from VAHAN database
const registered = computed(() => {
  const reg = props.riskResult?.registered_details
  if (!reg) {
    return {
      exists: false,
      plate: 'NOT FOUND IN REGISTRY',
      type: 'N/A',
      color: 'N/A',
      makeModel: 'N/A',
      status: 'Unregistered'
    }
  }
  return {
    exists: true,
    plate: reg.plate_number || 'N/A',
    type: reg.vehicle_type || 'N/A',
    color: reg.color || 'N/A',
    makeModel: `${reg.make || ''} ${reg.model || ''}`.trim() || 'N/A',
    status: reg.registration_status || 'Active'
  }
})

// Match status helpers
const factors = computed(() => props.riskResult?.factors || {})

const typeMatch = computed(() => {
  if (!registered.value.exists) return 'mismatch'
  return factors.value.type_matched !== false ? 'match' : 'mismatch'
})

const colorMatch = computed(() => {
  if (!registered.value.exists) return 'mismatch'
  const score = factors.value.score_color ?? 1.0
  if (score >= 0.8) return 'match'
  if (score >= 0.5) return 'variance'
  return 'mismatch'
})

const statusMatch = computed(() => {
  if (!registered.value.exists) return 'mismatch'
  return registered.value.status.toLowerCase() === 'active' ? 'match' : 'mismatch'
})

// Map color names to CSS preview backgrounds (Zero Blue)
const getColorDot = (colorName) => {
  const c = (colorName || '').toLowerCase()
  switch (c) {
    case 'white': return '#ffffff'
    case 'black': return '#18181b'
    case 'silver':
    case 'gray':
    case 'grey': return '#9ca3af'
    case 'red': return '#dc2626'
    case 'maroon': return '#800000'
    case 'yellow': return '#eab308'
    case 'orange': return '#ea580c'
    case 'green': return '#16a34a'
    case 'brown': return '#78350f'
    case 'beige': return '#f5f5dc'
    default: return '#71717a'
  }
}
</script>

<template>
  <div class="bg-white rounded-xl border border-zinc-200/90 shadow-card p-5">
    
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-zinc-100 pb-3">
      <div>
        <h2 class="text-xs font-bold uppercase tracking-wider text-zinc-500">Identity Cross-Verification</h2>
        <p class="text-sm font-bold text-zinc-900 font-sans">Observed Visuals vs. Registered Record</p>
      </div>

      <div class="flex items-center space-x-2">
        <span
          class="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-[11px] font-semibold"
          :class="registered.exists
            ? 'bg-zinc-100 text-zinc-800 border border-zinc-300'
            : 'bg-rose-50 text-rose-700 border border-rose-200'"
        >
          <Layers class="w-3 h-3 text-zinc-500" />
          <span>{{ registered.exists ? 'Registry Synced' : 'Unregistered Plate' }}</span>
        </span>
      </div>
    </div>

    <!-- Attribute Comparison Table -->
    <div class="mt-4 divide-y divide-zinc-100">

      <!-- 1. License Plate Number -->
      <div class="py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2.5 w-1/3">
          <CreditCard class="w-4 h-4 text-zinc-500" />
          <span class="text-xs font-semibold text-zinc-700">License Plate</span>
        </div>

        <div class="w-1/3 text-left">
          <div class="text-xs font-mono font-bold text-zinc-900 tracking-wider">
            {{ observed.plate.toUpperCase() }}
          </div>
          <span class="text-[10px] text-zinc-400 font-medium">OCR Conf: {{ observed.confidence }}%</span>
        </div>

        <div class="w-1/3 flex items-center justify-end space-x-2">
          <div class="text-xs font-mono font-bold text-zinc-800 tracking-wider text-right">
            {{ registered.plate.toUpperCase() }}
          </div>
          <CheckCircle2 v-if="registered.exists" class="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <XCircle v-else class="w-4 h-4 text-rose-600 flex-shrink-0" />
        </div>
      </div>

      <!-- 2. Vehicle Classification -->
      <div class="py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2.5 w-1/3">
          <Car class="w-4 h-4 text-zinc-500" />
          <span class="text-xs font-semibold text-zinc-700">Vehicle Type</span>
        </div>

        <div class="w-1/3 text-left">
          <span class="text-xs font-semibold text-zinc-900 capitalize">
            {{ observed.type }}
          </span>
          <div class="text-[10px] text-zinc-400">YOLOv8 Detection</div>
        </div>

        <div class="w-1/3 flex items-center justify-end space-x-2">
          <span class="text-xs font-semibold text-zinc-800 capitalize text-right">
            {{ registered.type }}
          </span>
          <CheckCircle2 v-if="typeMatch === 'match'" class="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <XCircle v-else class="w-4 h-4 text-rose-600 flex-shrink-0" />
        </div>
      </div>

      <!-- 3. Exterior Body Color -->
      <div class="py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2.5 w-1/3">
          <Palette class="w-4 h-4 text-zinc-500" />
          <span class="text-xs font-semibold text-zinc-700">Vehicle Color</span>
        </div>

        <div class="w-1/3 text-left flex items-center space-x-2">
          <span
            class="w-3.5 h-3.5 rounded-full border border-zinc-300 shadow-inner flex-shrink-0"
            :style="{ backgroundColor: getColorDot(observed.color) }"
          ></span>
          <div>
            <span class="text-xs font-semibold text-zinc-900 capitalize">
              {{ observed.color }}
            </span>
            <div class="text-[10px] text-zinc-400">MobileNetV3</div>
          </div>
        </div>

        <div class="w-1/3 flex items-center justify-end space-x-2">
          <div class="flex items-center space-x-1.5">
            <span
              class="w-3 h-3 rounded-full border border-zinc-300 shadow-inner flex-shrink-0"
              :style="{ backgroundColor: getColorDot(registered.color) }"
            ></span>
            <span class="text-xs font-semibold text-zinc-800 capitalize">
              {{ registered.color }}
            </span>
          </div>
          <CheckCircle2 v-if="colorMatch === 'match'" class="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <AlertTriangle v-else-if="colorMatch === 'variance'" class="w-4 h-4 text-amber-500 flex-shrink-0" />
          <XCircle v-else class="w-4 h-4 text-rose-600 flex-shrink-0" />
        </div>
      </div>

      <!-- 4. Registration Status & Legal Standing -->
      <div class="py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2.5 w-1/3">
          <Shield class="w-4 h-4 text-zinc-500" />
          <span class="text-xs font-semibold text-zinc-700">Legal Status</span>
        </div>

        <div class="w-1/3 text-left">
          <span class="text-xs font-medium text-zinc-500">Live Visual Analysis</span>
        </div>

        <div class="w-1/3 flex items-center justify-end space-x-2">
          <span
            class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
            :class="statusMatch === 'match'
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              : 'bg-rose-50 text-rose-700 border border-rose-200'"
          >
            {{ registered.status }}
          </span>
          <CheckCircle2 v-if="statusMatch === 'match'" class="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <XCircle v-else class="w-4 h-4 text-rose-600 flex-shrink-0" />
        </div>
      </div>

    </div>

  </div>
</template>
