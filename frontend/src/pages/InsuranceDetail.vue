<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Insurance policy detail page with claim history (Feature 28).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  Shield, Home, Package, Scale, Gavel, Droplets, HelpCircle,
  ArrowLeft, Download, Plus, FileText, AlertTriangle,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

interface Claim {
  idx: number
  claim_date: string
  incident_description: string
  outcome: string
  claim_amount?: number
  payout_amount?: number
  notes: string
}

interface PolicyData {
  name: string
  property: string
  household: string
  policy_name: string
  policy_type: string
  provider: string
  policy_number: string
  start_date: string
  end_date: string
  premium_annual: number | null
  coverage_amount: number | null
  coverage_notes: string
  auto_renews: boolean
  renewal_notice_days: number
  document: string | null
  notes: string
  renewal_status: 'active' | 'renewing_soon' | 'expired'
  days_to_renewal: number
  claims: Claim[]
}

const route = useRoute()
const router = useRouter()
const policyName = computed(() => route.params.name as string)

const policy = ref<PolicyData | null>(null)
const loading = ref(true)
const showAddClaim = ref(false)
const savingClaim = ref(false)

const newClaim = ref({
  claim_date: new Date().toISOString().split('T')[0],
  incident_description: '',
  outcome: 'Pending',
  claim_amount: 0,
  payout_amount: 0,
  notes: '',
})

const outcomes = ['Pending', 'Approved', 'Partial', 'Rejected']

async function loadPolicy() {
  loading.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.insurance.get_policy',
      params: { name: policyName.value },
    })
    policy.value = res
  } catch {
    policy.value = null
  } finally {
    loading.value = false
  }
}

async function addClaim() {
  if (!newClaim.value.incident_description.trim()) return
  savingClaim.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.insurance.add_claim',
      params: {
        policy: policyName.value,
        ...newClaim.value,
      },
    })
    showAddClaim.value = false
    newClaim.value = {
      claim_date: new Date().toISOString().split('T')[0],
      incident_description: '',
      outcome: 'Pending',
      claim_amount: 0,
      payout_amount: 0,
      notes: '',
    }
    await loadPolicy()
  } catch {
    // handled by frappe-ui error handler
  } finally {
    savingClaim.value = false
  }
}

const typeIcon = computed(() => {
  if (!policy.value) return Shield
  const map: Record<string, any> = {
    Buildings: Home,
    Contents: Package,
    Liability: Scale,
    'Legal Protection': Gavel,
    Flood: Droplets,
  }
  return map[policy.value.policy_type] || HelpCircle
})

const statusBadge = computed(() => {
  if (!policy.value) return { bg: '', text: '', label: '' }
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
  return map[policy.value.renewal_status] || map.active
})

const outcomeBadge = (outcome: string) => {
  const map: Record<string, string> = {
    Pending: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    Approved: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
    Partial: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300',
    Rejected: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
  }
  return map[outcome] || map.Pending
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatCurrency(amount: number | undefined | null): string {
  if (amount === undefined || amount === null) return ''
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
  }).format(amount)
}

onMounted(loadPolicy)
</script>

