<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Budget first-time setup wizard — pre-seeds targets from actuals (Feature 20).
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  year: number
  propertyLabel: string
}>()

const emit = defineEmits<{ done: [] }>()

interface Suggestion {
  amount: number
  basis: string
}

const suggestions = ref<Record<string, Suggestion>>({})
const targets = ref<Record<string, number>>({})
const loading = ref(true)
const saving = ref(false)

const categories = [
  'Maintenance & Repairs',
  'Utilities',
  'Insurance',
  'Supplies & Consumables',
  'Garden & Exterior',
  'Improvement Projects',
]

function formatCurrency(value: number): string {
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

async function loadSuggestions() {
  loading.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.budget.suggest_targets',
      params: { property: props.property, year: props.year },
    })
    suggestions.value = res?.suggestions || {}
    // Pre-fill targets from suggestions
    for (const cat of categories) {
      targets.value[cat] = suggestions.value[cat]?.amount || 0
    }
  } catch {
    // Just use zero defaults
    for (const cat of categories) {
      targets.value[cat] = 0
    }
  } finally {
    loading.value = false
  }
}

async function saveTargets() {
  saving.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.budget.save_targets',
      params: {
        property: props.property,
        year: props.year,
        targets: JSON.stringify(targets.value),
      },
    })
    emit('done')
  } catch (e: any) {
    alert(e.message || __('Failed to save targets'))
  } finally {
    saving.value = false
  }
}

async function skipSetup() {
  // Save with null targets (actuals-only mode)
  saving.value = true
  try {
    const nullTargets: Record<string, number | null> = {}
    for (const cat of categories) {
      nullTargets[cat] = 0
    }
    await frappeRequest({
      url: '/api/method/home.api.budget.save_targets',
      params: {
        property: props.property,
        year: props.year,
        targets: JSON.stringify(nullTargets),
      },
    })
    emit('done')
  } catch (e: any) {
    alert(e.message || __('Failed'))
  } finally {
    saving.value = false
  }
}

const priorYearTotal = ref(0)

onMounted(async () => {
  await loadSuggestions()
  // Calculate prior-year total for display
  priorYearTotal.value = Object.values(suggestions.value).reduce(
    (sum, s) => sum + (s.amount || 0), 0
  )
})
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
    <h1 class="text-h1 text-gray-900 dark:text-gray-100 mb-2">
      {{ __('Budget Overview') }}
    </h1>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400 py-4">
      {{ __('Loading suggestions…') }}
    </div>

    <template v-else>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">
        <template v-if="priorYearTotal > 0">
          {{ __('You spent') }} {{ formatCurrency(priorYearTotal) }} {{ __('on your home last year.') }}
        </template>
        {{ __('Set annual targets to track whether you\'re on pace.') }}
      </p>
      <p v-if="priorYearTotal > 0" class="text-xs text-gray-400 dark:text-gray-500 mb-5">
        {{ __('We\'ve suggested targets based on last year:') }}
      </p>

      <div class="space-y-3">
        <div
          v-for="cat in categories"
          :key="cat"
          class="flex items-center gap-3"
        >
          <label class="flex-1 text-sm text-gray-700 dark:text-gray-300 min-w-0">
            {{ __(cat) }}
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">€</span>
            <input
              v-model.number="targets[cat]"
              type="number"
              min="0"
              step="50"
              class="w-32 border border-gray-300 dark:border-gray-600 rounded-lg pl-7 pr-3 py-1.5 text-sm text-right
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <span
            v-if="suggestions[cat]?.basis"
            class="text-xs text-gray-400 dark:text-gray-500 w-32 truncate"
            :title="suggestions[cat].basis"
          >
            ({{ __(suggestions[cat].basis) }})
          </span>
        </div>
      </div>

      <div class="flex items-center gap-3 mt-6">
        <Button variant="solid" :loading="saving" @click="saveTargets">
          {{ __('Save budget targets') }}
        </Button>
        <Button variant="outline" :loading="saving" @click="skipSetup">
          {{ __('Skip — show actuals only') }}
        </Button>
      </div>
    </template>
  </div>
</template>
