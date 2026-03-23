<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Create Purchase Return dialog (Feature 18).
-->
<script setup lang="ts">
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
}>()

const emit = defineEmits<{ close: []; created: [] }>()

const itemDescription = ref('')
const retailer = ref('')
const returnDate = ref(new Date().toISOString().split('T')[0])
const returnReason = ref('Defective')
const purchasePrice = ref<number | null>(null)
const refundExpected = ref<number | null>(null)
const returnNotes = ref('')
const saving = ref(false)
const error = ref('')

const reasons = ['Defective', 'Wrong Item', 'Changed Mind', 'Damaged in Delivery', 'Other']

async function submit() {
  if (!itemDescription.value.trim()) return
  saving.value = true
  error.value = ''
  try {
    await frappeRequest({
      url: '/api/method/home.api.returns.create_return',
      params: {
        property: props.property,
        item_description: itemDescription.value.trim(),
        return_date: returnDate.value,
        return_reason: returnReason.value,
        retailer: retailer.value.trim() || undefined,
        purchase_price: purchasePrice.value || undefined,
        refund_expected: refundExpected.value || undefined,
        return_notes: returnNotes.value.trim() || undefined,
      },
    })
    emit('created')
  } catch (e: any) {
    error.value = e.message || __('Failed to create return')
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
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4 p-6 max-h-[90vh] overflow-y-auto"
      @keydown.escape="emit('close')"
    >
      <h2 class="text-h3 text-gray-900 dark:text-gray-100 mb-4">
        {{ __('New Return') }}
      </h2>

      <div class="space-y-3">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Item') }}
          </label>
          <input
            v-model="itemDescription"
            type="text"
            :placeholder="__('e.g. Bosch Dishwasher WAT28461')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @keyup.enter="submit"
          />
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Retailer') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <input
            v-model="retailer"
            type="text"
            :placeholder="__('e.g. MediaMarkt')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Return Date') }}
            </label>
            <input
              v-model="returnDate"
              type="date"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Reason') }}
            </label>
            <select
              v-model="returnReason"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option v-for="r in reasons" :key="r" :value="r">{{ __(r) }}</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Purchase Price') }} <span class="text-gray-400">{{ __('optional') }}</span>
            </label>
            <input
              v-model.number="purchasePrice"
              type="number"
              min="0"
              step="0.01"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Expected Refund') }} <span class="text-gray-400">{{ __('optional') }}</span>
            </label>
            <input
              v-model.number="refundExpected"
              type="number"
              min="0"
              step="0.01"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Notes') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <input
            v-model="returnNotes"
            type="text"
            :placeholder="__('Any details about the return')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      <p v-if="error" class="mt-3 text-sm text-red-600 dark:text-red-400">{{ error }}</p>

      <div class="flex justify-end gap-2 mt-5">
        <Button variant="outline" @click="emit('close')">{{ __('Cancel') }}</Button>
        <Button
          variant="solid"
          :loading="saving"
          :disabled="!itemDescription.trim()"
          @click="submit"
        >
          {{ __('Create') }}
        </Button>
      </div>
    </div>
  </div>
</template>
