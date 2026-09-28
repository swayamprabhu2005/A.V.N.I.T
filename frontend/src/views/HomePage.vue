<script setup>
import { ref } from 'vue'
import {
  Shield,
  ShieldCheck,
  KeyRound,
  LogIn,
  Camera,
  Layers,
  Cpu,
  Database,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  FileBadge
} from 'lucide-vue-next'
import { signInWithGoogle, signInWithMicrosoft, logInWithSerial } from '../services/firebase'

const emit = defineEmits(['login-success'])

const badgeSerial = ref('AVNIT-OFFICER-2026')
const department = ref('National Highway Enforcement Unit - Sector 4')
const isLoading = ref(false)
const errorMessage = ref('')
const infoMessage = ref('')

const handleSerialLogin = () => {
  if (!badgeSerial.value.trim()) {
    errorMessage.value = 'Please enter an Operator Badge ID or Serial Number.'
    return
  }
  isLoading.value = true
  errorMessage.value = ''
  
  setTimeout(() => {
    const user = logInWithSerial(badgeSerial.value, department.value)
    isLoading.value = false
    emit('login-success', user)
  }, 400)
}

const handleGoogleSSO = async () => {
  isLoading.value = true
  errorMessage.value = ''
  infoMessage.value = ''
  try {
    const user = await signInWithGoogle()
    isLoading.value = false
    emit('login-success', user)
  } catch (err) {
    isLoading.value = false
    console.warn('Google SSO notice:', err)
    if (err.message?.includes('FIREBASE_NOT_CONFIGURED')) {
      infoMessage.value = 'Firebase production credentials are not yet configured in frontend/.env. You can log in instantly below using your Operator Badge Serial Number.'
    } else {
      errorMessage.value = err.message || 'Google SSO authentication encountered an issue.'
    }
  }
}

