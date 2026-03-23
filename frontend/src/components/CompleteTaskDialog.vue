<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Maintenance task completion dialog — collects date, cost, notes (Feature 11).
-->
<script setup lang="ts">
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  taskName: string
}>()

const emit = defineEmits<{ close: []; completed: [] }>()

const completedDate = ref(new Date().toISOString().slice(0, 10))
const cost = ref<number | null>(null)
const notes = ref('')
const saving = ref(false)

async function submit() {
  saving.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.maintenance.complete_task',
      params: {
        name: props.taskName,
        completed_date: completedDate.value,
        cost: cost.value ?? undefined,
        notes: notes.value.trim() || undefined,
      },
    })
    emit('completed')
  } catch (e: any) {
    alert(e.message || __('Failed to complete task'))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-sm mx-4 p-6"
      @keydown.escape="emit('close')"
    >
      <h2 class="text-h3 text-gray-900 dark:text-gray-100 mb-4">
        {{ __('Mark as Complete') }}
      </h2>

      <div class="space-y-3">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Completed date') }}
          </label>
          <input
            v-model="completedDate"
            type="date"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Cost') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">€</span>
            <input
              v-model.number="cost"
              type="number"
              min="0"
              step="0.01"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-7 pr-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Notes') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <textarea
            v-model="notes"
            rows="2"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      <div class="flex justify-end gap-2 mt-5">
        <Button variant="outline" @click="emit('close')">{{ __('Cancel') }}</Button>
        <Button variant="solid" :loading="saving" @click="submit">{{ __('Complete') }}</Button>
      </div>
    </div>
  </div>
</template>
