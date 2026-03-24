<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Home health score widget — score, band, dot indicator, expandable breakdown (Feature 36).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { AlertTriangle, Info, ChevronDown, ChevronUp } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
}>()

const router = useRouter()

interface Factor {
  key: string
  label: string
  count: number
  deduction: number
  severity: string
  action_route?: string
  financial: boolean
}

interface HealthScore {
  score: number
  band: string
  colour: string
  total_deduction: number
  factors: Factor[]
}

const health = ref<HealthScore | null>(null)
const loading = ref(true)
const expanded = ref(false)

const DOT_COUNT = 12

const filledDots = computed(() => {
  if (!health.value) return 0
  return Math.round(health.value.score / 100 * DOT_COUNT)
})

const colourClasses = computed(() => {
  const c = health.value?.colour
  if (c === 'green') return { dot: 'bg-green-500', text: 'text-green-600 dark:text-green-400', ring: 'ring-green-500/20' }
  if (c === 'amber') return { dot: 'bg-amber-500', text: 'text-amber-600 dark:text-amber-400', ring: 'ring-amber-500/20' }
  return { dot: 'bg-red-500', text: 'text-red-600 dark:text-red-400', ring: 'ring-red-500/20' }
})

const bandLabel = computed(() => {
  if (!health.value) return ''
  const labels: Record<string, string> = {
    'Excellent': __('Everything is in order'),
    'Good': __('Looking good — minor items to address'),
    'Fair': __('Some items need attention'),
    'Needs attention': __('Several issues to address'),
    'Poor': __('Significant issues require action'),
  }
  return labels[health.value.band] || health.value.band
})

function severityIcon(severity: string) {
  return severity === 'low' ? Info : AlertTriangle
}

function navigate(route: string | undefined) {
  if (!route) return
  if (route.startsWith('/home/')) {
    router.push(route)
  } else {
    window.location.href = route
  }
}

async function loadScore() {
  loading.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.health.get_health_score',
      params: { property: props.property },
    })
    health.value = res
  } catch {
    health.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadScore)
</script>

<template>
  <div v-if="loading" class="animate-pulse h-12 bg-gray-100 dark:bg-gray-700 rounded-lg" />

  <div v-else-if="health" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <!-- Score header row -->
    <div class="flex items-center gap-4">
      <!-- Score number -->
      <div
        class="flex items-center justify-center w-12 h-12 rounded-full ring-4"
        :class="[colourClasses.ring]"
      >
        <span class="text-lg font-bold" :class="colourClasses.text">
          {{ health.score }}
        </span>
      </div>

      <!-- Band + dots -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ __('Health score') }}
          </span>
          <span class="text-sm font-medium" :class="colourClasses.text">
            {{ __(health.band) }}
          </span>
        </div>

        <!-- Dot indicator -->
        <div class="flex items-center gap-0.5">
          <span
            v-for="i in DOT_COUNT"
            :key="i"
            class="w-2 h-2 rounded-full"
            :class="i <= filledDots ? colourClasses.dot : 'bg-gray-200 dark:bg-gray-600'"
          />
        </div>
      </div>

      <!-- Expand toggle -->
      <button
        v-if="health.factors.length"
        @click="expanded = !expanded"
        class="flex items-center gap-1 text-xs text-accent-600 dark:text-accent-400 hover:underline flex-shrink-0"
      >
        {{ expanded ? __('Hide') : __('See what\'s affecting it') }}
        <component :is="expanded ? ChevronUp : ChevronDown" class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Perfect score message -->
    <p
      v-if="health.score === 100"
      class="text-sm text-gray-500 dark:text-gray-400 mt-2"
    >
      {{ __('Everything is in order.') }}
    </p>

    <!-- Expandable factor breakdown -->
    <div v-if="expanded && health.factors.length" class="mt-4 space-y-2">
      <div class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">
        {{ __('What\'s affecting it:') }}
      </div>

      <div
        v-for="factor in health.factors"
        :key="factor.key"
        :class="[
          'flex items-center gap-2 py-1.5 px-2 -mx-2 rounded text-sm',
          factor.action_route ? 'hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer' : '',
        ]"
        @click="navigate(factor.action_route)"
      >
        <component
          :is="severityIcon(factor.severity)"
          class="w-4 h-4 flex-shrink-0"
          :class="factor.severity === 'low'
            ? 'text-blue-400 dark:text-blue-500'
            : 'text-amber-500 dark:text-amber-400'"
        />
        <span class="flex-1 text-gray-700 dark:text-gray-300">
          {{ factor.label }}
        </span>
        <span class="text-xs text-gray-400 dark:text-gray-500 font-mono tabular-nums flex-shrink-0">
          −{{ factor.deduction }}
        </span>
        <span
          v-if="factor.action_route"
          class="text-xs text-accent-600 dark:text-accent-400 flex-shrink-0"
        >
          →
        </span>
      </div>

      <div class="text-xs text-gray-400 dark:text-gray-500 pt-1 border-t border-gray-100 dark:border-gray-700">
        {{ __('Total deductions:') }} −{{ health.total_deduction }}
        · {{ __('Score:') }} 100 − {{ health.total_deduction }} = {{ health.score }}
      </div>
    </div>
  </div>
</template>
