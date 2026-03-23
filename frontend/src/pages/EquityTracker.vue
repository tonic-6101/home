<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Home equity tracker (Feature 22) — property value vs mortgage balance.
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { ArrowLeft, TrendingUp, Landmark, PiggyBank } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()

const data = ref<any>(null)
const loading = ref(true)
const showUpdateForm = ref(false)
const newValue = ref('')
const newNote = ref('')
const saving = ref(false)

function formatCurrency(value: number | null): string {
  if (value == null) return '—'
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDate(d: string): string {
  if (!d) return ''
  return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short' })
}

async function loadEquity() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.equity.get_equity',
      params: { property: propName },
    })
    data.value = res
  } catch {
    data.value = null
  } finally {
    loading.value = false
  }
}

async function updateValue() {
  const val = parseFloat(newValue.value)
  if (isNaN(val) || val <= 0) return
  saving.value = true
  try {
    const propName = await loadPropertyName()
    await frappeRequest({
      url: '/api/method/home.api.equity.update_value',
      params: { property: propName, estimated_value: val, note: newNote.value || '' },
    })
    showUpdateForm.value = false
    newValue.value = ''
    newNote.value = ''
    await loadEquity()
  } catch (e: any) {
    alert(e.message || __('Failed to update'))
  } finally {
    saving.value = false
  }
}

const equityPct = computed(() => {
  if (!data.value?.equity_pct) return 0
  return Math.min(100, Math.max(0, data.value.equity_pct))
})

onMounted(loadEquity)
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <button
      class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
             hover:text-gray-700 dark:hover:text-gray-300 mb-4"
      @click="router.push('/home')"
    >
      <ArrowLeft class="w-4 h-4" />
      {{ __('My Home') }}
    </button>

    <h1 class="text-h1 text-gray-900 dark:text-gray-100 mb-6">{{ __('Home Equity') }}</h1>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <div v-else-if="!data" class="text-center py-12">
      <PiggyBank class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <p class="text-gray-500 dark:text-gray-400">{{ __('Equity tracking is available for owner-occupied properties.') }}</p>
    </div>

    <template v-else>
      <!-- Equity bar -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-5 mb-6">
        <div class="flex items-baseline justify-between mb-4">
          <div>
            <div class="text-sm text-gray-500 dark:text-gray-400">{{ __('Your equity') }}</div>
            <div class="text-2xl font-bold text-green-600 dark:text-green-400">
              {{ formatCurrency(data.equity_amount) }}
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-500 dark:text-gray-400">{{ __('Property value') }}</div>
            <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {{ formatCurrency(data.estimated_value) }}
            </div>
          </div>
        </div>

        <!-- Visual bar -->
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-green-500 rounded-full transition-all duration-500"
            :style="{ width: equityPct + '%' }"
          />
        </div>
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>{{ __('Equity') }}: {{ data.equity_pct?.toFixed(1) }}%</span>
          <span>{{ __('Mortgage') }}: {{ formatCurrency(data.total_mortgage_balance) }}</span>
        </div>

        <!-- LTV -->
        <div v-if="data.ltv" class="mt-3 text-sm text-gray-600 dark:text-gray-400">
          {{ __('Loan-to-value') }}: {{ data.ltv.toFixed(1) }}%
        </div>
      </div>

      <!-- Mortgages -->
      <h2 v-if="data.mortgages?.length" class="text-h3 text-gray-800 dark:text-gray-200 mb-3">
        {{ __('Mortgages') }}
      </h2>
      <div class="space-y-2 mb-6">
        <div
          v-for="m in data.mortgages"
          :key="m.name"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 px-4 py-3"
        >
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ m.mortgage_name }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ m.lender }}
                <span v-if="m.interest_rate"> · {{ m.interest_rate }}%</span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ formatCurrency(m.outstanding_balance) }}
              </div>
              <div v-if="m.balance_date" class="text-xs text-gray-500 dark:text-gray-400">
                {{ __('as of') }} {{ formatDate(m.balance_date) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Update value -->
      <div class="mb-6">
        <Button v-if="!showUpdateForm" variant="outline" @click="showUpdateForm = true">
          <template #prefix><TrendingUp class="w-4 h-4" /></template>
          {{ __('Update property value') }}
        </Button>

        <div v-else class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-3">
          <div>
            <label class="text-xs text-gray-500 dark:text-gray-400 block mb-1">{{ __('Estimated value') }}</label>
            <input
              v-model="newValue"
              type="number"
              step="1000"
              min="0"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              :placeholder="__('e.g. 350000')"
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 dark:text-gray-400 block mb-1">{{ __('Note (optional)') }}</label>
            <input
              v-model="newNote"
              type="text"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              :placeholder="__('e.g. Based on recent sale nearby')"
            />
          </div>
          <div class="flex gap-2">
            <Button variant="solid" :loading="saving" @click="updateValue">{{ __('Save') }}</Button>
            <Button variant="ghost" @click="showUpdateForm = false">{{ __('Cancel') }}</Button>
          </div>
        </div>
      </div>

      <!-- Snapshots -->
      <h2 v-if="data.snapshots?.length" class="text-h3 text-gray-800 dark:text-gray-200 mb-3">
        {{ __('History') }}
      </h2>
      <div class="space-y-1">
        <div
          v-for="snap in data.snapshots"
          :key="snap.snapshot_date"
          class="flex items-center gap-3 text-sm py-1.5"
        >
          <span class="text-gray-500 dark:text-gray-400 w-24">{{ formatDate(snap.snapshot_date) }}</span>
          <span class="font-medium text-green-600 dark:text-green-400 w-28 text-right">
            {{ formatCurrency(snap.equity_amount) }}
          </span>
          <span class="text-gray-500 dark:text-gray-400">
            {{ snap.equity_pct?.toFixed(1) }}%
          </span>
          <span v-if="snap.note" class="text-gray-400 dark:text-gray-500 text-xs truncate">
            {{ snap.note }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>
