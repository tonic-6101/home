<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Add Room inline dialog (Feature 3).
-->
<script setup lang="ts">
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{ property: string }>()
const emit = defineEmits<{ close: []; created: [] }>()

const roomName = ref('')
const roomType = ref('')
const areaSqm = ref<number | null>(null)
const saving = ref(false)
const error = ref('')

const roomTypes = ['Kitchen', 'Bedroom', 'Bathroom', 'Living Room', 'Garage', 'Storage', 'Other']

async function submit() {
  if (!roomName.value.trim()) return
  saving.value = true
  error.value = ''
  try {
    await frappeRequest({
      url: '/api/method/home.api.room.create_room',
      params: {
        property: props.property,
        room_name: roomName.value.trim(),
        room_type: roomType.value,
        area_sqm: areaSqm.value || undefined,
      },
    })
    emit('created')
  } catch (e: any) {
    error.value = e.message || __('Failed to create room')
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
      <h3 class="text-h4 text-gray-900 dark:text-gray-100 mb-4">
        {{ __('Add Room') }}
      </h3>

      <div class="space-y-3">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Room Name') }}
          </label>
          <input
            v-model="roomName"
            type="text"
            :placeholder="__('e.g. Kitchen')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @keyup.enter="submit"
          />
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Room Type') }}
          </label>
          <select
            v-model="roomType"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">{{ __('Select…') }}</option>
            <option v-for="t in roomTypes" :key="t" :value="t">{{ __(t) }}</option>
          </select>
        </div>

        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Area (m²)') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <input
            v-model.number="areaSqm"
            type="number"
            min="0"
            step="0.1"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      <p v-if="error" class="mt-2 text-sm text-red-600 dark:text-red-400">{{ error }}</p>

      <div class="flex justify-end gap-2 mt-5">
        <Button variant="outline" @click="emit('close')">{{ __('Cancel') }}</Button>
        <Button variant="solid" :loading="saving" @click="submit">{{ __('Add') }}</Button>
      </div>
    </div>
  </div>
</template>
