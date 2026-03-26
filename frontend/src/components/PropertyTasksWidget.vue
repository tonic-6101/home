<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Property Tasks Widget — shows Orga Task count for a property.

  Compact mode: inline stats for the stats bar.
  Full mode: card with link to Orga.
-->
<script lang="ts">
export default { name: 'PropertyTasksWidget' }
</script>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { CheckSquare, ExternalLink } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  compact?: boolean
}>()

const openCount = ref(0)
const overdueCount = ref(0)
const loading = ref(true)

async function loadTaskCounts() {
  loading.value = true
  try {
    const result = await frappeRequest({
      url: '/api/method/frappe.client.get_count',
      params: {
        doctype: 'Orga Task',
        filters: JSON.stringify({
          home_property: props.property,
          status: ['not in', ['Completed', 'Cancelled']],
        }),
      },
    })
    openCount.value = result?.message ?? 0

    const overdueResult = await frappeRequest({
      url: '/api/method/frappe.client.get_count',
      params: {
        doctype: 'Orga Task',
        filters: JSON.stringify({
          home_property: props.property,
          status: ['not in', ['Completed', 'Cancelled']],
          due_date: ['<', new Date().toISOString().split('T')[0]],
        }),
      },
    })
    overdueCount.value = overdueResult?.message ?? 0
  } catch {
    // Orga might not be installed or custom fields not yet migrated
  } finally {
    loading.value = false
  }
}

onMounted(loadTaskCounts)

function openOrgaTasks() {
  window.location.href = `/orga/my-tasks?home_property=${encodeURIComponent(props.property)}`
}
</script>

<template>
  <!-- Compact mode: inline stats for the stats bar -->
  <div v-if="compact" class="flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-400">
    <CheckSquare class="w-4 h-4" />
    <a
      href="#"
      class="hover:text-accent-600 dark:hover:text-accent-400 transition-colors no-underline"
      @click.prevent="openOrgaTasks"
    >
      <span>{{ openCount }} {{ __('open tasks') }}</span>
      <span v-if="overdueCount > 0" class="text-red-500 ml-1">({{ overdueCount }} {{ __('overdue') }})</span>
    </a>
  </div>

  <!-- Full mode: card widget -->
  <div
    v-else
    class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4"
  >
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-medium text-gray-800 dark:text-gray-200 flex items-center gap-2">
        <CheckSquare class="w-4 h-4" />
        {{ __('Tasks') }}
      </h3>
      <a
        href="#"
        class="text-xs text-accent-600 dark:text-accent-400 hover:text-accent-700 dark:hover:text-accent-300
               flex items-center gap-1 no-underline transition-colors"
        @click.prevent="openOrgaTasks"
      >
        {{ __('View') }}
        <ExternalLink class="w-3 h-3" />
      </a>
    </div>

    <div v-if="loading" class="text-xs text-gray-400">{{ __('Loading...') }}</div>

    <div v-else class="text-sm text-gray-600 dark:text-gray-400">
      <span>{{ openCount }} {{ __('open') }}</span>
      <span v-if="overdueCount > 0" class="text-red-500 ml-2">{{ overdueCount }} {{ __('overdue') }}</span>
    </div>
  </div>
</template>
