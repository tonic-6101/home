<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Warranty detail page with claim history table (Features 8–10).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { Shield, Clock, FileText, Plus, ArrowLeft, Download } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

interface Claim {
  idx: number
  claim_date: string
  description: string
  outcome: string
  amount_reimbursed?: number
  notes: string
}

interface WarrantyData {
  name: string
  appliance: string
  household: string
  user_role: 'Owner' | 'Adult' | 'Child'
  warranty_type: string
  provider: string
  start_date: string
  end_date: string
  document: string | null
  notes: string
  expiry_status: 'active' | 'expiring_soon' | 'expired'
  days_remaining: number
  claims: Claim[]
}

const route = useRoute()
const router = useRouter()
const warrantyName = computed(() => route.params.name as string)

const warranty = ref<WarrantyData | null>(null)
const loading = ref(true)
const showAddClaim = ref(false)
const savingClaim = ref(false)

// New claim form
const newClaim = ref({
  claim_date: new Date().toISOString().split('T')[0],
  description: '',
  outcome: 'Pending',
  amount_reimbursed: 0,
  notes: '',
})

const canManageClaims = computed(() => {
  const role = warranty.value?.user_role
  return role === 'Owner' || role === 'Adult'
})

const outcomes = ['Pending', 'Accepted', 'Partial', 'Rejected']

async function loadWarranty() {
  loading.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.warranty.get_warranty',
      params: { name: warrantyName.value },
    })
    warranty.value = res
  } catch {
    warranty.value = null
  } finally {
    loading.value = false
  }
}

async function addClaim() {
  if (!newClaim.value.description.trim()) return
  savingClaim.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.warranty.add_claim',
      params: {
        warranty: warrantyName.value,
        ...newClaim.value,
      },
    })
    showAddClaim.value = false
    newClaim.value = {
      claim_date: new Date().toISOString().split('T')[0],
      description: '',
      outcome: 'Pending',
      amount_reimbursed: 0,
      notes: '',
    }
    await loadWarranty()
  } catch {
    // handled by frappe-ui error handler
  } finally {
    savingClaim.value = false
  }
}

const statusBadge = computed(() => {
  if (!warranty.value) return { bg: '', text: '', label: '' }
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
  return map[warranty.value.expiry_status] || map.active
})

const outcomeBadge = (outcome: string) => {
  const map: Record<string, string> = {
    Pending: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    Accepted: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
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

function formatCurrency(amount: number | undefined): string {
  if (amount === undefined || amount === null) return ''
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
  }).format(amount)
}

onMounted(loadWarranty)
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <!-- Back link -->
    <button
      class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-4"
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
    <div v-else-if="!warranty" class="text-center py-16">
      <p class="text-gray-500 dark:text-gray-400">{{ __('Warranty not found') }}</p>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <Shield class="w-5 h-5 text-gray-400" />
            <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
              {{ __(warranty.warranty_type) }}
            </h1>
            <span
              :class="[statusBadge.bg, statusBadge.text]"
              class="text-xs px-2 py-0.5 rounded-full font-medium"
            >
              {{ statusBadge.label }}
            </span>
          </div>
          <p v-if="warranty.provider" class="text-sm text-gray-600 dark:text-gray-400">
            {{ warranty.provider }}
          </p>
        </div>

        <!-- Document download -->
        <a
          v-if="warranty.document"
          :href="warranty.document"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-1 text-sm text-home-600 dark:text-home-400 hover:underline"
        >
          <Download class="w-4 h-4" />
          {{ __('Document') }}
        </a>
      </div>

      <!-- Info grid -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Start Date') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ formatDate(warranty.start_date) }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('End Date') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ formatDate(warranty.end_date) }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Days Remaining') }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
            <template v-if="warranty.expiry_status === 'expired'">{{ __('Expired') }}</template>
            <template v-else>{{ warranty.days_remaining }}</template>
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ __('Appliance') }}</div>
          <router-link
            :to="`/home/items/${warranty.appliance}`"
            class="text-sm font-medium text-home-600 dark:text-home-400 hover:underline"
          >
            {{ warranty.appliance }}
          </router-link>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="warranty.notes" class="mb-6">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ __('Notes') }}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{{ warranty.notes }}</p>
      </div>

      <!-- Claim History -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ __('Claim History') }}
          </h2>
          <Button
            v-if="canManageClaims"
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
          v-if="canManageClaims && showAddClaim"
          class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4 space-y-3"
        >
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Claim Date') }}</label>
              <input
                v-model="newClaim.claim_date"
                type="date"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Outcome') }}</label>
              <select
                v-model="newClaim.outcome"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              >
                <option v-for="o in outcomes" :key="o" :value="o">{{ __(o) }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Description') }}</label>
            <input
              v-model="newClaim.description"
              type="text"
              :placeholder="__('What is the claim for?')"
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Amount Reimbursed') }}</label>
              <input
                v-model.number="newClaim.amount_reimbursed"
                type="number"
                min="0"
                step="0.01"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ __('Notes') }}</label>
              <input
                v-model="newClaim.notes"
                type="text"
                :placeholder="__('Reference numbers, details')"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>
          <div class="flex justify-end gap-2">
            <Button variant="subtle" size="sm" @click="showAddClaim = false">
              {{ __('Cancel') }}
            </Button>
            <Button
              variant="solid"
              size="sm"
              :loading="savingClaim"
              :disabled="!newClaim.description.trim()"
              @click="addClaim"
            >
              {{ __('Save Claim') }}
            </Button>
          </div>
        </div>

        <!-- Claims table -->
        <div v-if="warranty.claims && warranty.claims.length" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700">
                <th class="text-left py-2 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Date') }}
                </th>
                <th class="text-left py-2 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Description') }}
                </th>
                <th class="text-left py-2 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400">
                  {{ __('Outcome') }}
                </th>
                <th
                  v-if="warranty.claims[0]?.amount_reimbursed !== undefined"
                  class="text-right py-2 text-xs font-medium text-gray-500 dark:text-gray-400"
                >
                  {{ __('Amount') }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="claim in warranty.claims"
                :key="claim.idx"
                class="border-b border-gray-100 dark:border-gray-800"
              >
                <td class="py-2.5 pr-4 text-gray-900 dark:text-gray-100 whitespace-nowrap">
                  {{ formatDate(claim.claim_date) }}
                </td>
                <td class="py-2.5 pr-4 text-gray-700 dark:text-gray-300">
                  {{ claim.description }}
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
                <td
                  v-if="claim.amount_reimbursed !== undefined"
                  class="py-2.5 text-right text-gray-900 dark:text-gray-100 whitespace-nowrap"
                >
                  {{ formatCurrency(claim.amount_reimbursed) }}
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
