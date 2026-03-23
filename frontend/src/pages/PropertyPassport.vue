<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Digital property passport — chronological timeline (Feature 37).
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  ArrowLeft, BookOpen, Download, Wrench, Shield,
  Package, Home as HomeIcon, Camera,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()

const passport = ref<any>(null)
const loading = ref(true)
const exporting = ref(false)
const periodFilter = ref('all')

interface PassportEvent {
  date: string
  type: string
  title: string
  description: string
  cost: number | null
}

const typeIcons: Record<string, any> = {
  maintenance: Wrench,
  warranty: Shield,
  item_added: Package,
  item_disposed: Package,
  property_update: HomeIcon,
  photo: Camera,
}

const typeColors: Record<string, string> = {
  maintenance: 'bg-blue-500',
  warranty: 'bg-green-500',
  item_added: 'bg-purple-500',
  item_disposed: 'bg-red-500',
  property_update: 'bg-amber-500',
  photo: 'bg-gray-500',
}

function formatDate(d: string): string {
  if (!d) return ''
  return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatCurrency(value: number | null): string {
  if (value == null) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

async function loadPassport() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.passport.get_passport',
      params: { property: propName },
    })
    passport.value = res
  } catch {
    passport.value = null
  } finally {
    loading.value = false
  }
}

async function exportPdf() {
  exporting.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.passport.export_passport_pdf',
      params: { property: propName },
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
      url: '/api/method/home.api.passport.export_passport_csv',
      params: { property: propName },
    })
    if (res?.file_url) {
      window.open(res.file_url, '_blank')
    }
  } catch (e: any) {
    alert(e.message || __('Export failed'))
  }
}

onMounted(loadPassport)
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
        <h1 class="text-h1 text-gray-900 dark:text-gray-100">{{ __('Property Passport') }}</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ __('Chronological record of everything done to your property.') }}
        </p>
      </div>
      <div class="flex gap-2">
        <Button variant="outline" :loading="exporting" @click="exportPdf">
          <template #prefix><Download class="w-4 h-4" /></template>
          {{ __('PDF') }}
        </Button>
        <Button variant="ghost" @click="exportCsv">{{ __('CSV') }}</Button>
      </div>
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <div v-else-if="!passport?.events?.length" class="text-center py-12">
      <BookOpen class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">{{ __('Empty passport') }}</h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('As you add items, complete maintenance, and register warranties, the passport fills up.') }}
      </p>
    </div>

    <!-- Timeline -->
    <div v-else class="relative">
      <!-- Vertical line -->
      <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

      <div class="space-y-4">
        <div
          v-for="(event, idx) in passport.events"
          :key="idx"
          class="relative flex gap-4 pl-10"
        >
          <!-- Dot -->
          <div
            class="absolute left-2.5 w-3 h-3 rounded-full ring-2 ring-white dark:ring-gray-900 flex-shrink-0 mt-1.5"
            :class="typeColors[event.type] || 'bg-gray-400'"
          />

          <div class="flex-1 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 px-4 py-3">
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-2">
                <component
                  :is="typeIcons[event.type] || Wrench"
                  class="w-4 h-4 text-gray-400 flex-shrink-0"
                />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ event.title }}
                </span>
              </div>
              <span class="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0 ml-2">
                {{ formatDate(event.date) }}
              </span>
            </div>
            <p v-if="event.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {{ event.description }}
            </p>
            <span v-if="event.cost" class="text-xs text-gray-500 dark:text-gray-400 mt-1 block">
              {{ formatCurrency(event.cost) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
