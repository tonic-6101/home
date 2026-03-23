<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Utility trends page — cost and consumption views (Features 26-27, 58).
-->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { ArrowLeft, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { __ } from '@/composables/useTranslate'
import { useHouseholdRole } from '@/composables/useHouseholdRole'
import { useProperty } from '@/composables/useProperty'

const router = useRouter()
const { isAdultOrAbove, load: loadRole } = useHouseholdRole()
const { propertyName, load: loadPropertyName } = useProperty()

interface MonthData {
  month: number
  consumption: number
}

interface TrendsData {
  year: number
  utility_type: string
  unit: string | null
  monthly: MonthData[]
  total_consumption: number
  total_cost: number
  prior_consumption: number
  prior_cost: number
  consumption_change_pct: number | null
  cost_change_pct: number | null
  per_sqm: number | null
  bills_without_consumption: number
}

interface CostMonthData {
  month: number
  amount: number
}

interface CostTrendsData {
  year: number
  utility_type: string
  monthly: CostMonthData[]
  total: number
  prior_total: number
  change_pct: number | null
  spike_months: number[]
}

const loading = ref(true)
const error = ref('')

const viewMode = ref<'cost' | 'consumption'>('cost')
const selectedYear = ref(new Date().getFullYear())
const selectedUtility = ref('Electricity')

const costData = ref<CostTrendsData | null>(null)
const consumptionData = ref<TrendsData | null>(null)

const utilityTypes = [
  'Electricity', 'Gas', 'Water', 'Internet', 'Heating Oil', 'District Heating',
]

const monthNames = [
  __('Jan'), __('Feb'), __('Mar'), __('Apr'), __('May'), __('Jun'),
  __('Jul'), __('Aug'), __('Sep'), __('Oct'), __('Nov'), __('Dec'),
]

const yearOptions = computed(() => {
  const current = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => current - i)
})

function formatCurrency(value: number | null): string {
  if (value == null) return '—'
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

function formatNumber(value: number | null, decimals = 0): string {
  if (value == null) return '—'
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: decimals }).format(value)
}

function changePctClass(pct: number | null): string {
  if (pct == null) return 'text-gray-500'
  if (pct < 0) return 'text-green-600 dark:text-green-400'
  if (pct > 0) return 'text-red-600 dark:text-red-400'
  return 'text-gray-500'
}

function barWidth(value: number, max: number): string {
  if (!max || !value) return '0%'
  return `${Math.min(100, (value / max) * 100)}%`
}

const costMax = computed(() => {
  if (!costData.value) return 0
  return Math.max(...costData.value.monthly.map(m => m.amount), 1)
})

const consumptionMax = computed(() => {
  if (!consumptionData.value) return 0
  return Math.max(...consumptionData.value.monthly.map(m => m.consumption), 1)
})

async function loadData() {
  if (!propertyName.value) return
  loading.value = true
  error.value = ''
  try {
    if (viewMode.value === 'cost') {
      const res = await frappeRequest({
        url: '/api/method/home.api.utility.get_cost_trends',
        params: {
          property_name: propertyName.value,
          year: selectedYear.value,
          utility_type: selectedUtility.value,
        },
      })
      costData.value = res
    } else {
      const res = await frappeRequest({
        url: '/api/method/home.api.utility.get_consumption_trends',
        params: {
          property_name: propertyName.value,
          year: selectedYear.value,
          utility_type: selectedUtility.value,
        },
      })
      consumptionData.value = res
    }
  } catch (e: any) {
    error.value = e.message || __('Failed to load trends')
  } finally {
    loading.value = false
  }
}

watch([viewMode, selectedYear, selectedUtility], () => {
  loadData()
})

