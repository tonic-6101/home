<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Warranty list page — single property view with expiry status (Feature 9).
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { ShieldCheck } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'

interface Warranty {
  name: string
  appliance: string
  warranty_type: string
  start_date: string | null
  end_date: string | null
  expiry_status: string
}

const { load: loadProperty } = useProperty()
const warranties = ref<Warranty[]>([])
const loading = ref(true)
const noProperty = ref(false)

const expiryColors: Record<string, string> = {
  active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  expiring_soon: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  expired: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
}

const expiryLabels: Record<string, string> = {
  active: 'Active',
  expiring_soon: 'Expiring Soon',
  expired: 'Expired',
}

async function loadWarranties() {
  loading.value = true
  try {
    const property = await loadProperty()
    if (!property) {
      noProperty.value = true
      return
    }
    const res = await frappeRequest({
      url: '/api/method/home.api.warranty.get_property_warranties',
      params: { property },
    })
    warranties.value = res.warranties || []
  } catch {
    warranties.value = []
  } finally {
    loading.value = false
  }
}

function formatDate(date: string | null): string {
  if (!date) return '—'
  return new Date(date).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(loadWarranties)
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-h1 text-gray-900 dark:text-gray-100">
        {{ __('Warranties') }}
      </h1>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- No property -->
    <div v-else-if="noProperty" class="text-center py-12">
      <ShieldCheck class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No property yet') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('Set up your property first to manage warranties.') }}
      </p>
    </div>

    <!-- Empty -->
    <div v-else-if="!warranties.length" class="text-center py-12">
      <ShieldCheck class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No warranties') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('No warranties found.') }}
      </p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700 text-left">
            <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Appliance') }}</th>
            <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Type') }}</th>
            <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Start') }}</th>
            <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('End') }}</th>
            <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Status') }}</th>
          </tr>
        </thead>
        <tbody>
          <router-link
            v-for="w in warranties"
            :key="w.name"
            :to="`/home/warranty/${w.name}`"
            custom
            v-slot="{ navigate }"
          >
            <tr
              @click="navigate"
              class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800
                     cursor-pointer transition-colors"
            >
              <td class="py-3 pr-4">
                <span class="font-medium text-gray-900 dark:text-gray-100">{{ w.appliance }}</span>
              </td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">{{ __(w.warranty_type) }}</td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">{{ formatDate(w.start_date) }}</td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">{{ formatDate(w.end_date) }}</td>
              <td class="py-3">
                <span
                  class="text-xs px-2 py-0.5 rounded-full"
                  :class="expiryColors[w.expiry_status] || 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'"
                >
                  {{ __(expiryLabels[w.expiry_status] || w.expiry_status) }}
                </span>
              </td>
            </tr>
          </router-link>
        </tbody>
      </table>
    </div>
  </div>
</template>
