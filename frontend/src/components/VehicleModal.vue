<script setup>
import { ref, onMounted } from 'vue'
import {
  X,
  Plus,
  Trash2,
  Edit2,
  Database,
  Search,
  CheckCircle,
  AlertCircle
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'refresh'])

const vehicles = ref([])
const loading = ref(false)
const searchQuery = ref('')
const isAdding = ref(false)

// Form fields
const form = ref({
  plate_number: '',
  vehicle_type: 'car',
  color: 'white',
  make: 'Hyundai',
  model: 'i20',
  registration_status: 'Active'
})

const fetchVehicles = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/vehicles')
    if (res.ok) {
      vehicles.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to load vehicles:', e)
  } finally {
    loading.value = false
  }
}

const handleAddVehicle = async () => {
  if (!form.value.plate_number.trim()) {
    alert('Please enter a license plate number.')
    return
  }

  try {
    const res = await fetch('/api/vehicles', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plate_number: form.value.plate_number.trim().toUpperCase(),
        vehicle_type: form.value.vehicle_type.trim().toLowerCase(),
        color: form.value.color.trim().toLowerCase(),
        make: form.value.make.trim(),
        model: form.value.model.trim(),
        registration_status: form.value.registration_status
      })
    })

    if (res.ok) {
      isAdding.value = false
      form.value = {
        plate_number: '',
        vehicle_type: 'car',
        color: 'white',
        make: 'Hyundai',
        model: 'i20',
        registration_status: 'Active'
      }
      await fetchVehicles()
      emit('refresh')
    } else {
      const err = await res.json()
      alert(err.detail || 'Could not register vehicle.')
    }
  } catch (e) {
    alert('Network error while creating vehicle.')
  }
}

const handleDeleteVehicle = async (id) => {
  if (!confirm('Are you sure you want to remove this vehicle from the registry?')) return

  try {
    const res = await fetch(`/api/vehicles/${id}`, { method: 'DELETE' })
    if (res.ok) {
      await fetchVehicles()
      emit('refresh')
    }
  } catch (e) {
    alert('Failed to delete vehicle.')
  }
}

