<script setup>
import { computed } from 'vue'
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-vue-next'

const props = defineProps({
  riskResult: {
    type: Object,
    default: null
  },
  visible: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['dismiss'])

const isHighRisk = computed(() => {
  const score = props.riskResult?.risk_score || 0
  return score >= 60 || props.riskResult?.risk_level === 'RED'
})

const isWarning = computed(() => {
  const score = props.riskResult?.risk_score || 0
  return score >= 30 && score < 60
})
</script>

<template>
  <transition
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="translate-y-2 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition ease-in duration-150"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="visible && (isHighRisk || isWarning)"
      class="rounded-xl border shadow-card p-4 transition-all"
      :class="isHighRisk
        ? 'bg-rose-50/95 border-rose-300 text-rose-900'
        : 'bg-amber-50/95 border-amber-300 text-amber-900'"
    >
      <div class="flex items-start justify-between">
        <div class="flex items-start space-x-3">
          <div
            class="p-2 rounded-lg flex-shrink-0 mt-0.5"
            :class="isHighRisk ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'"
          >
            <ShieldAlert v-if="isHighRisk" class="w-5 h-5 animate-pulse" />
            <AlertTriangle v-else class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <span class="text-xs font-bold uppercase tracking-wider">
                {{ isHighRisk ? 'CRITICAL IDENTITY TAMPERING ALERT' : 'ATTRIBUTE VARIANCE DETECTED' }}
              </span>
              <span class="font-mono text-xs font-extrabold px-2 py-0.5 rounded bg-white/80 border border-zinc-300">
                {{ (riskResult?.plate_number || 'UNKNOWN').toUpperCase() }}
              </span>
            </div>
            <p class="text-xs mt-1 font-medium leading-relaxed">
              {{ riskResult?.reasons?.[0] || 'Vehicle attributes do not match official VAHAN registry records.' }}
            </p>
          </div>
        </div>

        <button
          @click="emit('dismiss')"
          type="button"
          class="p-1 rounded-lg text-zinc-400 hover:text-zinc-600 transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
  </transition>
</template>
