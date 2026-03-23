<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Utility bills page — grouped by type with cost trends (Features 26-27, 58).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { ArrowLeft, Zap, Flame, Droplets, Wifi, Fuel, Thermometer, Plus, Check, TrendingUp } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'
import { useHouseholdRole } from '@/composables/useHouseholdRole'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()
const { isAdultOrAbove, load: loadRole } = useHouseholdRole()

interface BillGroup {
  bill_type: string
  bills: any[]
  avg_12m: number | null
  total_ytd: number
}

const groups = ref<BillGroup[]>([])
const loading = ref(true)
const expandedType = ref<string | null>(null)

const typeIcons: Record<string, any> = {
  Electricity: Zap,
  Gas: Flame,
  Water: Droplets,
  Internet: Wifi,
  'Heating Oil': Fuel,
  'District Heating': Thermometer,
}

function formatCurrency(value: number | null): string {
  if (value == null) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDate(d: string): string {
  if (!d) return ''
  return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadBills() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.utility.get_bills',
      params: { property: propName },
    })
    groups.value = res?.groups || []
  } catch {
    groups.value = []
  } finally {
    loading.value = false
  }
}

async function markPaid(billName: string) {
  try {
    await frappeRequest({
      url: '/api/method/home.api.utility.mark_paid',
      params: { bill_name: billName },
    })
    await loadBills()
  } catch (e: any) {
    alert(e.message || __('Failed to mark as paid'))
  }
}

const totalYtd = computed(() =>
  groups.value.reduce((sum, g) => sum + (g.total_ytd || 0), 0)
)

onMounted(() => {
  loadRole()
  loadBills()
})
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

    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-h1 text-gray-900 dark:text-gray-100">{{ __('Utility Bills') }}</h1>
        <p v-if="!loading && groups.length" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ __('Year to date') }}: {{ formatCurrency(totalYtd) }}
        </p>
      </div>
      <router-link
        to="/home/utilities/trends"
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg
               bg-home-50 dark:bg-home-900/20 text-home-600 dark:text-home-400
               hover:bg-home-100 dark:hover:bg-home-900/30 transition-colors no-underline"
      >
        <TrendingUp class="w-4 h-4" />
        {{ __('Trends') }}
      </router-link>
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <div v-else-if="!groups.length" class="text-center py-12">
      <Zap class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">{{ __('No utility bills yet') }}</h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('Track electricity, gas, water, and other utility bills here.') }}
      </p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="group in groups"
        :key="group.bill_type"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
      >
        <button
          class="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
          @click="expandedType = expandedType === group.bill_type ? null : group.bill_type"
        >
          <component
            :is="typeIcons[group.bill_type] || Zap"
            class="w-5 h-5 text-gray-400 flex-shrink-0"
          />
          <div class="flex-1 text-left">
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ __(group.bill_type) }}
            </span>
            <span v-if="group.avg_12m" class="text-xs text-gray-500 dark:text-gray-400 ml-2">
              {{ __('avg') }} {{ formatCurrency(group.avg_12m) }}/{{ __('bill') }}
            </span>
          </div>
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {{ formatCurrency(group.total_ytd) }}
          </span>
        </button>

        <div v-if="expandedType === group.bill_type" class="border-t border-gray-200 dark:border-gray-700">
          <div
            v-for="bill in group.bills"
            :key="bill.name"
            class="flex items-center gap-3 px-4 py-2.5 text-sm border-b last:border-b-0
                   border-gray-100 dark:border-gray-700"
          >
            <div class="flex-1 min-w-0">
              <span class="text-gray-700 dark:text-gray-300">
                {{ formatDate(bill.period_start) }} – {{ formatDate(bill.period_end) }}
              </span>
              <span v-if="bill.provider" class="text-xs text-gray-500 dark:text-gray-400 ml-2">
                {{ bill.provider }}
              </span>
            </div>
            <span class="font-medium text-gray-900 dark:text-gray-100">
              {{ formatCurrency(bill.amount) }}
            </span>
            <span
              v-if="bill.paid"
              class="text-xs text-green-600 dark:text-green-400 flex items-center gap-0.5"
            >
              <Check class="w-3 h-3" /> {{ __('Paid') }}
            </span>
            <button
              v-else-if="isAdultOrAbove"
              class="text-xs text-amber-600 dark:text-amber-400 hover:underline"
              @click.stop="markPaid(bill.name)"
            >
              {{ __('Mark paid') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
