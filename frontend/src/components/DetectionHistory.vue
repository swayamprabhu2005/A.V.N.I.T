<script setup>
import { ref, computed } from 'vue'
import {
  Search,
  Filter,
  FileSpreadsheet,
  FileText,
  Clock,
  Car,
  AlertCircle,
  CheckCircle,
  AlertTriangle
} from 'lucide-vue-next'

const props = defineProps({
  alerts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['export-csv', 'export-pdf', 'select-alert'])

const searchQuery = ref('')
const selectedFilter = ref('ALL') // 'ALL', 'GREEN', 'YELLOW', 'RED'

const filteredAlerts = computed(() => {
  let list = props.alerts || []

  // Filter by category
  if (selectedFilter.value !== 'ALL') {
    list = list.filter(a => {
      const score = a.risk_score || 0
      if (selectedFilter.value === 'RED') return score >= 60 || a.risk_level === 'RED'
      if (selectedFilter.value === 'YELLOW') return (score >= 30 && score < 60) || a.risk_level === 'YELLOW'
      if (selectedFilter.value === 'GREEN') return score < 30 || a.risk_level === 'GREEN'
      return true
    })
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(a =>
      (a.plate_number || '').toLowerCase().includes(q) ||
      (a.observed_type || '').toLowerCase().includes(q) ||
      (a.reason || '').toLowerCase().includes(q)
    )
  }

  return list
})

const getVerdictBadge = (score, level) => {
  const s = score || 0
  if (s >= 60 || level === 'RED') {
    return {
      text: 'TAMPER ALERT',
      badgeClass: 'bg-rose-50 text-rose-700 border-rose-200',
      dotClass: 'bg-rose-600'
    }
  }
  if (s >= 30 || level === 'YELLOW') {
    return {
      text: 'REVIEW',
      badgeClass: 'bg-amber-50 text-amber-700 border-amber-200',
      dotClass: 'bg-amber-600'
    }
  }
  return {
    text: 'VERIFIED',
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dotClass: 'bg-emerald-600'
  }
}
</script>

<template>
  <div class="bg-white rounded-xl border border-zinc-200/90 shadow-card overflow-hidden flex flex-col">
    
    <!-- Top Filter & Search Header -->
    <div class="px-5 py-4 border-b border-zinc-100 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-xs font-bold uppercase tracking-wider text-zinc-500">Live Incident Stream</h2>
        <p class="text-sm font-bold text-zinc-900 font-sans">Chronological Vehicle Audit Feed</p>
      </div>

      <!-- Search & Filter Controls -->
      <div class="flex items-center space-x-2.5 flex-wrap">
        
        <!-- Search Input -->
        <div class="relative flex items-center">
          <Search class="w-3.5 h-3.5 text-zinc-400 absolute left-3 pointer-events-none" />
          <input
            v-model="searchQuery"
            placeholder="Search plate or type..."
            class="text-xs pl-8 pr-3 py-1.5 rounded-lg border border-zinc-300 bg-white placeholder:text-zinc-400 text-zinc-800 focus:outline-none focus:border-zinc-500 w-44 sm:w-56 shadow-sm"
          />
        </div>

        <!-- Filter Tabs -->
        <div class="inline-flex rounded-lg border border-zinc-200 p-0.5 bg-zinc-100 text-xs font-medium text-zinc-600">
          <button
            @click="selectedFilter = 'ALL'"
            type="button"
            class="px-2.5 py-1 rounded-md transition-all text-[11px]"
            :class="selectedFilter === 'ALL' ? 'bg-white font-bold text-zinc-900 shadow-sm' : 'hover:text-zinc-900'"
          >
            All
          </button>
          <button
            @click="selectedFilter = 'GREEN'"
            type="button"
            class="px-2.5 py-1 rounded-md transition-all text-[11px]"
            :class="selectedFilter === 'GREEN' ? 'bg-white font-bold text-emerald-700 shadow-sm' : 'hover:text-emerald-700'"
          >
            Passes
          </button>
          <button
            @click="selectedFilter = 'RED'"
            type="button"
            class="px-2.5 py-1 rounded-md transition-all text-[11px]"
            :class="selectedFilter === 'RED' ? 'bg-white font-bold text-rose-700 shadow-sm' : 'hover:text-rose-700'"
          >
            Alerts
          </button>
        </div>

        <!-- Direct CSV & PDF Export Buttons -->
        <div class="flex items-center space-x-1.5 border-l border-zinc-200 pl-2.5">
          <button
            @click="emit('export-csv')"
            title="Download CSV Spreadsheet"
            type="button"
            class="p-1.5 rounded-lg border border-zinc-200 hover:bg-zinc-100 text-zinc-700 transition-colors shadow-sm"
          >
            <FileSpreadsheet class="w-4 h-4 text-emerald-600" />
          </button>
          <button
            @click="emit('export-pdf')"
            title="Download PDF Dossier"
            type="button"
            class="p-1.5 rounded-lg border border-zinc-200 hover:bg-zinc-100 text-zinc-700 transition-colors shadow-sm"
          >
            <FileText class="w-4 h-4 text-rose-600" />
          </button>
        </div>

      </div>
    </div>

    <!-- Table Container -->
    <div class="overflow-x-auto max-h-[380px] overflow-y-auto">
      <table class="w-full text-left border-collapse">
        <thead class="bg-zinc-50 border-b border-zinc-200 sticky top-0 z-10 text-[11px] font-bold uppercase tracking-wider text-zinc-500">
          <tr>
            <th class="py-2.5 px-4">Time</th>
            <th class="py-2.5 px-4">Plate Number</th>
            <th class="py-2.5 px-4">Observed Attributes</th>
            <th class="py-2.5 px-4">Risk Index</th>
            <th class="py-2.5 px-4">Verdict</th>
            <th class="py-2.5 px-4">Audit Finding</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-100 text-xs">
          <tr
            v-for="(item, idx) in filteredAlerts"
            :key="idx"
            @click="emit('select-alert', item)"
            class="hover:bg-zinc-50/90 cursor-pointer transition-colors"
          >
            <!-- Timestamp -->
            <td class="py-3 px-4 font-mono text-[11px] text-zinc-500 whitespace-nowrap">
              {{ (item.timestamp || '').slice(11, 19) || 'Just now' }}
            </td>

            <!-- Plate Number -->
            <td class="py-3 px-4">
              <span class="font-mono font-bold text-zinc-900 bg-zinc-100 px-2 py-0.5 rounded border border-zinc-200 tracking-wider">
                {{ (item.plate_number || 'UNKNOWN').toUpperCase() }}
              </span>
            </td>

            <!-- Observed Attributes -->
            <td class="py-3 px-4 text-zinc-700 capitalize whitespace-nowrap">
              <div class="flex items-center space-x-1.5">
                <Car class="w-3.5 h-3.5 text-zinc-400" />
                <span class="font-semibold">{{ item.observed_type || 'Car' }}</span>
                <span class="text-zinc-300">•</span>
                <span>{{ item.observed_color || 'White' }}</span>
              </div>
            </td>

            <!-- Risk Score -->
            <td class="py-3 px-4 font-mono font-bold text-zinc-900 whitespace-nowrap">
              {{ typeof item.risk_score === 'number' ? item.risk_score.toFixed(1) : '0.0' }}%
            </td>

            <!-- Verdict Badge -->
            <td class="py-3 px-4 whitespace-nowrap">
              <span
                class="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border tracking-wide"
                :class="getVerdictBadge(item.risk_score, item.risk_level).badgeClass"
              >
                <span
                  class="w-1.5 h-1.5 rounded-full"
                  :class="getVerdictBadge(item.risk_score, item.risk_level).dotClass"
                ></span>
                <span>{{ getVerdictBadge(item.risk_score, item.risk_level).text }}</span>
              </span>
            </td>

            <!-- Audit Finding Explanation -->
            <td class="py-3 px-4 text-zinc-600 max-w-xs truncate text-[11px]">
              {{ item.reason || 'Routine Verification Pass' }}
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="filteredAlerts.length === 0">
            <td colspan="6" class="py-8 text-center text-zinc-400 text-xs italic">
              No incident records matching the selected filter criteria.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Table Footer Count -->
    <div class="px-5 py-2.5 bg-zinc-50 border-t border-zinc-200 flex items-center justify-between text-[11px] text-zinc-500 font-medium">
      <span>Showing {{ filteredAlerts.length }} of {{ alerts.length }} total events</span>
      <span>SQLite WAL Sync Active</span>
    </div>

  </div>
</template>
