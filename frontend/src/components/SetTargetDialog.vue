<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Per-category budget target editing modal (Feature 20).
-->
<script setup lang="ts">
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  year: number
  category: string
  currentTarget: number
  suggestion: { amount: number; basis: string } | null
}>()

const emit = defineEmits<{ close: []; saved: [] }>()

const target = ref(props.currentTarget || 0)
const saving = ref(false)

function formatCurrency(value: number): string {
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

function useSuggestion() {
  if (props.suggestion) {
    target.value = props.suggestion.amount
  }
}

async function save() {
  saving.value = true
  try {
    // Fetch current budget to get all existing targets, then update this one
    const res = await frappeRequest({
      url: '/api/method/home.api.budget.get_overview',
      params: { property: props.property, year: props.year },
    })
    const targets: Record<string, number> = {}
    for (const line of res?.lines || []) {
      targets[line.category] = line.annual_target || 0
    }
    targets[props.category] = target.value

    await frappeRequest({
      url: '/api/method/home.api.budget.save_targets',
      params: {
        property: props.property,
        year: props.year,
        targets: JSON.stringify(targets),
      },
    })
    emit('saved')
  } catch (e: any) {
    alert(e.message || __('Failed to save'))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-sm mx-4 p-6"
      @keydown.escape="emit('close')"
    >
      <h2 class="text-h3 text-gray-900 dark:text-gray-100 mb-1">
        {{ __('Set annual target') }}
      </h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {{ __(category) }}
      </p>

      <div class="mb-4">
        <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
          {{ __('Annual target') }}
        </label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">€</span>
          <input
            v-model.number="target"
            type="number"
            min="0"
            step="50"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-7 pr-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @keyup.enter="save"
          />
        </div>
      </div>

      <div v-if="suggestion && suggestion.amount > 0" class="mb-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="text-sm text-gray-600 dark:text-gray-400">
          {{ __('Suggestion:') }} {{ formatCurrency(suggestion.amount) }}
        </div>
        <div class="text-xs text-gray-400 dark:text-gray-500 mb-2">
          ({{ __(suggestion.basis) }})
        </div>
        <button
          @click="useSuggestion"
          class="text-xs text-accent-600 dark:text-accent-400 hover:underline"
        >
          {{ __('Use suggestion') }}
        </button>
      </div>

      <div class="flex justify-end gap-2">
        <button
          class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
          @click="emit('close')"
        >
          {{ __('Cancel') }}
        </button>
        <button
          class="rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? __('Saving…') : __('Save') }}
        </button>
      </div>
    </div>
  </div>
</template>
