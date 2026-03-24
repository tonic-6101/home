<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Budget category drill-down — event list or monthly bars (Feature 20).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useRouter } from 'vue-router'
import {
  ArrowLeft, Wrench, Zap, Shield, ShoppingCart, Trees, HardHat,
  Check, AlertTriangle, X, Minus, ChevronRight,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useHouseholdRole } from '@/composables/useHouseholdRole'

const props = defineProps<{
  property: string
  year: number
  category: string
  line: {
    category: string
    annual_target: number
    actual_spend: number
    pace_expected: number | null
    status: string
  }
}>()

const emit = defineEmits<{ back: []; editTarget: [] }>()
const router = useRouter()
const { isAdultOrAbove } = useHouseholdRole()
const isCurrentYear = computed(() => props.year === new Date().getFullYear())

function rowLink(row: any): string | null {
  // Maintenance records
  if (row.completed_date && row.title) {
    return `/app/home-maintenance/${row.name}`
  }
  // Insurance policies
  if (row.policy_name) {
    return `/app/home-insurance-policy/${row.name}`
  }
  // Utility bills
  if (row.bill_type || row.utility_type) {
    return `/app/home-utility-bill/${row.name}`
  }
  return null
}

const detail = ref<{ type: string; rows: any[] } | null>(null)
const loading = ref(true)

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

function formatCurrency(value: number | null): string {
  if (value == null) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDate(date: string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })
}

function progressPct(): number {
  if (!props.line.annual_target) return 0
  return Math.min(100, Math.round((props.line.actual_spend / props.line.annual_target) * 100))
}

function pacePct(): number | null {
  if (!props.line.annual_target || props.line.pace_expected == null) return null
  return Math.min(100, Math.round((props.line.pace_expected / props.line.annual_target) * 100))
}

function statusLabel(): string {
  const s = props.line.status
  if (s === 'on_track') return __('On track')
  if (s === 'ahead_of_pace') return __('Ahead of pace')
  if (s === 'over_budget') return __('Over budget')
  return __('No target set')
}

// Group utility rows by month for flowing category display
function monthlyGroups(rows: any[]): { label: string; total: number; items: any[] }[] {
  const months: Record<string, { total: number; items: any[] }> = {}
  for (const row of rows) {
    const date = row.period_end || row.completed_date || ''
    if (!date) continue
    const d = new Date(date)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const label = d.toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
    if (!months[key]) months[key] = { total: 0, items: [] }
    months[key].total += row.amount || row.cost || 0
    months[key].items.push({ ...row, _monthLabel: label })
  }
  return Object.entries(months)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, v]) => ({
      label: v.items[0]?._monthLabel || '',
      total: v.total,
      items: v.items,
    }))
}

const maxMonthly = ref(0)

