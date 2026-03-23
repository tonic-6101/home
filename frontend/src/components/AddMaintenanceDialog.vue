<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Add Maintenance Task dialog — used from Dashboard, ItemDetail, and RoomCardGrid (Feature 11).
-->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  room?: string
  roomName?: string
  item?: string
  itemName?: string
  itemCategory?: string
}>()

const emit = defineEmits<{ close: []; created: [] }>()
const router = useRouter()

const title = ref('')
const category = ref(props.itemCategory || '')
const maintenanceType = ref('One-off')
const recurrence = ref('')
const scheduledDate = ref('')
const saving = ref(false)
const error = ref('')

const categories = [
  'Plumbing', 'Electrical', 'HVAC & Heating', 'Painting & Decorating',
  'Carpentry', 'Roofing & Gutters', 'Cleaning', 'Garden & Landscaping',
  'Pest Control', 'Inspection', 'General Repair', 'Other',
]

const maintenanceTypes = ['One-off', 'Recurring']

const recurrenceOptions = ['Weekly', 'Bi-weekly', 'Monthly', 'Quarterly', 'Bi-annual', 'Annual']

const contextLabel = computed(() => {
  const parts: string[] = []
  if (props.itemName) parts.push(props.itemName)
  if (props.roomName) parts.push(props.roomName)
  return parts.join(' — ')
})

async function submit() {
  if (!title.value.trim()) return
  saving.value = true
  error.value = ''
  try {
    const res = await frappeRequest({
      url: '/api/method/frappe.client.insert',
      params: {
        doc: {
          doctype: 'Home Maintenance',
          title: title.value.trim(),
          property: props.property,
          room: props.room || undefined,
          item: props.item || undefined,
          category: category.value || undefined,
          maintenance_type: maintenanceType.value,
          recurrence: maintenanceType.value === 'Recurring' ? recurrence.value || undefined : undefined,
          scheduled_date: scheduledDate.value || undefined,
          status: 'Scheduled',
        },
      },
    })
    emit('created')
    router.push(`/home/maintenance/${res.name}`)
  } catch (e: any) {
    error.value = e.message || __('Failed to create task')
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
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-sm mx-4 p-5"
      @keydown.escape="emit('close')"
    >
      <h3 class="text-h4 text-gray-900 dark:text-gray-100 mb-1">
        {{ __('Log Maintenance Task') }}
      </h3>
      <p v-if="contextLabel" class="text-xs text-gray-500 dark:text-gray-400 mb-4">
        {{ contextLabel }}
      </p>
      <div v-else class="mb-4" />

      <div class="space-y-3">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Title') }}
          </label>
          <input
            v-model="title"
            type="text"
            :placeholder="__('e.g. Annual boiler service')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @keyup.enter="submit"
          />
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Category') }}
          </label>
          <select
            v-model="category"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">{{ __('Select…') }}</option>
            <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
          </select>
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Type') }}
          </label>
          <select
            v-model="maintenanceType"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option v-for="t in maintenanceTypes" :key="t" :value="t">{{ __(t) }}</option>
          </select>
        </div>

        <div v-if="maintenanceType === 'Recurring'">
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Recurrence') }}
          </label>
          <select
            v-model="recurrence"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">{{ __('Select…') }}</option>
            <option v-for="r in recurrenceOptions" :key="r" :value="r">{{ __(r) }}</option>
          </select>
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Scheduled date') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <input
            v-model="scheduledDate"
            type="date"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      <p v-if="error" class="mt-2 text-sm text-red-600 dark:text-red-400">{{ error }}</p>

      <div class="flex justify-end gap-2 mt-5">
        <Button variant="outline" @click="emit('close')">{{ __('Cancel') }}</Button>
        <Button variant="solid" :loading="saving" @click="submit">{{ __('Create') }}</Button>
      </div>
    </div>
  </div>
</template>
