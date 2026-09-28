<script setup>
import { computed } from 'vue'
import {
  ShieldCheck,
  AlertTriangle,
  ShieldAlert,
  Moon,
  Info
} from 'lucide-vue-next'

const props = defineProps({
  riskResult: {
    type: Object,
    default: null
  },
  isNightMode: {
    type: Boolean,
    default: false
  }
})

// Current Risk Score (0 - 100)
const riskScore = computed(() => {
  if (!props.riskResult || typeof props.riskResult.risk_score !== 'number') {
    return 0
  }
  return Math.min(100, Math.max(0, props.riskResult.risk_score))
})

// Risk Classification Level
const riskLevel = computed(() => {
  if (!props.riskResult) return 'STANDBY'
  const score = riskScore.value
  if (score >= 60 || props.riskResult.risk_level === 'RED') return 'RED'
  if (score >= 30 || props.riskResult.risk_level === 'YELLOW') return 'YELLOW'
  return 'GREEN'
})

// Visual Theme Configuration (Strictly Zero Blue)
const levelConfig = computed(() => {
  switch (riskLevel.value) {
    case 'RED':
      return {
        label: 'IDENTITY TAMPERING DETECTED',
        badgeBg: 'bg-rose-50 text-rose-700 border-rose-200',
        strokeColor: '#f43f5e',
        glowColor: 'rgba(244, 63, 94, 0.25)',
        icon: ShieldAlert,
        iconColor: 'text-rose-600'
      }
    case 'YELLOW':
      return {
        label: 'ATTRIBUTE VARIANCE REVIEW',
        badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
        strokeColor: '#f59e0b',
        glowColor: 'rgba(245, 158, 11, 0.25)',
        icon: AlertTriangle,
        iconColor: 'text-amber-600'
      }
    case 'GREEN':
      return {
        label: 'VEHICLE IDENTITY VERIFIED',
        badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        strokeColor: '#10b981',
        glowColor: 'rgba(16, 185, 129, 0.25)',
        icon: ShieldCheck,
        iconColor: 'text-emerald-600'
      }
    default:
      return {
        label: 'SYSTEM IDLE / MONITORING',
        badgeBg: 'bg-zinc-100 text-zinc-600 border-zinc-200',
        strokeColor: '#71717a',
        glowColor: 'rgba(113, 113, 122, 0.1)',
        icon: Info,
        iconColor: 'text-zinc-500'
      }
  }
})

// Radial Gauge Math
const radius = 54
const circumference = 2 * Math.PI * radius
const strokeDashoffset = computed(() => {
  const fraction = riskScore.value / 100
  return circumference - fraction * circumference
})

// Granular Risk Factor Breakdowns
const breakdown = computed(() => {
  const factors = props.riskResult?.factors || {}
  const isNight = props.isNightMode

  return [
    {
      name: 'Vehicle Type',
      score: factors.score_type !== undefined ? Math.round(factors.score_type * 100) : 100,
      weight: isNight ? '40% (Night Adj)' : '35%',
      status: factors.type_matched !== false
    },
    {
      name: 'Color Spectrum',
      score: factors.score_color !== undefined ? Math.round(factors.score_color * 100) : 100,
      weight: isNight ? '5% (IR Night Mode)' : '20%',
      status: (factors.score_color ?? 1.0) >= 0.5
    },
    {
      name: 'OCR Fidelity',
      score: factors.score_ocr !== undefined ? Math.round(factors.score_ocr * 100) : 100,
      weight: isNight ? '35% (Night Adj)' : '20%',
      status: (factors.score_ocr ?? 1.0) >= 0.7
    },
    {
      name: 'Make / Model',
      score: factors.score_make_model !== undefined ? Math.round(factors.score_make_model * 100) : 85,
      weight: isNight ? '20% (Night Adj)' : '25%',
      status: true
    }
  ]
})
</script>

<template>
  <div class="bg-white/92 backdrop-blur-xl rounded-2xl border border-white/60 shadow-xl p-5 flex flex-col justify-between relative overflow-hidden">
    <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#e11d48] via-[#d97706] to-[#fbbf24]"></div>
    
    <!-- Top Header -->
    <div class="flex items-center justify-between border-b border-zinc-100 pb-3 pt-1">
      <div>
        <h2 class="text-xs font-bold uppercase tracking-wider text-zinc-500">Bayesian Risk Engine</h2>
        <p class="text-sm font-bold text-zinc-900 font-sans">Multi-Factor Integrity Assessment</p>
      </div>

      <!-- Verdict Pill -->
      <span
        class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-bold border tracking-wide shadow-sm"
        :class="levelConfig.badgeBg"
      >
        <component :is="levelConfig.icon" class="w-3.5 h-3.5" :class="levelConfig.iconColor" />
        <span>{{ levelConfig.label }}</span>
      </span>
    </div>

    <!-- Center: Radial Gauge Display -->
    <div class="my-4 flex items-center justify-center">
      <div class="relative flex items-center justify-center">
        
        <!-- SVG Gauge -->
        <svg class="w-36 h-36 transform -rotate-90" viewBox="0 0 128 128">
          <!-- Background track -->
          <circle
            cx="64"
            cy="64"
            :r="radius"
            stroke="#f4f4f5"
            stroke-width="10"
            fill="transparent"
          />
          <!-- Animated Score arc -->
          <circle
            cx="64"
            cy="64"
            :r="radius"
            :stroke="levelConfig.strokeColor"
            stroke-width="10"
            stroke-linecap="round"
            fill="transparent"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="strokeDashoffset"
            class="transition-all duration-700 ease-out"
          />
        </svg>

        <!-- Center Ticker Number -->
        <div class="absolute flex flex-col items-center justify-center text-center">
          <span class="text-3xl font-extrabold tracking-tight font-sans text-zinc-900">
            {{ riskScore.toFixed(0) }}<span class="text-sm font-semibold text-zinc-400">%</span>
          </span>
          <span class="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mt-0.5">
            Risk Index
          </span>
        </div>

      </div>
    </div>

    <!-- Factor Weights Breakdown Grid -->
    <div class="grid grid-cols-2 gap-2 my-2">
      <div
        v-for="f in breakdown"
        :key="f.name"
        class="p-2.5 rounded-lg bg-zinc-50/80 border border-zinc-200/70 flex flex-col justify-between"
      >
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-semibold text-zinc-700">{{ f.name }}</span>
          <span
            class="w-2 h-2 rounded-full"
            :class="f.status ? 'bg-emerald-500' : 'bg-rose-500'"
          ></span>
        </div>
        <div class="flex items-baseline justify-between mt-1">
          <span class="text-xs font-mono font-bold text-zinc-900">{{ f.score }}%</span>
          <span class="text-[9px] text-zinc-400 font-medium">{{ f.weight }}</span>
        </div>
      </div>
    </div>

    <!-- Explainability Findings Box -->
    <div class="mt-2 pt-3 border-t border-zinc-100">
      <div class="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider mb-1">
        Telemetry Findings
      </div>
      <div class="text-xs text-zinc-700 bg-zinc-50 rounded-lg p-2.5 border border-zinc-200 font-medium leading-relaxed">
        <ul v-if="riskResult?.reasons?.length" class="space-y-1 list-disc list-inside">
          <li v-for="(reason, idx) in riskResult.reasons" :key="idx" class="text-zinc-800">
            {{ reason }}
          </li>
        </ul>
        <div v-else class="text-zinc-400 italic">
          Awaiting vehicle detection in active camera zone...
        </div>
      </div>
    </div>

  </div>
</template>