async function loadDetail() {
  loading.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.budget.get_category_detail',
      params: { property: props.property, year: props.year, category: props.category },
    })
    detail.value = res
    if (res?.type === 'flowing') {
      const groups = monthlyGroups(res.rows)
      maxMonthly.value = Math.max(...groups.map(g => g.total), 1)
    }
  } catch (e: any) {
    detail.value = { type: 'event', rows: [] }
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <button
          @click="emit('back')"
          class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
        >
          <ArrowLeft class="w-4 h-4" />
        </button>
        <component
          :is="categoryIcons[category] || Wrench"
          class="w-5 h-5 text-gray-500 dark:text-gray-400"
        />
        <h2 class="text-h3 text-gray-900 dark:text-gray-100">
          {{ __(category) }} — {{ year }}
        </h2>
      </div>
    </div>

    <!-- Summary -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4">
      <div class="grid grid-cols-3 gap-4 text-sm mb-3">
        <div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ __('Annual target') }}</div>
          <div class="font-medium text-gray-900 dark:text-gray-100">
            {{ line.annual_target ? formatCurrency(line.annual_target) : __('Not set') }}
            <button
              v-if="isAdultOrAbove && isCurrentYear"
              @click="emit('editTarget')"
              class="text-xs text-accent-600 dark:text-accent-400 hover:underline ml-1"
            >
              {{ __('Edit') }}
            </button>
          </div>
        </div>
        <div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ __('Spent to date') }}</div>
          <div class="font-medium text-gray-900 dark:text-gray-100">
            {{ formatCurrency(line.actual_spend) }}
            <span v-if="line.annual_target" class="text-gray-500 font-normal">
              ({{ progressPct() }}%)
            </span>
          </div>
        </div>
        <div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ __('Expected pace') }}</div>
          <div class="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-1.5">
            {{ line.pace_expected != null ? formatCurrency(line.pace_expected) : '—' }}
            <component
              :is="statusConfig[line.status]?.icon || Minus"
              class="w-3.5 h-3.5"
              :class="statusConfig[line.status]?.color"
            />
            <span class="text-xs" :class="statusConfig[line.status]?.color">
              {{ statusLabel() }}
            </span>
          </div>
        </div>
      </div>

      <!-- Progress bar -->
      <div v-if="line.annual_target" class="relative h-3 bg-gray-100 dark:bg-gray-700 rounded-full overflow-visible">
        <div
          :class="['h-full rounded-full', statusConfig[line.status]?.barColor || 'bg-gray-400']"
          :style="{ width: `${Math.min(100, progressPct())}%` }"
        />
        <div
          v-if="pacePct() != null"
          class="absolute top-0 h-full w-0.5 bg-gray-900/30 dark:bg-white/30"
          :style="{ left: `${pacePct()}%` }"
        />
      </div>
    </div>

    <!-- Detail rows -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400 py-4">
      {{ __('Loading…') }}
    </div>

    <template v-else-if="detail">
      <!-- Flowing category: monthly bars + individual rows -->
      <template v-if="detail.type === 'flowing' && detail.rows.length">
        <h3 class="text-h4 text-gray-800 dark:text-gray-200 mb-2">{{ __('Monthly spend') }}</h3>
        <div class="space-y-1 mb-4">
          <div
            v-for="group in monthlyGroups(detail.rows)"
            :key="group.label"
            class="flex items-center gap-3"
          >
            <span class="text-xs text-gray-500 dark:text-gray-400 w-16 text-right">{{ group.label }}</span>
            <div class="flex-1 h-5 bg-gray-100 dark:bg-gray-700 rounded">
              <div
                class="h-full bg-blue-500 rounded"
                :style="{ width: `${(group.total / maxMonthly) * 100}%` }"
              />
            </div>
            <span class="text-xs text-gray-700 dark:text-gray-300 w-20 text-right">
              {{ formatCurrency(group.total) }}
            </span>
          </div>
        </div>

        <h3 class="text-h4 text-gray-800 dark:text-gray-200 mb-2">{{ __('Individual bills') }}</h3>
        <div class="space-y-1">
          <a
            v-for="row in detail.rows"
            :key="row.name"
            :href="`/app/home-utility-bill/${row.name}`"
            class="flex items-center justify-between py-1.5 text-sm no-underline
                   hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded px-1 -mx-1 transition-colors"
          >
            <div class="text-gray-700 dark:text-gray-300">
              <span class="text-xs text-gray-400 dark:text-gray-500 mr-2">
                {{ formatDate(row.period_end) }}
              </span>
              {{ row.bill_type || row.utility_type || '' }}
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-gray-700 dark:text-gray-300 font-medium">
                {{ formatCurrency(row.amount) }}
              </span>
              <ChevronRight class="w-3.5 h-3.5 text-gray-400" />
            </div>
          </a>
        </div>
      </template>

      <!-- Event category: chronological list -->
      <template v-else-if="detail.type === 'event' && detail.rows.length">
        <h3 class="text-h4 text-gray-800 dark:text-gray-200 mb-2">{{ __('Spend events') }}</h3>
        <div class="space-y-2">
          <component
            :is="rowLink(row) ? 'a' : 'div'"
            v-for="row in detail.rows"
            :key="row.name"
            :href="rowLink(row) || undefined"
            :class="[
              'flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700',
              rowLink(row) ? 'hover:shadow-sm transition-shadow no-underline cursor-pointer' : '',
            ]"
          >
            <div>
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ row.title || row.policy_name || '' }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                <template v-if="row.completed_date">{{ formatDate(row.completed_date) }}</template>
                <template v-if="row.contractor"> · {{ row.contractor }}</template>
                <template v-if="row.provider"> · {{ row.provider }}</template>
                <template v-if="row.policy_type"> · {{ row.policy_type }}</template>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ formatCurrency(row.cost || row.premium_annual || 0) }}
              </span>
              <ChevronRight v-if="rowLink(row)" class="w-4 h-4 text-gray-400" />
            </div>
          </component>
        </div>
      </template>

      <!-- Empty -->
      <div v-else class="text-sm text-gray-400 dark:text-gray-500 py-4">
        {{ __('No records for this category in') }} {{ year }}.
      </div>
    </template>
  </div>
</template>