<template>
  <div class="p-6 max-w-3xl">
    <!-- Back link -->
    <button
      class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
             hover:text-gray-700 dark:hover:text-gray-300 mb-4"
      @click="router.back()"
    >
      <ArrowLeft class="w-4 h-4" />
      {{ __('Back') }}
    </button>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- Not found -->
    <div v-else-if="!policy" class="text-center py-16">
      <p class="text-gray-500 dark:text-gray-400">{{ __('Policy not found') }}</p>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <component :is="typeIcon" class="w-5 h-5 text-gray-400" />
            <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {{ policy.policy_name }}
            </h1>
            <span
              :class="[statusBadge.bg, statusBadge.text]"
              class="text-xs px-2 py-0.5 rounded-full font-medium"
            >
              {{ statusBadge.label }}
            </span>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ __(policy.policy_type) }}
            <template v-if="policy.renewal_status === 'renewing_soon'">
              · {{ __('Renews in') }} {{ policy.days_to_renewal }} {{ __('days') }}
            </template>
          </p>
        </div>

        <!-- Document download -->
        <a
          v-if="policy.document"
          :href="policy.document"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-1 text-sm text-accent-600 dark:text-accent-400 hover:underline"
        >
          <Download class="w-4 h-4" />
          {{ __('Policy PDF') }}
        </a>
      </div>

      <!-- Renewal warning -->
      <div
        v-if="policy.renewal_status === 'renewing_soon'"
        class="mb-6 flex items-center gap-2 text-sm text-amber-700 dark:text-amber-300
               bg-amber-50 dark:bg-amber-900/20 rounded-lg px-3 py-2"
      >
        <AlertTriangle class="w-4 h-4 flex-shrink-0" />
        {{ __('Renews in') }} {{ policy.days_to_renewal }} {{ __('days') }}
        · {{ policy.auto_renews ? __('Auto-renews') : __('Manual renewal required') }}
      </div>

      <!-- Info grid -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Provider') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ policy.provider }}</div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Policy Number') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ policy.policy_number || '—' }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Period') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ formatDate(policy.start_date) }} – {{ formatDate(policy.end_date) }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Premium') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            <template v-if="policy.premium_annual">
              {{ formatCurrency(policy.premium_annual) }} / {{ __('year') }}
            </template>
            <template v-else>—</template>
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Coverage') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ policy.coverage_amount ? formatCurrency(policy.coverage_amount) : '—' }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Auto-renews') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ policy.auto_renews ? __('Yes') : __('No — manual renewal') }}
          </div>
        </div>
      </div>

      <!-- Coverage notes -->
      <div v-if="policy.coverage_notes" class="mb-6">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ __('Coverage Notes') }}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{{ policy.coverage_notes }}</p>
      </div>

      <!-- Notes -->
      <div v-if="policy.notes" class="mb-6">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ __('Notes') }}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{{ policy.notes }}</p>
      </div>

      <!-- Claims -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-white">
            {{ __('Claims') }}
          </h2>
          <Button
            variant="outline"
            size="sm"
            @click="showAddClaim = !showAddClaim"
          >
            <Plus class="w-3.5 h-3.5 mr-1" />
            {{ __('Add Claim') }}
          </Button>
        </div>

        <!-- Add claim form -->
        <div
          v-if="showAddClaim"
          class="bg-gray-50 dark:bg-gray-800 rounded-lg p-5 mb-4 space-y-3"
        >
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Claim Date') }}</label>
              <input
                v-model="newClaim.claim_date"
                type="date"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Outcome') }}</label>
              <select
                v-model="newClaim.outcome"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              >
                <option v-for="o in outcomes" :key="o" :value="o">{{ __(o) }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('What happened') }}</label>
            <input
              v-model="newClaim.incident_description"
              type="text"
              :placeholder="__('e.g. Storm damage to roof')"
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Amount Claimed') }}</label>
              <input
                v-model.number="newClaim.claim_amount"
                type="number"
                min="0"
                step="0.01"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Payout Amount') }}</label>
              <input
                v-model.number="newClaim.payout_amount"
                type="number"
                min="0"
                step="0.01"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>
          <div>
            <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Notes') }}</label>
            <input
              v-model="newClaim.notes"
              type="text"
              :placeholder="__('Reference numbers, loss adjuster notes')"
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
            />
          </div>
          <div class="flex justify-end gap-2">
            <Button variant="subtle" size="sm" @click="showAddClaim = false">
              {{ __('Cancel') }}
            </Button>
            <Button
              variant="solid"
              size="sm"
              :loading="savingClaim"
              :disabled="!newClaim.incident_description.trim()"
              @click="addClaim"
            >
              {{ __('Save Claim') }}
            </Button>
          </div>
        </div>

        <!-- Claims table -->
        <div v-if="policy.claims && policy.claims.length" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700">
                <th class="text-left py-2 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Date') }}
                </th>
                <th class="text-left py-2 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Incident') }}
                </th>
                <th class="text-left py-2 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Outcome') }}
                </th>
                <th class="text-right py-2 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Claimed') }}
                </th>
                <th class="text-right py-2 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Paid Out') }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="claim in policy.claims"
                :key="claim.idx"
                class="border-b border-gray-100 dark:border-gray-800"
              >
                <td class="py-2.5 pr-4 text-gray-900 dark:text-gray-100 whitespace-nowrap">
                  {{ formatDate(claim.claim_date) }}
                </td>
                <td class="py-2.5 pr-4 text-gray-700 dark:text-gray-300">
                  {{ claim.incident_description }}
                  <div v-if="claim.notes" class="text-xs text-gray-400 mt-0.5">{{ claim.notes }}</div>
                </td>
                <td class="py-2.5 pr-4">
                  <span
                    :class="outcomeBadge(claim.outcome)"
                    class="text-xs px-2 py-0.5 rounded-full font-medium"
                  >
                    {{ __(claim.outcome) }}
                  </span>
                </td>
                <td class="py-2.5 pr-4 text-right text-gray-900 dark:text-gray-100 whitespace-nowrap">
                  {{ formatCurrency(claim.claim_amount) }}
                </td>
                <td class="py-2.5 text-right text-gray-900 dark:text-gray-100 whitespace-nowrap">
                  {{ formatCurrency(claim.payout_amount) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty claims -->
        <div
          v-else
          class="text-center py-8 text-sm text-gray-500 dark:text-gray-400"
        >
          <FileText class="w-8 h-8 mx-auto mb-2 text-gray-300 dark:text-gray-600" />
          {{ __('No claims recorded') }}
        </div>
      </div>
    </template>
  </div>
</template>
