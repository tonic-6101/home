<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Quick "Mark refund received" dialog for purchase returns (Feature 18).
-->
<script setup lang="ts">
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  returnName: string
}>()

const emit = defineEmits<{ close: []; saved: [] }>()

const amount = ref<number>(0)
const receivedDate = ref(new Date().toISOString().split('T')[0])
const saving = ref(false)
const error = ref('')

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await frappeRequest({
      url: '/api/method/home.api.returns.mark_refund_received',
      params: {
        name: props.returnName,
        refund_amount_received: amount.value,
        refund_received_date: receivedDate.value,
      },
    })
    emit('saved')
  } catch (e: any) {
    error.value = e.message || __('Failed to update')
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
        {{ __('Mark Refund Received') }}
      </h2>

      <div class="space-y-3">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Amount Received') }}
          </label>
          <input
            v-model.number="amount"
            type="number"
            min="0"
            step="0.01"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @keyup.enter="submit"
          />
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Date Received') }}
          </label>
          <input
            v-model="receivedDate"
            type="date"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      <p v-if="error" class="mt-3 text-sm text-red-600 dark:text-red-400">{{ error }}</p>

      <div class="flex justify-end gap-2 mt-5">
        <Button variant="outline" @click="emit('close')">{{ __('Cancel') }}</Button>
        <Button variant="solid" :loading="saving" @click="submit">
          {{ __('Confirm') }}
        </Button>
      </div>
    </div>
  </div>
</template>