onMounted(async () => {
  await loadRole()
  await loadPropertyName()
  if (propertyName.value) {
    await loadData()
  }
})
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <!-- Back -->
    <button
      @click="router.push('/home')"
      class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
             hover:text-gray-700 dark:hover:text-gray-200 mb-4"
    >
      <ArrowLeft class="w-4 h-4" />
      {{ __('My Home') }}
    </button>

    <h1 class="text-h1 text-gray-900 dark:text-gray-100 mb-4">
      {{ __('Utility Trends') }}
    </h1>

    <!-- Controls -->
    <div class="flex flex-wrap items-center gap-3 mb-6">
      <!-- View toggle -->
      <div class="flex rounded-lg border border-gray-300 dark:border-gray-600 overflow-hidden">
        <button
          @click="viewMode = 'cost'"
          :class="[
            'px-3 py-1.5 text-sm transition-colors',
            viewMode === 'cost'
              ? 'bg-home-500 text-white'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
          ]"
        >
          {{ __('Cost') }}
        </button>
        <button
          @click="viewMode = 'consumption'"
          :class="[
            'px-3 py-1.5 text-sm transition-colors',
            viewMode === 'consumption'
              ? 'bg-home-500 text-white'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
          ]"
        >
          {{ __('Consumption') }}
        </button>
      </div>

      <!-- Utility type -->
      <select
        v-model="selectedUtility"
        class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm
               bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
      >
        <option v-for="ut in utilityTypes" :key="ut" :value="ut">{{ __(ut) }}</option>
      </select>

      <!-- Year -->
      <select
        v-model="selectedYear"
        class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm
               bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
      >
        <option v-for="yr in yearOptions" :key="yr" :value="yr">{{ yr }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <!-- Cost view -->
    <template v-else-if="viewMode === 'cost' && costData">
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h2 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-4">
          {{ __(selectedUtility) }} — {{ __('Cost') }}
        </h2>

        <!-- Monthly bars -->
        <div class="space-y-2 mb-4">
          <div v-for="(m, idx) in costData.monthly" :key="idx" class="flex items-center gap-3">
            <span class="w-8 text-xs text-gray-500 dark:text-gray-400 text-right">{{ monthNames[m.month - 1] }}</span>
            <div class="flex-1 h-5 bg-gray-100 dark:bg-gray-700 rounded overflow-hidden">
              <div
                class="h-full rounded transition-all duration-300"
                :class="costData.spike_months?.includes(m.month) ? 'bg-red-400' : 'bg-home-400'"
                :style="{ width: barWidth(m.amount, costMax) }"
              />
            </div>
            <span class="w-20 text-xs text-gray-700 dark:text-gray-300 text-right">
              {{ formatCurrency(m.amount) }}
            </span>
          </div>
        </div>

        <!-- Summary -->
        <div class="flex flex-wrap gap-6 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div>
            <span class="text-caption text-gray-500 dark:text-gray-400 block">{{ __('Annual total') }}</span>
            <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {{ formatCurrency(costData.total) }}
            </span>
          </div>
          <div v-if="costData.change_pct != null">
            <span class="text-caption text-gray-500 dark:text-gray-400 block">{{ __('vs prior year') }}</span>
            <span :class="['text-sm font-semibold', changePctClass(costData.change_pct)]">
              {{ costData.change_pct > 0 ? '+' : '' }}{{ costData.change_pct }}%
            </span>
          </div>
        </div>

        <!-- Spike warning -->
        <div
          v-if="costData.spike_months?.length"
          class="mt-3 flex items-center gap-2 text-xs text-amber-600 dark:text-amber-400"
        >
          <AlertTriangle class="w-3.5 h-3.5" />
          {{ __('Highlighted months exceed 150% of the 12-month average.') }}
        </div>
      </div>
    </template>

    <!-- Consumption view -->
    <template v-else-if="viewMode === 'consumption' && consumptionData">
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h2 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-4">
          {{ __(selectedUtility) }} — {{ __('Consumption') }}
        </h2>

        <!-- Monthly bars -->
        <div class="space-y-2 mb-4">
          <div v-for="m in consumptionData.monthly" :key="m.month" class="flex items-center gap-3">
            <span class="w-8 text-xs text-gray-500 dark:text-gray-400 text-right">{{ monthNames[m.month - 1] }}</span>
            <div class="flex-1 h-5 bg-gray-100 dark:bg-gray-700 rounded overflow-hidden">
              <div
                class="h-full bg-blue-400 rounded transition-all duration-300"
                :style="{ width: barWidth(m.consumption, consumptionMax) }"
              />
            </div>
            <span class="w-24 text-xs text-gray-700 dark:text-gray-300 text-right">
              {{ formatNumber(m.consumption) }} {{ consumptionData.unit || '' }}
            </span>
          </div>
        </div>

        <!-- Summary -->
        <div class="flex flex-wrap gap-6 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div>
            <span class="text-caption text-gray-500 dark:text-gray-400 block">{{ __('Annual total') }}</span>
            <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {{ formatNumber(consumptionData.total_consumption) }} {{ consumptionData.unit || '' }}
            </span>
          </div>
          <div v-if="consumptionData.per_sqm != null">
            <span class="text-caption text-gray-500 dark:text-gray-400 block">{{ __('Per m²') }}</span>
            <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {{ formatNumber(consumptionData.per_sqm, 1) }} {{ consumptionData.unit || '' }}/m²
            </span>
          </div>
        </div>

        <!-- YoY comparison — consumption + cost split -->
        <div
          v-if="consumptionData.consumption_change_pct != null || consumptionData.cost_change_pct != null"
          class="mt-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
        >
          <h3 class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
            {{ __('Year-over-year comparison') }}
          </h3>
          <div class="flex flex-wrap gap-4 text-sm">
            <div v-if="consumptionData.consumption_change_pct != null" class="flex items-center gap-1">
              <component
                :is="consumptionData.consumption_change_pct < 0 ? TrendingDown : consumptionData.consumption_change_pct > 0 ? TrendingUp : Minus"
                class="w-4 h-4"
                :class="changePctClass(consumptionData.consumption_change_pct)"
              />
              <span :class="changePctClass(consumptionData.consumption_change_pct)">
                {{ consumptionData.consumption_change_pct > 0 ? '+' : '' }}{{ consumptionData.consumption_change_pct }}%
              </span>
              <span class="text-gray-500 dark:text-gray-400">{{ __('consumption') }}</span>
            </div>
            <div v-if="consumptionData.cost_change_pct != null" class="flex items-center gap-1">
              <component
                :is="consumptionData.cost_change_pct < 0 ? TrendingDown : consumptionData.cost_change_pct > 0 ? TrendingUp : Minus"
                class="w-4 h-4"
                :class="changePctClass(consumptionData.cost_change_pct)"
              />
              <span :class="changePctClass(consumptionData.cost_change_pct)">
                {{ consumptionData.cost_change_pct > 0 ? '+' : '' }}{{ consumptionData.cost_change_pct }}%
              </span>
              <span class="text-gray-500 dark:text-gray-400">{{ __('cost') }}</span>
            </div>
          </div>
          <p
            v-if="consumptionData.consumption_change_pct != null && consumptionData.cost_change_pct != null
                  && consumptionData.consumption_change_pct < 0 && consumptionData.cost_change_pct > 0"
            class="text-xs text-gray-500 dark:text-gray-400 mt-2"
          >
            {{ __('Your consumption dropped but costs rose — likely a price increase.') }}
          </p>
        </div>

        <!-- Bills without consumption data -->
        <div
          v-if="consumptionData.bills_without_consumption > 0"
          class="mt-3 text-xs text-gray-500 dark:text-gray-400"
        >
          {{ __('Note: {0} bill(s) in this period have no consumption data recorded.', [consumptionData.bills_without_consumption]) }}
          {{ __('Add meter readings to get a complete picture.') }}
        </div>
      </div>
    </template>

    <!-- No data -->
    <div
      v-else-if="!loading"
      class="text-center py-12 text-gray-500 dark:text-gray-400"
    >
      <p class="text-sm">{{ __('No utility bills found for this period.') }}</p>
    </div>
  </div>
</template>
