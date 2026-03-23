<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Add / edit improvement wish dialog (Feature 45).
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  wish?: any | null
}>()

const emit = defineEmits<{ close: []; saved: [] }>()

const isEdit = !!props.wish

const title = ref(props.wish?.title || '')
const category = ref(props.wish?.category || 'Other')
const priority = ref(props.wish?.priority || 'Nice to have')
const estimatedCost = ref<number | null>(props.wish?.estimated_cost ?? null)
const room = ref(props.wish?.room || '')
const notes = ref(props.wish?.notes || '')
const saving = ref(false)

const rooms = ref<{ name: string; room_name: string }[]>([])

const categories = [
  'Cosmetic', 'Structural', 'Energy Efficiency', 'Comfort',
  'Safety', 'Garden', 'Technology', 'Other',
]

const priorities = ['Urgent', 'Important', 'Nice to have']

async function loadRooms() {
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.room.get_rooms',
      params: { property: props.property },
    })
    rooms.value = res || []
  } catch {
    // Rooms are optional — ignore errors
  }
}

async function submit() {
  if (!title.value.trim()) return
  saving.value = true
  try {
    if (isEdit) {
      await frappeRequest({
        url: '/api/method/home.api.wishlist.update_wish',
        params: {
          name: props.wish.name,
          title: title.value.trim(),
          category: category.value,
          priority: priority.value,
          estimated_cost: estimatedCost.value ?? 0,
          room: room.value || '',
          notes: notes.value.trim(),
        },
      })
    } else {
      await frappeRequest({
        url: '/api/method/home.api.wishlist.create_wish',
        params: {
          property: props.property,
          title: title.value.trim(),
          category: category.value,
          priority: priority.value,
          estimated_cost: estimatedCost.value ?? undefined,
          room: room.value || undefined,
          notes: notes.value.trim() || undefined,
        },
      })
    }
    emit('saved')
  } catch (e: any) {
    alert(e.message || __('Failed to save'))
  } finally {
    saving.value = false
  }
}

onMounted(loadRooms)
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4 p-6"
      @keydown.escape="emit('close')"
    >
      <h2 class="text-h3 text-gray-900 dark:text-gray-100 mb-4">
        {{ isEdit ? __('Edit Wish') : __('Add Improvement Wish') }}
      </h2>

      <div class="space-y-3">
        <!-- Title -->
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Title') }}
          </label>
          <input
            v-model="title"
            type="text"
            :placeholder="__('e.g. Replace kitchen worktops')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>

        <!-- Category -->
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Category') }}
          </label>
          <select
            v-model="category"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
          </select>
        </div>

        <!-- Priority -->
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Priority') }}
          </label>
          <select
            v-model="priority"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option v-for="p in priorities" :key="p" :value="p">{{ __(p) }}</option>
          </select>
        </div>

        <!-- Room (optional) -->
        <div v-if="rooms.length > 0">
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Room') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <select
            v-model="room"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">{{ __('Whole property') }}</option>
            <option v-for="r in rooms" :key="r.name" :value="r.name">{{ r.room_name }}</option>
          </select>
        </div>

        <!-- Estimated cost -->
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Estimated cost') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">€</span>
            <input
              v-model.number="estimatedCost"
              type="number"
              min="0"
              step="100"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-7 pr-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
        </div>

        <!-- Notes -->
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Notes') }} <span class="text-gray-400">{{ __('optional') }}</span>
          </label>
          <textarea
            v-model="notes"
            rows="3"
            :placeholder="__('Ideas, measurements, inspiration…')"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      <div class="flex justify-end gap-2 mt-5">
        <Button variant="outline" @click="emit('close')">{{ __('Cancel') }}</Button>
        <Button
          variant="solid"
          :loading="saving"
          :disabled="!title.trim()"
          @click="submit"
        >
          {{ isEdit ? __('Save') : __('Add') }}
        </Button>
      </div>
    </div>
  </div>
</template>