onMounted(() => {
  fetchVehicles()
})
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/60 backdrop-blur-sm animate-in fade-in duration-150"
  >
    <div
      class="bg-white rounded-2xl border border-white/60 shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-150 relative"
    >
      <div class="h-1.5 w-full bg-gradient-to-r from-[#e11d48] via-[#d97706] to-[#fbbf24]"></div>
      
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-zinc-100 flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded-lg bg-stone-900 flex items-center justify-center text-white shadow-sm border border-amber-400/60">
            <Database class="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-zinc-900 font-sans">VAHAN Vehicle Registry Management</h3>
            <p class="text-[11px] text-zinc-500">Official ground-truth vehicle records for identity cross-verification</p>
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

      <!-- Search & Add Bar -->
      <div class="px-6 py-3 bg-zinc-50 border-b border-zinc-200 flex items-center justify-between gap-3">
        <div class="relative flex-1">
          <Search class="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-2.5 pointer-events-none" />
          <input
            v-model="searchQuery"
            placeholder="Search by plate number, make, model..."
            class="w-full text-xs pl-8 pr-3 py-1.5 rounded-lg border border-zinc-300 bg-white placeholder:text-zinc-400 text-zinc-800 focus:outline-none focus:border-zinc-500"
          />
        </div>

        <button
          @click="isAdding = !isAdding"
          type="button"
          class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-black bg-gradient-to-r from-[#e11d48] via-[#d97706] to-[#fbbf24] hover:brightness-105 active:scale-[0.98] text-stone-950 shadow-md transition-colors cursor-pointer"
        >
          <Plus class="w-3.5 h-3.5 text-stone-950" />
          <span>{{ isAdding ? 'Cancel Form' : 'Register Vehicle' }}</span>
        </button>
      </div>

      <!-- Add Vehicle Form (Collapsible) -->
      <div v-if="isAdding" class="p-6 bg-zinc-50/70 border-b border-zinc-200">
        <h4 class="text-xs font-bold text-zinc-800 uppercase tracking-wider mb-3">Add Registry Vehicle</h4>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label class="block text-[11px] font-semibold text-zinc-600 mb-1">Plate Number</label>
            <input
              v-model="form.plate_number"
              placeholder="e.g. MH12DE1433"
              class="w-full text-xs font-mono font-bold uppercase px-3 py-1.5 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500"
            />
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-zinc-600 mb-1">Vehicle Type</label>
            <select
              v-model="form.vehicle_type"
              class="w-full text-xs px-3 py-1.5 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500 bg-white"
            >
              <option value="car">Car</option>
              <option value="suv">SUV</option>
              <option value="truck">Truck</option>
              <option value="motorcycle">Motorcycle</option>
              <option value="bus">Bus</option>
            </select>
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-zinc-600 mb-1">Body Color</label>
            <input
              v-model="form.color"
              placeholder="e.g. white, silver, red"
              class="w-full text-xs px-3 py-1.5 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500"
            />
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-zinc-600 mb-1">Make</label>
            <input
              v-model="form.make"
              placeholder="e.g. Hyundai"
              class="w-full text-xs px-3 py-1.5 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500"
            />
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-zinc-600 mb-1">Model</label>
            <input
              v-model="form.model"
              placeholder="e.g. i20"
              class="w-full text-xs px-3 py-1.5 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500"
            />
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-zinc-600 mb-1">Registration Status</label>
            <select
              v-model="form.registration_status"
              class="w-full text-xs px-3 py-1.5 rounded-lg border border-zinc-300 focus:outline-none focus:border-zinc-500 bg-white"
            >
              <option value="Active">Active</option>
              <option value="Stolen">Stolen</option>
              <option value="Suspended">Suspended</option>
            </select>
          </div>
        </div>
        <div class="mt-4 flex justify-end space-x-2">
          <button
            @click="isAdding = false"
            type="button"
            class="px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-600 hover:bg-zinc-200"
          >
            Cancel
          </button>
          <button
            @click="handleAddVehicle"
            type="button"
            class="px-4 py-1.5 rounded-xl text-xs font-black bg-gradient-to-r from-[#e11d48] via-[#d97706] to-[#fbbf24] hover:brightness-105 active:scale-[0.98] text-stone-950 shadow-md cursor-pointer"
          >
            Save Vehicle
          </button>
        </div>
      </div>

      <!-- Vehicle Table List -->
      <div class="overflow-y-auto flex-1">
        <table class="w-full text-left border-collapse">
          <thead class="bg-zinc-50 border-b border-zinc-200 text-[11px] font-bold uppercase tracking-wider text-zinc-500 sticky top-0">
            <tr>
              <th class="py-2.5 px-4">Plate</th>
              <th class="py-2.5 px-4">Type</th>
              <th class="py-2.5 px-4">Color</th>
              <th class="py-2.5 px-4">Make & Model</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-100 text-xs">
            <tr
              v-for="v in vehicles.filter(x => !searchQuery || x.plate_number.toLowerCase().includes(searchQuery.toLowerCase()))"
              :key="v.vehicle_id"
              class="hover:bg-zinc-50"
            >
              <td class="py-2.5 px-4 font-mono font-bold text-zinc-900 tracking-wider">
                {{ v.plate_number }}
              </td>
              <td class="py-2.5 px-4 capitalize text-zinc-700">
                {{ v.vehicle_type }}
              </td>
              <td class="py-2.5 px-4 capitalize text-zinc-700">
                {{ v.color }}
              </td>
              <td class="py-2.5 px-4 text-zinc-700">
                {{ v.make }} {{ v.model }}
              </td>
              <td class="py-2.5 px-4">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase"
                  :class="v.registration_status === 'Active'
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-rose-50 text-rose-700 border border-rose-200'"
                >
                  {{ v.registration_status }}
                </span>
              </td>
              <td class="py-2.5 px-4 text-right">
                <button
                  @click="handleDeleteVehicle(v.vehicle_id)"
                  type="button"
                  class="p-1 rounded text-zinc-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                  title="Remove vehicle"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-3 bg-zinc-50 border-t border-zinc-200 flex items-center justify-between text-xs text-zinc-500">
        <span>Total Registered: {{ vehicles.length }}</span>
        <button
          @click="emit('close')"
          type="button"
          class="px-4 py-1.5 rounded-lg text-xs font-semibold bg-zinc-900 hover:bg-zinc-800 text-white"
        >
          Close
        </button>
      </div>

    </div>
  </div>
</template>
