<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Budget overview page — annual targets vs actuals per property (Feature 20).
-->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  ArrowLeft, Wrench, Zap, Shield, ShoppingCart, Trees, HardHat,
  Check, AlertTriangle, X, Minus, ChevronDown,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useHouseholdRole } from '@/composables/useHouseholdRole'
import { useProperty } from '@/composables/useProperty'
import BudgetSetup from '@/components/BudgetSetup.vue'
import BudgetCategoryDetail from '@/components/BudgetCategoryDetail.vue'
import SetTargetDialog from '@/components/SetTargetDialog.vue'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()
const { isAdultOrAbove, isChild, load: loadRole } = useHouseholdRole()

interface BudgetLine {
  category: string
  annual_target: number
  actual_spend: number
  pace_expected: number | null
  status: string
  notes: string | null
}

interface SoftLine {
  source: string
  label: string
  annual_total: number
}

interface BudgetOverview {
  budget_name: string
  year: number
  lines: BudgetLine[]
  soft_lines: SoftLine[]
  totals: { annual_target: number; actual_spend: number; pace_expected: number }
  pace: { months_elapsed: number; months_total: number; pct_year_elapsed: number }
}

const overview = ref<BudgetOverview | null>(null)
const loading = ref(true)
const error = ref('')
const year = ref(new Date().getFullYear())
const yearOptions = computed(() => {
  const cur = new Date().getFullYear()
  return [cur - 1, cur, cur + 1]
})
const propertyLabel = ref('')

// Sub-views
const showSetup = ref(false)
const detailCategory = ref<string | null>(null)
const targetCategory = ref<string | null>(null)
const targetSuggestion = ref<{ amount: number; basis: string } | null>(null)

const categoryIcons: Record<string, any> = {
  'Maintenance & Repairs': Wrench,
  'Utilities': Zap,
  'Insurance': Shield,
  'Supplies & Consumables': ShoppingCart,
  'Garden & Exterior': Trees,
  'Improvement Projects': HardHat,
}

const statusConfig: Record<string, { icon: any; color: string; barColor: string }> = {
  on_track: { icon: Check, color: 'text-green-600 dark:text-green-400', barColor: 'bg-green-500' },
  ahead_of_pace: { icon: AlertTriangle, color: 'text-amber-600 dark:text-amber-400', barColor: 'bg-amber-500' },
  over_budget: { icon: X, color: 'text-red-600 dark:text-red-400', barColor: 'bg-red-500' },
  no_target: { icon: Minus, color: 'text-gray-400 dark:text-gray-500', barColor: 'bg-gray-400' },
}

function statusLabel(line: BudgetLine): string {
  if (line.status === 'on_track') return __('On track')
  if (line.status === 'ahead_of_pace') return __('Ahead of pace')
  if (line.status === 'over_budget') {
    const over = line.actual_spend - line.annual_target
    return __('Over budget by') + ' ' + formatCurrency(over)
  }
  return __('No target set')
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

function progressPct(line: BudgetLine): number {
  if (!line.annual_target) return 0
  return Math.min(100, Math.round((line.actual_spend / line.annual_target) * 100))
}

function pacePct(line: BudgetLine): number | null {
  if (!line.annual_target || line.pace_expected == null) return null
  return Math.min(100, Math.round((line.pace_expected / line.annual_target) * 100))
}

const isCurrentYear = computed(() => year.value === new Date().getFullYear())

async function loadOverview() {
  loading.value = true
  error.value = ''
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.budget.get_overview',
      params: { property: propName, year: year.value },
    })
    overview.value = res

    // Check if this is first-time (all targets are 0/null)
    const hasAnyTarget = res?.lines?.some((l: BudgetLine) => l.annual_target > 0)
    if (!hasAnyTarget && isCurrentYear.value) {
      showSetup.value = true
    }
  } catch (e: any) {
    error.value = e.message || __('Failed to load budget')
  } finally {
    loading.value = false
  }
}

