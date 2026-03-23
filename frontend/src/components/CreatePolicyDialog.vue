<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Create Insurance Policy dialog (Feature 28).
-->
<script setup lang="ts">
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
}>()

const emit = defineEmits<{ close: []; created: [] }>()

const policyName = ref('')
const policyType = ref('Contents')
const provider = ref('')
const endDate = ref('')
const premiumAnnual = ref<number | null>(null)
const renewalNoticeDays = ref(60)
const saving = ref(false)
const error = ref('')

const policyTypes = [
  'Buildings', 'Contents', 'Liability', 'Legal Protection', 'Flood', 'Other',
]

async function submit() {
  if (!policyName.value.trim() || !provider.value.trim() || !endDate.value) return
  saving.value = true
  error.value = ''
  try {
    await frappeRequest({
      url: '/api/method/home.api.insurance.create_policy',
      params: {
        property: props.property,
        policy_name: policyName.value.trim(),
        policy_type: policyType.value,
        provider: provider.value.trim(),
        start_date: new Date().toISOString().split('T')[0],
        end_date: endDate.value,
        premium_annual: premiumAnnual.value || undefined,
        renewal_notice_days: renewalNoticeDays.value,
      },
    })
    emit('created')
  } catch (e: any) {
    error.value = e.message || __('Failed to create policy')
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
        {{ __('Add Insurance Policy') }}
      </h2>

      <div class="space-y-3">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Policy Name') }}
          </label>
          <input
            v-model="policyName"
            type="text"
            :placeholder="__('e.g. Home Contents — Allianz')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @keyup.enter="submit"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Type') }}
            </label>
            <select
              v-model="policyType"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option v-for="t in policyTypes" :key="t" :value="t">{{ __(t) }}</option>
            </select>
          </div>
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Provider') }}
            </label>
            <input
              v-model="provider"
              type="text"
              :placeholder="__('e.g. Allianz')"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Renewal Date') }}
            </label>
            <input
              v-model="endDate"
              type="date"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Premium') }} <span class="text-gray-400">{{ __('/yr') }}</span>
            </label>
            <input
              v-model.number="premiumAnnual"
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
            {{ __('Alert before renewal (days)') }}
          </label>
          <input
            v-model.number="renewalNoticeDays"
            type="number"
            min="1"
            max="365"
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
          :disabled="!policyName.trim() || !provider.trim() || !endDate"
          @click="submit"
        >
          {{ __('Add') }}
        </Button>
      </div>
    </div>
  </div>
</template>
