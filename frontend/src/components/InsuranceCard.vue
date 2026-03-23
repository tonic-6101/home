<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Insurance policy card for the policy list (Feature 28).
-->
<script setup lang="ts">
import { computed } from 'vue'
import { Shield, Home, Package, Scale, Gavel, Droplets, HelpCircle, AlertTriangle } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

export interface PolicySummary {
  name: string
  policy_name: string
  policy_type: string
  provider: string
  policy_number: string
  start_date: string
  end_date: string
  premium_annual: number | null
  coverage_amount: number | null
  auto_renews: boolean
  renewal_notice_days: number
  renewal_status: 'active' | 'renewing_soon' | 'expired'
  days_to_renewal: number
  document: string | null
}

const props = defineProps<{
  policy: PolicySummary
}>()

const typeIcon = computed(() => {
  const map: Record<string, any> = {
    Buildings: Home,
    Contents: Package,
    Liability: Scale,
    'Legal Protection': Gavel,
    Flood: Droplets,
  }
  return map[props.policy.policy_type] || HelpCircle
})

const statusBadge = computed(() => {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    active: {
      bg: 'bg-gray-100 dark:bg-gray-700',
      text: 'text-gray-700 dark:text-gray-300',
      label: __('Active'),
    },
    renewing_soon: {
      bg: 'bg-amber-100 dark:bg-amber-900/30',
      text: 'text-amber-700 dark:text-amber-300',
      label: __('Renewing soon'),
    },
    expired: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      text: 'text-red-700 dark:text-red-300',
      label: __('Expired'),
    },
  }
  return map[props.policy.renewal_status] || map.active
})

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
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
</script>

<template>
  <router-link
    :to="`/home/insurance/${policy.name}`"
    class="block rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800
           hover:shadow-md transition-shadow no-underline p-4"
  >
    <!-- Header -->
    <div class="flex items-start justify-between mb-1">
      <div class="flex items-center gap-2 min-w-0">
        <component :is="typeIcon" class="w-4 h-4 text-gray-400 flex-shrink-0" />
        <span class="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
          {{ policy.policy_name }}
        </span>
      </div>
      <span
        :class="[statusBadge.bg, statusBadge.text]"
        class="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0"
      >
        {{ statusBadge.label }}
      </span>
    </div>

    <!-- Provider + policy number -->
    <div class="text-sm text-gray-600 dark:text-gray-400">
      {{ policy.provider }}
      <template v-if="policy.policy_number"> · {{ policy.policy_number }}</template>
    </div>

    <!-- Renewal date + premium -->
    <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
      {{ __('Renews') }} {{ formatDate(policy.end_date) }}
      <template v-if="policy.premium_annual">
        · {{ formatCurrency(policy.premium_annual) }}/{{ __('yr') }}
      </template>
    </div>

    <!-- Coverage -->
    <div v-if="policy.coverage_amount" class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
      {{ __('Coverage') }}: {{ formatCurrency(policy.coverage_amount) }}
    </div>

    <!-- Auto-renew flag -->
    <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
      <template v-if="policy.auto_renews">{{ __('Auto-renews') }} &#10003;</template>
      <template v-else>{{ __('Manual renewal') }}</template>
    </div>

    <!-- Renewal warning banner -->
    <div
      v-if="policy.renewal_status === 'renewing_soon'"
      class="mt-2 flex items-center gap-1.5 text-xs text-amber-700 dark:text-amber-300
             bg-amber-50 dark:bg-amber-900/20 rounded px-2 py-1.5"
    >
      <AlertTriangle class="w-3.5 h-3.5 flex-shrink-0" />
      {{ __('Renews in') }} {{ policy.days_to_renewal }} {{ __('days') }}
    </div>
  </router-link>
</template>
