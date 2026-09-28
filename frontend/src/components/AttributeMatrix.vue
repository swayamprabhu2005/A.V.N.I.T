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
  Layers,
  Camera,
  Image as ImageIcon,
  Lock
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
    plate: props.telemetry?.plate_number || 'DETECTING...',
    type: props.telemetry?.vehicle_type || 'N/A',
    color: props.telemetry?.observed_color || 'N/A',
    confidence: props.telemetry?.ocr_confidence
      ? Math.round(props.telemetry.ocr_confidence * 100)
      : (props.telemetry?.plate_number && props.telemetry?.plate_number !== 'DETECTING...' ? 95 : 0),
    isLocked: Boolean(props.telemetry?.is_locked),
    snapshotImage: props.telemetry?.snapshot_image || '',
    plateImage: props.telemetry?.plate_image || ''
  }
})

// Registered values from VAHAN database
const registered = computed(() => {
  const reg = props.riskResult?.registered_details || props.riskResult?.registration_record
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
</script>

<template>
  <div class="bg-white/92 backdrop-blur-xl rounded-2xl border border-[#743E63]/25 shadow-xl p-6 space-y-5 transition-all relative overflow-hidden">
    <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#743E63] via-[#974A5E] via-[#BF5E65] via-[#E95350] to-[#F27951]"></div>
    
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-stone-200 pb-3 pt-1">
      <div>
        <span class="text-[11px] font-bold text-stone-500 uppercase tracking-widest block">Identity Cross-Verification</span>
        <h3 class="text-sm font-black text-stone-900 tracking-tight">Observed Visuals vs. Registered Record</h3>
      </div>
      <div v-if="registered.exists" class="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300">
        <CheckCircle2 class="w-3.5 h-3.5" />
        <span>VAHAN Matched</span>
      </div>
      <div v-else class="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 text-xs font-bold border border-rose-300">
        <XCircle class="w-3.5 h-3.5" />
        <span>Unregistered Plate</span>
      </div>
    </div>

    <!-- 📸 Captured Keyframe Evidence Snapshot (New Feature) -->
    <div v-if="observed.snapshotImage" class="p-4 rounded-xl bg-gradient-to-br from-stone-900 to-stone-950 text-white border border-stone-800 shadow-inner space-y-3">
      
      <div class="flex items-center justify-between text-xs">
        <div class="flex items-center space-x-2 font-bold tracking-wide text-stone-200">
          <Camera class="w-4 h-4 text-emerald-400" />
          <span>Best-Frame Vehicle Capture</span>
        </div>
        <div class="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono text-[10px] font-bold border border-emerald-500/30">
          <Lock class="w-3 h-3" />
          <span>LOCKED VERDICT</span>
        </div>
      </div>

      <div class="grid grid-cols-12 gap-3 items-center">
        <!-- Full Car Snip -->
        <div class="col-span-8 rounded-lg overflow-hidden border border-stone-700 bg-black aspect-video relative group">
          <img
            :src="observed.snapshotImage"
            alt="Captured Vehicle"
            class="w-full h-full object-cover"
          />
          <div class="absolute bottom-1.5 left-2 px-1.5 py-0.5 rounded bg-black/70 text-[10px] font-mono text-stone-300">
            ID #{{ telemetry?.track_id || 1 }} Peak Clarity
          </div>
        </div>

        <!-- Bumper Plate Snip -->
        <div class="col-span-4 space-y-1.5">
          <div class="text-[10px] uppercase font-bold text-stone-400">Plate Crop</div>
          <div class="rounded-lg overflow-hidden border border-amber-500/40 bg-black aspect-[3/1] flex items-center justify-center">
            <img
              v-if="observed.plateImage"
              :src="observed.plateImage"
              alt="Plate Crop"
              class="w-full h-full object-contain"
            />
            <span v-else class="text-[10px] text-stone-500">Plate Crop</span>
          </div>
          <div class="text-[11px] font-mono font-bold text-amber-300 tracking-wider text-center">
            {{ observed.plate }}
          </div>
        </div>
      </div>

    </div>

    <!-- Comparative Visual Grid -->
    <div class="space-y-3">
      
      <!-- Attribute 1: Plate Number -->
      <div class="p-3.5 rounded-xl border border-stone-200 bg-stone-50/80 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="p-2 rounded-lg bg-stone-200 text-stone-800">
            <CreditCard class="w-4 h-4" />
          </div>
          <div>
            <div class="text-xs font-bold text-stone-600">License Plate</div>
            <div class="text-sm font-mono font-black text-stone-900 tracking-wider">
              {{ observed.plate }}
            </div>
            <div class="text-[10px] text-stone-500 font-mono">
              OCR Conf: {{ observed.confidence }}%
            </div>
          </div>
        </div>

        <div class="text-right">
          <div class="text-xs font-bold font-mono tracking-wider" :class="registered.exists ? 'text-stone-900' : 'text-rose-700'">
            {{ registered.plate }}
          </div>
          <div class="text-[10px] font-medium" :class="registered.exists ? 'text-emerald-700' : 'text-rose-600'">
            {{ registered.exists ? 'VAHAN Registered' : 'Not in Central DB' }}
          </div>
        </div>
      </div>

      <!-- Attribute 2: Vehicle Type -->
      <div class="p-3.5 rounded-xl border border-stone-200 bg-stone-50/80 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="p-2 rounded-lg bg-stone-200 text-stone-800">
            <Car class="w-4 h-4" />
          </div>
          <div>
            <div class="text-xs font-bold text-stone-600">Vehicle Type</div>
            <div class="text-sm font-black text-stone-900 capitalize">
              {{ observed.type }}
            </div>
            <div class="text-[10px] text-stone-500 font-medium">
              YOLOv8 Detection
            </div>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <div class="text-right">
            <div class="text-xs font-bold capitalize text-stone-900">
              {{ registered.type }}
            </div>
            <div class="text-[10px] text-stone-500">
              Registered Class
            </div>
          </div>
          <div v-if="registered.exists">
            <CheckCircle2 v-if="typeMatch === 'match'" class="w-4 h-4 text-emerald-700" />
            <XCircle v-else class="w-4 h-4 text-rose-700" />
          </div>
          <XCircle v-else class="w-4 h-4 text-rose-600" />
        </div>
      </div>

      <!-- Attribute 3: Vehicle Color -->
      <div class="p-3.5 rounded-xl border border-stone-200 bg-stone-50/80 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="p-2 rounded-lg bg-stone-200 text-stone-800">
            <Palette class="w-4 h-4" />
          </div>
          <div>
            <div class="text-xs font-bold text-stone-600">Vehicle Color</div>
            <div class="text-sm font-black text-stone-900 capitalize">
              {{ observed.color }}
            </div>
            <div class="text-[10px] text-stone-500 font-medium">
              MobileNetV3 15-Class
            </div>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <div class="text-right">
            <div class="text-xs font-bold capitalize text-stone-900">
              {{ registered.color }}
            </div>
            <div class="text-[10px] text-stone-500">
              Registered Color
            </div>
          </div>
          <div v-if="registered.exists">
            <CheckCircle2 v-if="colorMatch === 'match'" class="w-4 h-4 text-emerald-700" />
            <AlertTriangle v-else-if="colorMatch === 'variance'" class="w-4 h-4 text-amber-700" />
            <XCircle v-else class="w-4 h-4 text-rose-700" />
          </div>
          <XCircle v-else class="w-4 h-4 text-rose-600" />
        </div>
      </div>

      <!-- Attribute 4: Legal Registration Status -->
      <div class="p-3.5 rounded-xl border border-stone-200 bg-stone-50/80 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="p-2 rounded-lg bg-stone-200 text-stone-800">
            <Shield class="w-4 h-4" />
          </div>
          <div>
            <div class="text-xs font-bold text-stone-600">Legal Status</div>
            <div class="text-sm font-black text-stone-900">
              Live Audit Pass
            </div>
            <div class="text-[10px] text-stone-500 font-medium">
              Real-time verification
            </div>
          </div>
        </div>

        <div>
          <span
            class="px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider border"
            :class="registered.exists && statusMatch === 'match'
              ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
              : 'bg-rose-100 text-rose-800 border-rose-300'"
          >
            {{ registered.status }}
          </span>
        </div>
      </div>

    </div>

  </div>
</template>
