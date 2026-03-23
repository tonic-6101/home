<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Annual cost report page (Feature 23).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { ArrowLeft, FileText, Download, ChevronDown } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()

const report = ref<any>(null)
const loading = ref(true)
const year = ref(new Date().getFullYear())
const expandedCategory = ref<string | null>(null)
const exporting = ref(false)

function formatCurrency(value: number | null): string {
  if (value == null) return '€0'
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

async function loadReport() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.cost_report.get_cost_report',
      params: { property: propName, year: year.value },
    })
    report.value = res
  } catch {
    report.value = null
  } finally {
    loading.value = false
  }
}

async function exportPdf() {
  exporting.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.cost_report.export_pdf',
      params: { property: propName, year: year.value },
    })
    if (res?.file_url) {
      window.open(res.file_url, '_blank')
    }
  } catch (e: any) {
    alert(e.message || __('Export failed'))
  } finally {
    exporting.value = false
  }
}

async function exportCsv() {
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.cost_report.export_csv',
      params: { property: propName, year: year.value },
    })
    if (res?.file_url) {
      window.open(res.file_url, '_blank')
    }
  } catch (e: any) {
    alert(e.message || __('Export failed'))
  }
}

const isPartialYear = computed(() => year.value === new Date().getFullYear())

const categoryColors: Record<string, string> = {
  'Maintenance & Repairs': 'bg-blue-500',
  Utilities: 'bg-amber-500',
  Insurance: 'bg-green-500',
  Items: 'bg-purple-500',
  Returns: 'bg-red-500',
}

onMounted(loadReport)
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

    <div class="flex items-start justify-between mb-6">
      <div>
        <h1 class="text-h1 text-gray-900 dark:text-gray-100">{{ __('Annual Cost Report') }}</h1>
        <p v-if="isPartialYear" class="text-xs text-amber-600 dark:text-amber-400 mt-1">
          {{ __('Partial year — data through today') }}
        </p>
      </div>
      <div class="flex items-center gap-2">
        <select
          v-model="year"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1.5 text-sm
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          @change="loadReport"
        >
          <option v-for="y in [2026, 2025, 2024]" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <div v-else-if="!report" class="text-center py-12">
      <FileText class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <p class="text-gray-500 dark:text-gray-400">{{ __('No cost data for this year.') }}</p>
    </div>

    <template v-else>
      <!-- Grand total -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div class="text-sm text-gray-500 dark:text-gray-400">{{ __('Total spending') }}</div>
        <div class="text-2xl font-bold text-gray-900 dark:text-gray-100">
          {{ formatCurrency(report.grand_total) }}
        </div>
      </div>

      <!-- By category -->
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-3">{{ __('By category') }}</h2>
      <div class="space-y-2 mb-6">
        <div
          v-for="cat in report.by_category"
          :key="cat.category"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          <button
            class="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-750"
            @click="expandedCategory = expandedCategory === cat.category ? null : cat.category"
          >
            <div
              class="w-3 h-3 rounded-full flex-shrink-0"
              :class="categoryColors[cat.category] || 'bg-gray-400'"
            />
            <span class="flex-1 text-sm font-medium text-gray-900 dark:text-gray-100 text-left">
              {{ __(cat.category) }}
            </span>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {{ cat.pct }}%
            </span>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300 w-24 text-right">
              {{ formatCurrency(cat.total) }}
            </span>
            <ChevronDown
              class="w-4 h-4 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedCategory === cat.category }"
            />
          </button>

          <div
            v-if="expandedCategory === cat.category && cat.rows?.length"
            class="border-t border-gray-200 dark:border-gray-700 max-h-64 overflow-y-auto"
          >
            <div
              v-for="row in cat.rows"
              :key="row.name"
              class="flex items-center gap-2 px-4 py-2 text-sm border-b last:border-b-0
                     border-gray-100 dark:border-gray-700"
            >
              <span class="flex-1 text-gray-600 dark:text-gray-400 truncate">{{ row.label }}</span>
              <span class="text-gray-500 dark:text-gray-400">{{ row.date }}</span>
              <span class="font-medium text-gray-900 dark:text-gray-100 w-20 text-right">
                {{ formatCurrency(row.amount) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Export -->
      <div class="flex gap-2">
        <Button variant="outline" :loading="exporting" @click="exportPdf">
          <template #prefix><Download class="w-4 h-4" /></template>
          {{ __('Export PDF') }}
        </Button>
        <Button variant="outline" @click="exportCsv">
          {{ __('Export CSV') }}
        </Button>
      </div>
    </template>
  </div>
</template>
