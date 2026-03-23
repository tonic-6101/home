<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Warranty card for item detail warranty section (Features 8–10).
-->
<script setup lang="ts">
import { computed } from 'vue'
import { Shield, Scale, Clock, FileText } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

export interface WarrantySummary {
  name: string
  warranty_type: string
  provider: string
  start_date: string
  end_date: string
  burden_of_proof_date: string | null
  document: string | null
  expiry_status: 'active' | 'expiring_soon' | 'expired'
  days_remaining: number
  claim_count: number
  last_claim_outcome: string | null
  item: string
}

const props = defineProps<{
  warranty: WarrantySummary
}>()

const isLegal = computed(() => props.warranty.warranty_type === 'Legal')

const statusBadge = computed(() => {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    active: {
      bg: 'bg-gray-100 dark:bg-gray-700',
      text: 'text-gray-700 dark:text-gray-300',
      label: __('Active'),
    },
    expiring_soon: {
      bg: 'bg-amber-100 dark:bg-amber-900/30',
      text: 'text-amber-700 dark:text-amber-300',
      label: __('Expiring soon'),
    },
    expired: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      text: 'text-red-700 dark:text-red-300',
      label: __('Expired'),
    },
  }
  return map[props.warranty.expiry_status] || map.active
})

const progressPct = computed(() => {
  if (!props.warranty.start_date || !props.warranty.end_date) return 0
  const start = new Date(props.warranty.start_date).getTime()
  const end = new Date(props.warranty.end_date).getTime()
  const now = Date.now()
  if (now >= end) return 100
  if (now <= start) return 0
  return Math.round(((now - start) / (end - start)) * 100)
})

const progressColor = computed(() => {
  const status = props.warranty.expiry_status
  if (status === 'expired') return 'bg-red-500'
  if (status === 'expiring_soon') return 'bg-amber-500'
  return 'bg-green-500'
})

// Burden of proof progress (Legal warranties only)
const burdenPassed = computed(() => {
  if (!props.warranty.burden_of_proof_date) return false
  return new Date(props.warranty.burden_of_proof_date).getTime() <= Date.now()
})

const burdenDaysRemaining = computed(() => {
  if (!props.warranty.burden_of_proof_date) return 0
  const diff = new Date(props.warranty.burden_of_proof_date).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
})

const burdenProgressPct = computed(() => {
  if (!props.warranty.start_date || !props.warranty.burden_of_proof_date) return 0
  const start = new Date(props.warranty.start_date).getTime()
  const end = new Date(props.warranty.burden_of_proof_date).getTime()
  const now = Date.now()
  if (now >= end) return 100
  if (now <= start) return 0
  return Math.round(((now - start) / (end - start)) * 100)
})

const claimSummary = computed(() => {
  if (!props.warranty.claim_count) return __('No claims')
  const count = props.warranty.claim_count
  const outcome = props.warranty.last_claim_outcome
  if (outcome) {
    return `${count} ${count === 1 ? __('claim') : __('claims')} · ${__(outcome)}`
  }
  return `${count} ${count === 1 ? __('claim') : __('claims')}`
})

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<template>
  <div
    class="block rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4"
  >
    <!-- Header -->
    <div class="flex items-start justify-between mb-2">
      <div class="flex items-center gap-2">
        <Scale v-if="isLegal" class="w-4 h-4 text-gray-400" />
        <Shield v-else class="w-4 h-4 text-gray-400" />
        <span class="font-medium text-gray-900 dark:text-gray-100 text-sm">
          {{ isLegal ? __('Legal Warranty (Gewährleistung)') : __(warranty.warranty_type) }}
        </span>
      </div>
      <span
        :class="[statusBadge.bg, statusBadge.text]"
        class="text-xs px-2 py-0.5 rounded-full font-medium"
      >
        {{ statusBadge.label }}
      </span>
    </div>

    <!-- Provider + expiry -->
    <div class="text-sm text-gray-600 dark:text-gray-400 mb-3">
      <span v-if="warranty.provider">{{ warranty.provider }} · </span>
      {{ __('Expires') }} {{ formatDate(warranty.end_date) }}
    </div>

    <!-- Progress bar -->
    <div class="w-full h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full mb-2">
      <div
        :class="progressColor"
        class="h-full rounded-full transition-all"
        :style="{ width: `${progressPct}%` }"
      />
    </div>

    <!-- Burden of proof (Legal warranties only) -->
    <template v-if="isLegal && warranty.burden_of_proof_date">
      <div class="mt-3 mb-2 text-xs text-gray-600 dark:text-gray-400">
        {{ __('Burden of proof shifts') }} {{ formatDate(warranty.burden_of_proof_date) }}
      </div>
      <div class="w-full h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full mb-1">
        <div
          :class="burdenPassed ? 'bg-amber-500' : 'bg-green-500'"
          class="h-full rounded-full transition-all"
          :style="{ width: `${burdenProgressPct}%` }"
        />
      </div>
      <div class="text-xs mb-2" :class="burdenPassed ? 'text-amber-600 dark:text-amber-400' : 'text-green-600 dark:text-green-400'">
        <template v-if="burdenPassed">{{ __('buyer proves') }}</template>
        <template v-else>{{ burdenDaysRemaining }}d — {{ __('seller proves') }}</template>
      </div>
    </template>

    <!-- Footer -->
    <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
      <span class="flex items-center gap-1">
        <Clock class="w-3 h-3" />
        <template v-if="warranty.expiry_status === 'expired'">
          {{ __('Expired') }}
        </template>
        <template v-else>
          {{ warranty.days_remaining }} {{ __('days left') }}
        </template>
      </span>
      <span>{{ claimSummary }}</span>
    </div>
  </div>
</template>
