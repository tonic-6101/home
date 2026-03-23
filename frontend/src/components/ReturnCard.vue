<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Purchase return card for the return list (Feature 18).
-->
<script setup lang="ts">
import { computed } from 'vue'
import { RotateCcw, AlertTriangle } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

export interface ReturnSummary {
  name: string
  item_description: string
  retailer: string
  return_date: string
  return_reason: string
  refund_status: 'Pending' | 'Received' | 'Partially Received' | 'Denied'
  refund_expected: number | null
  refund_amount_received: number | null
  refund_received_date: string | null
  linked_item: string | null
  days_since_return: number
  overdue_followup: boolean
}

const props = defineProps<{
  returnItem: ReturnSummary
}>()

defineEmits<{ markReceived: [name: string] }>()

const statusBadge = computed(() => {
  const map: Record<string, { bg: string; text: string; icon: string }> = {
    Pending: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      text: 'text-red-700 dark:text-red-300',
      icon: '🔴',
    },
    Received: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      text: 'text-green-700 dark:text-green-300',
      icon: '✓',
    },
    'Partially Received': {
      bg: 'bg-amber-100 dark:bg-amber-900/30',
      text: 'text-amber-700 dark:text-amber-300',
      icon: '⚠',
    },
    Denied: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      text: 'text-red-700 dark:text-red-300',
      icon: '✗',
    },
  }
  return map[props.returnItem.refund_status] || map.Pending
})

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
  })
}

function formatCurrency(amount: number | null): string {
  if (amount === null || amount === undefined) return ''
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
  }).format(amount)
}

const refundLabel = computed(() => {
  const r = props.returnItem
  if (r.refund_status === 'Received' && r.refund_amount_received != null) {
    return `${__('Refund received')}: ${formatCurrency(r.refund_amount_received)}`
  }
  if (r.refund_status === 'Partially Received' && r.refund_amount_received != null) {
    return `${formatCurrency(r.refund_amount_received)} ${__('of')} ${formatCurrency(r.refund_expected)}`
  }
  if (r.refund_status === 'Denied') {
    return __('Refund denied')
  }
  if (r.refund_expected) {
    return `${__('Refund expected')}: ${formatCurrency(r.refund_expected)}`
  }
  return ''
})
</script>

<template>
  <div
    class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4"
  >
    <!-- Header row -->
    <div class="flex items-start justify-between mb-1">
      <div class="flex items-center gap-2 min-w-0">
        <RotateCcw class="w-4 h-4 text-gray-400 flex-shrink-0" />
        <span class="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
          {{ returnItem.item_description }}
        </span>
      </div>
      <button
        v-if="returnItem.refund_status === 'Pending'"
        :class="[statusBadge.bg, statusBadge.text]"
        class="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 hover:opacity-80 cursor-pointer"
        @click.stop="$emit('markReceived', returnItem.name)"
      >
        {{ statusBadge.icon }} {{ __(returnItem.refund_status) }}
      </button>
      <span
        v-else
        :class="[statusBadge.bg, statusBadge.text]"
        class="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0"
        :style="returnItem.refund_status === 'Denied' ? 'text-decoration: line-through' : ''"
      >
        {{ statusBadge.icon }} {{ __(returnItem.refund_status) }}
      </span>
    </div>

    <!-- Details -->
    <div class="text-sm text-gray-600 dark:text-gray-400">
      {{ __('Returned') }} {{ formatDate(returnItem.return_date) }}
      <template v-if="returnItem.retailer"> · {{ returnItem.retailer }}</template>
    </div>

    <div class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
      {{ __(returnItem.return_reason) }}
      <template v-if="refundLabel"> · {{ refundLabel }}</template>
    </div>

    <!-- Overdue follow-up banner -->
    <div
      v-if="returnItem.overdue_followup"
      class="mt-2 flex items-center gap-1.5 text-xs text-amber-700 dark:text-amber-300
             bg-amber-50 dark:bg-amber-900/20 rounded px-2 py-1.5"
    >
      <AlertTriangle class="w-3.5 h-3.5 flex-shrink-0" />
      {{ returnItem.days_since_return }} {{ __('days since return — follow up') }}
    </div>
  </div>
</template>
