<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { __ } from '@/composables/useTranslate'

export interface ScanResult {
  brand: string
  model: string
  serial_number: string
  category: string
  confidence: Record<string, 'high' | 'low'>
  method: string
}

export interface ConfirmedResult {
  brand: string
  model: string
  serial_number: string
  category: string
  expected_lifespan_years: number | null
}

const props = defineProps<{
  result: ScanResult
  lifespanYears: number | null
  imagePreview?: string
}>()

const emit = defineEmits<{
  confirm: [data: ConfirmedResult]
  retry: []
  manual: []
}>()

const brand = ref(props.result.brand)
const model = ref(props.result.model)
const serialNumber = ref(props.result.serial_number)
const category = ref(props.result.category)
const lifespanYears = ref(props.lifespanYears)

const categories = [
  'White Goods', 'HVAC', 'Heating', 'Electronics', 'Kitchen', 'Plumbing', 'Other'
]

function confidenceClass(field: string): string {
  const level = props.result.confidence[field]
  if (level === 'high') return 'text-green-600 dark:text-green-400'
  return 'text-amber-600 dark:text-amber-400'
}

function confidenceIcon(field: string): string {
  return props.result.confidence[field] === 'high' ? '✓' : '⚠'
}

function handleConfirm(): void {
  emit('confirm', {
    brand: brand.value,
    model: model.value,
    serial_number: serialNumber.value,
    category: category.value,
    expected_lifespan_years: lifespanYears.value,
  })
}
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 max-w-md w-full mx-auto">
    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
      {{ __('Confirm Appliance Details') }}
    </h2>

    <!-- Image preview -->
    <div v-if="imagePreview" class="mb-4 flex justify-center">
      <img
        :src="imagePreview"
        :alt="__('Scanned image')"
        class="w-32 h-32 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
      />
    </div>

    <!-- Fields -->
    <div class="space-y-3">
      <div>
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-1">
          {{ __('Brand') }}
          <span :class="confidenceClass('brand')" class="text-xs">{{ confidenceIcon('brand') }}</span>
        </label>
        <input
          v-model="brand"
          type="text"
          class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-accent-500 focus:border-transparent"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-1">
          {{ __('Model') }}
          <span :class="confidenceClass('model')" class="text-xs">{{ confidenceIcon('model') }}</span>
        </label>
        <input
          v-model="model"
          type="text"
          class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-accent-500 focus:border-transparent"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-1">
          {{ __('Serial Number') }}
          <span :class="confidenceClass('serial_number')" class="text-xs">{{ confidenceIcon('serial_number') }}</span>
        </label>
        <input
          v-model="serialNumber"
          type="text"
          class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-accent-500 focus:border-transparent"
        />
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-1">
          {{ __('Category') }}
          <span class="text-xs text-amber-600 dark:text-amber-400">⚠</span>
        </label>
        <select
          v-model="category"
          class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-accent-500 focus:border-transparent"
        >
          <option value="">{{ __('Select category') }}</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ __(cat) }}</option>
        </select>
      </div>

      <div>
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ __('Expected Lifespan (years)') }}
        </label>
        <input
          v-model.number="lifespanYears"
          type="number"
          min="1"
          max="50"
          class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-accent-500 focus:border-transparent"
        />
      </div>
    </div>

    <!-- Actions -->
    <div class="mt-6 space-y-2">
      <button
        class="w-full px-4 py-2.5 bg-accent-500 text-white rounded-lg font-medium hover:bg-accent-600 transition-colors"
        @click="handleConfirm"
      >
        {{ __('Looks good') }}
      </button>
      <div class="flex gap-2">
        <button
          class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          @click="$emit('retry')"
        >
          {{ __('Try again') }}
        </button>
        <button
          class="flex-1 px-4 py-2 text-gray-500 dark:text-gray-400 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          @click="$emit('manual')"
        >
          {{ __('Enter manually') }}
        </button>
      </div>
    </div>
  </div>
</template>
