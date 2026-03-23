<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Smart delete room dialog (Feature 3).
  Empty rooms → simple confirm. Rooms with records → move-to dropdown.
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

interface Room {
  name: string
  room_name: string
  room_type: string
  item_count: number
  open_task_count: number
}

const props = defineProps<{
  room: Room
  allRooms: Room[]
}>()
const emit = defineEmits<{ close: []; deleted: [] }>()

const itemCount = ref(0)
const loadingCounts = ref(true)
const moveTo = ref<string>('')
const deleting = ref(false)

const hasLinkedRecords = computed(() => itemCount.value > 0)

const otherRooms = computed(() =>
  props.allRooms.filter(r => r.name !== props.room.name)
)

async function loadCounts() {
  loadingCounts.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.room.get_room_counts',
      params: { name: props.room.name },
    })
    const data = res || {}
    itemCount.value = data.item_count || 0
  } catch {
    // Fall back to prop counts
    itemCount.value = props.room.item_count || 0
  } finally {
    loadingCounts.value = false
  }
}

async function confirmDelete() {
  deleting.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.room.delete_room',
      params: {
        name: props.room.name,
        move_to: moveTo.value || undefined,
      },
    })
    emit('deleted')
  } catch (e: any) {
    alert(e.message || __('Failed to delete room'))
    deleting.value = false
  }
}

onMounted(loadCounts)
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
      <h3 class="text-h4 text-gray-900 dark:text-gray-100 mb-3">
        {{ __('Delete {0}?').replace('{0}', room.room_name) }}
      </h3>

      <div v-if="loadingCounts" class="text-sm text-gray-500">
        {{ __('Checking linked records…') }}
      </div>

      <template v-else>
        <!-- Simple confirm for empty rooms -->
        <p v-if="!hasLinkedRecords" class="text-sm text-gray-600 dark:text-gray-400">
          {{ __('This room has no items. It will be permanently deleted.') }}
        </p>

        <!-- Move-to dialog for rooms with records -->
        <template v-else>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
            {{ __('This room has {0} item(s).')
              .replace('{0}', String(itemCount))
            }}
          </p>

          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Move items to:') }}
            </label>
            <select
              v-model="moveTo"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="">{{ __('Unassigned') }}</option>
              <option
                v-for="r in otherRooms"
                :key="r.name"
                :value="r.name"
              >
                {{ r.room_name }}
              </option>
            </select>
          </div>
        </template>
      </template>

      <div class="flex justify-end gap-2 mt-5">
        <Button variant="outline" @click="emit('close')">{{ __('Cancel') }}</Button>
        <Button
          variant="solid"
          theme="red"
          :loading="deleting"
          :disabled="loadingCounts"
          @click="confirmDelete"
        >
          {{ hasLinkedRecords ? __('Delete & move items') : __('Delete') }}
        </Button>
      </div>
    </div>
  </div>
</template>