async function loadPropertyLabel() {
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.property.get_property',
      params: { name: propName },
    })
    propertyLabel.value = res?.property_name || propName
  } catch {
    propertyLabel.value = propertyName.value
  }
}

function openSetTarget(line: BudgetLine) {
  targetCategory.value = line.category
  targetSuggestion.value = null
  // Try to get suggestion
  frappeRequest({
    url: '/api/method/home.api.budget.suggest_targets',
    params: { property: propertyName.value, year: year.value },  // propertyName is already loaded at this point
  }).then((res: any) => {
    const s = res?.suggestions?.[line.category]
    if (s) targetSuggestion.value = s
  }).catch(() => {})
}

async function onTargetSaved() {
  targetCategory.value = null
  await loadOverview()
}

function onSetupDone() {
  showSetup.value = false
  loadOverview()
}

watch(year, () => {
  showSetup.value = false
  detailCategory.value = null
  loadOverview()
})

onMounted(() => {
  loadRole()
  loadPropertyLabel()
  loadOverview()
})
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <!-- Child role: hidden entirely -->
    <div v-if="isChild" class="text-gray-500 dark:text-gray-400 text-center py-12">
      {{ __('Budget information is not available for your role.') }}
    </div>

    <template v-else>
      <!-- Back -->
      <button
        @click="router.push('/home')"
        class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
               hover:text-gray-700 dark:hover:text-gray-200 mb-4"
      >
        <ArrowLeft class="w-4 h-4" />
        {{ propertyLabel || __('My Home') }}
      </button>

      <!-- Loading -->
      <div v-if="loading" class="text-gray-500 dark:text-gray-400">
        {{ __('Loading…') }}
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-red-600 dark:text-red-400">
        {{ error }}
      </div>

      <template v-else-if="overview">
        <!-- First-time setup wizard -->
        <BudgetSetup
          v-if="showSetup"
          :property="propertyName"
          :year="year"
          :property-label="propertyLabel"
          @done="onSetupDone"
        />

        <!-- Category detail drill-down -->
        <BudgetCategoryDetail
          v-else-if="detailCategory"
          :property="propertyName"
          :year="year"
          :category="detailCategory"
          :line="overview.lines.find(l => l.category === detailCategory)!"
          @back="detailCategory = null"
          @edit-target="openSetTarget(overview.lines.find(l => l.category === detailCategory)!)"
        />

        <!-- Main overview -->
        <template v-else>
          <!-- Summary header -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-5 mb-6">
            <div class="flex items-center justify-between mb-4">
              <h1 class="text-h1 text-gray-900 dark:text-gray-100">
                {{ __('Budget Overview') }}
              </h1>
              <!-- Year selector -->
              <div class="relative">
                <select
                  v-model="year"
                  class="appearance-none bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600
                         rounded-lg pl-3 pr-8 py-1.5 text-sm text-gray-900 dark:text-gray-100 cursor-pointer"
                >
                  <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
                </select>
                <ChevronDown class="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400" />
              </div>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ __('Total budgeted') }}</div>
                <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {{ formatCurrency(overview.totals.annual_target) }}
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ __('Spent to date') }}</div>
                <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {{ formatCurrency(overview.totals.actual_spend) }}
                  <span v-if="overview.totals.annual_target" class="text-sm font-normal text-gray-500">
                    ({{ Math.round((overview.totals.actual_spend / overview.totals.annual_target) * 100) }}%)
                  </span>
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ __('Expected pace') }}</div>
                <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {{ formatCurrency(overview.totals.pace_expected) }}
                </div>
              </div>
            </div>

            <div class="text-xs text-gray-400 dark:text-gray-500 mt-3">
              {{ overview.pace.months_elapsed }} / 12 {{ __('months elapsed') }}
            </div>
          </div>

          <!-- Category cards -->
          <div class="space-y-3">
            <div
              v-for="line in overview.lines"
              :key="line.category"
              class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
            >
              <!-- Category header -->
              <div class="flex items-center gap-2 mb-3">
                <component
                  :is="categoryIcons[line.category] || Wrench"
                  class="w-4 h-4 text-gray-500 dark:text-gray-400"
                />
                <span class="font-medium text-gray-900 dark:text-gray-100 text-sm">
                  {{ __(line.category) }}
                </span>
              </div>

              <!-- Progress bar -->
              <div class="relative h-3 bg-gray-100 dark:bg-gray-700 rounded-full overflow-visible mb-2">
                <div
                  :class="[
                    'h-full rounded-full transition-all duration-500',
                    statusConfig[line.status]?.barColor || 'bg-gray-400',
                  ]"
                  :style="{ width: `${Math.min(100, progressPct(line))}%` }"
                />
                <!-- Pace marker -->
                <div
                  v-if="pacePct(line) != null"
                  class="absolute top-0 h-full w-0.5 bg-gray-900/30 dark:bg-white/30"
                  :style="{ left: `${pacePct(line)}%` }"
                  :title="__('Expected pace')"
                />
              </div>

              <!-- Amounts -->
              <div class="flex items-center justify-between text-sm mb-2">
                <span class="text-gray-700 dark:text-gray-300">
                  {{ formatCurrency(line.actual_spend) }}
                  <template v-if="line.annual_target">
                    / {{ formatCurrency(line.annual_target) }}
                  </template>
                </span>
                <span v-if="line.annual_target" class="text-gray-500 dark:text-gray-400">
                  {{ progressPct(line) }}%
                </span>
              </div>

              <!-- Status + actions -->
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <component
                    :is="statusConfig[line.status]?.icon || Minus"
                    class="w-3.5 h-3.5"
                    :class="statusConfig[line.status]?.color || 'text-gray-400'"
                  />
                  <span
                    class="text-xs"
                    :class="statusConfig[line.status]?.color || 'text-gray-400'"
                  >
                    {{ statusLabel(line) }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    v-if="isAdultOrAbove && isCurrentYear"
                    @click="openSetTarget(line)"
                    class="text-xs text-home-600 dark:text-home-400 hover:underline"
                  >
                    {{ line.annual_target ? __('Edit target') : __('Set target') }}
                  </button>
                  <button
                    @click="detailCategory = line.category"
                    class="text-xs text-home-600 dark:text-home-400 hover:underline"
                  >
                    {{ __('Details') }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Soft integration lines -->
          <div v-if="overview.soft_lines.length" class="mt-4 space-y-3">
            <div
              v-for="sl in overview.soft_lines"
              :key="sl.source"
              class="bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
            >
              <div class="flex items-center gap-2 mb-1">
                <ShoppingCart v-if="sl.label === 'Groceries'" class="w-4 h-4 text-gray-400" />
                <component v-else :is="HardHat" class="w-4 h-4 text-gray-400" />
                <span class="font-medium text-gray-700 dark:text-gray-300 text-sm">
                  {{ __(sl.label) }}
                </span>
                <span class="text-xs text-gray-400 dark:text-gray-500">
                  ({{ __('via') }} {{ sl.source }})
                </span>
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                {{ formatCurrency(sl.annual_total) }} {{ __('this year') }}
              </div>
              <div class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                {{ __('Read-only — managed in') }} {{ sl.source }}
              </div>
            </div>
          </div>
        </template>
      </template>

      <!-- Set target dialog -->
      <SetTargetDialog
        v-if="targetCategory"
        :property="propertyName"
        :year="year"
        :category="targetCategory"
        :current-target="overview?.lines.find(l => l.category === targetCategory)?.annual_target || 0"
        :suggestion="targetSuggestion"
        @close="targetCategory = null"
        @saved="onTargetSaved"
      />
    </template>
  </div>
</template>