const handleMicrosoftSSO = async () => {
  isLoading.value = true
  errorMessage.value = ''
  infoMessage.value = ''
  try {
    const user = await signInWithMicrosoft()
    isLoading.value = false
    emit('login-success', user)
  } catch (err) {
    isLoading.value = false
    console.warn('Microsoft SSO notice:', err)
    if (err.message?.includes('FIREBASE_NOT_CONFIGURED')) {
      infoMessage.value = 'Firebase production credentials are not yet configured in frontend/.env. You can log in instantly below using your Operator Badge Serial Number.'
    } else {
      errorMessage.value = err.message || 'Microsoft SSO authentication encountered an issue.'
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-[#faf7f2] via-[#f1ebe0] to-[#e4ded0] text-stone-900 flex flex-col font-sans selection:bg-amber-100 selection:text-amber-900 relative overflow-hidden">
    
    <!-- Ambient Warm Geometric Gradients (Zero Blue) -->
    <div class="absolute top-0 left-1/4 w-[600px] h-[600px] bg-amber-500/5 rounded-full blur-3xl pointer-events-none -translate-y-1/2"></div>
    <div class="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-3xl pointer-events-none translate-y-1/2"></div>

    <!-- Top Navigation Header -->
    <header class="w-full border-b border-stone-300/80 bg-white/70 backdrop-blur-md sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        
        <div class="flex items-center space-x-3.5">
          <img
            src="/AVNIT.png"
            alt="AVNIT Emblem"
            class="w-10 h-10 rounded-xl shadow-md border border-stone-300/80 object-cover"
          />
          <div>
            <div class="flex items-center space-x-2">
              <span class="text-xl font-black tracking-wider text-stone-900">A.V.N.I.T.</span>
              <span class="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded bg-stone-900 text-stone-100">Enterprise</span>
            </div>
            <p class="text-xs text-stone-600 font-medium tracking-tight">Automated Vehicle Identity & Tampering Detection</p>
          </div>
        </div>

        <div class="hidden md:flex items-center space-x-4 text-xs font-semibold text-stone-700">
          <div class="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-100/80 text-emerald-800 border border-emerald-300/60">
            <span class="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
            <span>Vision Nodes Online</span>
          </div>
          <div class="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-stone-200/80 text-stone-800 border border-stone-300/60">
            <Database class="w-3.5 h-3.5 text-stone-600" />
            <span>VAHAN Gateway Ready</span>
          </div>
        </div>

      </div>
    </header>

    <!-- Main Hero & Authentication Container -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16 flex flex-col lg:flex-row items-center justify-between gap-12 z-10">
      
      <!-- Left Column: System Vision & Capabilities -->
      <div class="flex-1 space-y-6 text-left max-w-2xl">
        
        <div class="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-stone-900/5 border border-stone-400/30 text-stone-800 text-xs font-semibold">
          <ShieldCheck class="w-4 h-4 text-emerald-700" />
          <span>Next-Generation Intelligent Transportation Security</span>
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black text-stone-950 tracking-tight leading-[1.1]">
          Autonomous Vehicle <br/>
          <span class="bg-gradient-to-r from-stone-900 via-amber-900 to-stone-800 bg-clip-text text-transparent">Identity Verification</span> <br/>
          & Tampering Detection
        </h1>

        <p class="text-stone-700 text-base sm:text-lg leading-relaxed font-normal">
          Beyond conventional OCR. A.V.N.I.T. combines deep neural network tracking with real-time VAHAN motor registry cross-referencing to instantly intercept cloned plates, altered characters, and swapped registrations across national highways.
        </p>

        <!-- Feature Grid (Warm Slate/Stone Cards, Zero Blue) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          
          <div class="p-4 rounded-xl bg-white/80 backdrop-blur-sm border border-stone-300/80 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex items-center space-x-3 mb-2">
              <div class="p-2 rounded-lg bg-stone-100 text-stone-800">
                <Camera class="w-5 h-5" />
              </div>
              <h3 class="font-bold text-stone-900 text-sm">Best-Frame Snapshot Capture</h3>
            </div>
            <p class="text-xs text-stone-600 leading-normal">
              Automatically captures high-res vehicle and plate crops at peak foreground resolution, eliminating distant blur.
            </p>
          </div>

          <div class="p-4 rounded-xl bg-white/80 backdrop-blur-sm border border-stone-300/80 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex items-center space-x-3 mb-2">
              <div class="p-2 rounded-lg bg-emerald-100 text-emerald-800">
                <Cpu class="w-5 h-5" />
              </div>
              <h3 class="font-bold text-stone-900 text-sm">4-Factor Bayesian Risk</h3>
            </div>
            <p class="text-xs text-stone-600 leading-normal">
              Evaluates Vehicle Type, 15-Class Color, Plate Geometry, and OCR character topology with night IR compensation.
            </p>
          </div>

        </div>

      </div>

      <!-- Right Column: Authentication Card with SSO & Serial Login -->
      <div class="w-full max-w-md">
        
        <div class="bg-white/95 backdrop-blur-xl border border-stone-300 shadow-2xl rounded-2xl p-7 space-y-6">
          
          <div class="text-center space-y-1.5 border-b border-stone-200 pb-5">
            <div class="inline-flex p-3 rounded-2xl bg-stone-100 border border-stone-200 text-stone-900 mb-2">
              <Shield class="w-6 h-6 text-stone-800" />
            </div>
            <h2 class="text-2xl font-black text-stone-900 tracking-tight">Command Center Portal</h2>
            <p class="text-xs text-stone-600 font-medium">Authenticate to access live camera feeds and violation audits</p>
          </div>

          <!-- Alert / Info Banners -->
          <div v-if="infoMessage" class="p-3.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs flex items-start space-x-2.5">
            <AlertCircle class="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
            <div class="space-y-1">
              <p class="font-medium leading-relaxed">{{ infoMessage }}</p>
            </div>
          </div>

          <div v-if="errorMessage" class="p-3 rounded-xl bg-rose-50 border border-rose-300 text-rose-900 text-xs flex items-center space-x-2">
            <AlertCircle class="w-4 h-4 text-rose-700 flex-shrink-0" />
            <p class="font-medium">{{ errorMessage }}</p>
          </div>

          <!-- SSO Options -->
          <div class="space-y-3">
            
            <!-- Google SSO -->
            <button
              @click="handleGoogleSSO"
              :disabled="isLoading"
              class="w-full flex items-center justify-center space-x-3 py-2.5 px-4 rounded-xl border border-stone-300 bg-white hover:bg-stone-50 active:bg-stone-100 text-stone-800 text-sm font-semibold transition shadow-sm"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.9c2.28-2.1 3.64-5.2 3.64-9.15z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.9-3.05c-1.08.72-2.45 1.16-4.03 1.16-3.1 0-5.74-2.1-6.68-4.93H1.21v3.15C3.25 21.32 7.33 24 12 24z"/>
                <path fill="#FBBC05" d="M5.32 14.27c-.24-.72-.38-1.49-.38-2.27s.14-1.55.38-2.27V6.58H1.21C.44 8.11 0 9.99 0 12s.44 3.89 1.21 5.42l4.11-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.25 2.68 1.21 6.58l4.11 3.15c.94-2.83 3.58-4.98 6.68-4.98z"/>
              </svg>
              <span>Sign in with Google</span>
            </button>

            <!-- Microsoft SSO -->
            <button
              @click="handleMicrosoftSSO"
              :disabled="isLoading"
              class="w-full flex items-center justify-center space-x-3 py-2.5 px-4 rounded-xl border border-stone-300 bg-white hover:bg-stone-50 active:bg-stone-100 text-stone-800 text-sm font-semibold transition shadow-sm"
            >
              <svg class="w-4 h-4" viewBox="0 0 23 23">
                <path fill="#f35325" d="M1 1h10v10H1z"/>
                <path fill="#81bc06" d="M12 1h10v10H12z"/>
                <path fill="#05a6f0" d="M1 12h10v10H1z"/>
                <path fill="#ffba08" d="M12 12h10v10H12z"/>
              </svg>
              <span>Sign in with Microsoft</span>
            </button>

          </div>

          <!-- Divider -->
          <div class="relative flex items-center justify-center">
            <div class="border-t border-stone-200 w-full"></div>
            <span class="bg-white px-3 text-[11px] font-bold uppercase tracking-wider text-stone-500 relative">Or Badge Serial ID</span>
          </div>

          <!-- Official Law Enforcement Serial Login Form -->
          <form @submit.prevent="handleSerialLogin" class="space-y-4">
            
            <div>
              <label class="block text-xs font-bold text-stone-700 uppercase tracking-wider mb-1.5">
                Operator Badge Serial Number
              </label>
              <div class="relative">
                <input
                  v-model="badgeSerial"
                  type="text"
                  placeholder="e.g. AVNIT-OFFICER-2026"
                  class="w-full pl-10 pr-4 py-2.5 bg-stone-50 border border-stone-300 rounded-xl text-stone-900 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-stone-900 focus:border-stone-900 transition"
                  required
                />
                <KeyRound class="w-4 h-4 text-stone-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-stone-700 uppercase tracking-wider mb-1.5">
                Assigned Enforcement Division
              </label>
              <div class="relative">
                <input
                  v-model="department"
                  type="text"
                  placeholder="e.g. National Highway Enforcement Unit"
                  class="w-full pl-10 pr-4 py-2.5 bg-stone-50 border border-stone-300 rounded-xl text-stone-900 text-sm focus:outline-none focus:ring-2 focus:ring-stone-900 focus:border-stone-900 transition"
                  required
                />
                <FileBadge class="w-4 h-4 text-stone-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <button
              type="submit"
              :disabled="isLoading"
              class="w-full py-3 px-4 rounded-xl bg-stone-900 hover:bg-stone-800 active:bg-black text-stone-100 font-bold text-sm tracking-wide transition-all shadow-lg shadow-stone-900/20 flex items-center justify-center space-x-2 group cursor-pointer"
            >
              <span v-if="isLoading" class="inline-block w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
              <span v-else>Authenticate & Enter Command Center</span>
              <ArrowRight class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </button>

          </form>

          <p class="text-[11px] text-center text-stone-500 leading-normal">
            Official law enforcement system. Unauthorized tampering or proxy access is subject to prosecution under IT Act 2000.
          </p>

        </div>

      </div>

    </main>

    <!-- Bottom Footer -->
    <footer class="w-full border-t border-stone-300/80 bg-white/50 backdrop-blur-sm py-4">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-stone-600 gap-2">
        <p>© 2026 A.V.N.I.T. Intelligent Highway Safety & Motor Vehicle Fraud Detection.</p>
        <p class="font-mono text-[11px]">System Kernel v2.4.0 (WAL-DB Active)</p>
      </div>
    </footer>

  </div>
</template>
