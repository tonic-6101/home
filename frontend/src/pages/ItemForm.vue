<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Item creation / edit form — stays within the SPA (Feature 5).
-->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { ArrowLeft } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'

const route = useRoute()
const router = useRouter()
const { load: loadProperty } = useProperty()

const isEdit = computed(() => !!route.params.name)
const saving = ref(false)
const loading = ref(true)
const error = ref('')
const rooms = ref<{ name: string; room_name: string }[]>([])
const property = ref('')

const form = ref({
  item_name: '',
  item_type: 'Appliance' as 'Appliance' | 'Possession' | 'Fixture',
  category: '',
  room: '',
  brand: '',
  model: '',
  serial_number: '',
  purchase_date: '',
  purchase_price: '',
  notes: '',
  // Appliance
  status: 'Working',
  // Possession
  estimated_value: '',
  condition: '',
  insured: false,
  // Fixture
  installed_date: '',
  material: '',
})

const CATEGORIES = [
  'White Goods', 'HVAC', 'Heating', 'Kitchen', 'Plumbing',
  'Furniture', 'Electronics', 'Jewelry & Watches', 'Art & Collectibles',
  'Tools & Equipment', 'Clothing & Accessories', 'Musical Instruments',
  'Sports Equipment', 'Doors & Windows', 'Walls & Floors',
  'Roof & Structure', 'Garden & Landscape', 'Fixtures & Fittings',
  'Exterior', 'Other',
]

const STATUSES = ['Working', 'Needs Repair', 'Broken', 'Disposed']
const CONDITIONS = ['New', 'Excellent', 'Good', 'Fair', 'Poor']
const ITEM_TYPES = ['Appliance', 'Possession', 'Fixture']

const roomOptions = computed(() => [
  { value: '', label: __('— None —') },
  ...rooms.value.map(r => ({ value: r.name, label: r.room_name })),
])

async function loadRooms(prop: string) {
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.room.get_rooms',
      params: { property: prop },
    })
    rooms.value = res || []
  } catch {
    rooms.value = []
  }
}

async function loadExisting() {
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.item.get_item',
      params: { name: route.params.name },
    })
    property.value = res.property
    form.value.item_name = res.item_name || ''
    form.value.item_type = res.item_type || 'Appliance'
    form.value.category = res.category || ''
    form.value.room = res.room || ''
    form.value.brand = res.brand || ''
    form.value.model = res.model || ''
    form.value.serial_number = res.serial_number || ''
    form.value.purchase_date = res.purchase_date || ''
    form.value.purchase_price = res.purchase_price ?? ''
    form.value.notes = res.notes || ''
    form.value.status = res.status || 'Working'
    form.value.estimated_value = res.estimated_value ?? ''
    form.value.condition = res.condition || ''
    form.value.insured = !!res.insured
    form.value.installed_date = res.installed_date || ''
    form.value.material = res.material || ''
    await loadRooms(res.property)
  } catch (e: any) {
    error.value = e.message || __('Failed to load item')
  }
}

async function init() {
  loading.value = true
  try {
    if (isEdit.value) {
      await loadExisting()
    } else {
      const prop = await loadProperty()
      if (!prop) {
        error.value = __('No property found. Set up your property first.')
        return
      }
      property.value = prop
      await loadRooms(prop)
      // Pre-fill from query params (e.g. from scan page)
      const q = route.query
      if (q.brand) form.value.brand = q.brand as string
      if (q.model) form.value.model = q.model as string
      if (q.serial_number) form.value.serial_number = q.serial_number as string
      if (q.category) form.value.category = q.category as string
    }
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!form.value.item_name.trim()) {
    error.value = __('Item name is required')
    return
  }
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      await frappeRequest({
        url: '/api/method/frappe.client.set_value',
        params: {
          doctype: 'Home Item',
          name: route.params.name,
          fieldname: buildPayload(),
        },
      })
      router.push(`/home/items/${route.params.name}`)
    } else {
      const res = await frappeRequest({
        url: '/api/method/frappe.client.insert',
        params: {
          doc: {
            doctype: 'Home Item',
            property: property.value,
            ...buildPayload(),
          },
        },
      })
      router.push(`/home/items/${res.name}`)
    }
  } catch (e: any) {
    error.value = e.message || e._server_messages || __('Failed to save')
    saving.value = false
  }
}

function buildPayload(): Record<string, any> {
  const data: Record<string, any> = {
    item_name: form.value.item_name.trim(),
    item_type: form.value.item_type,
    category: form.value.category || null,
    room: form.value.room || null,
    brand: form.value.brand || null,
    model: form.value.model || null,
    serial_number: form.value.serial_number || null,
    purchase_date: form.value.purchase_date || null,
    purchase_price: form.value.purchase_price ? Number(form.value.purchase_price) : null,
    notes: form.value.notes || null,
  }

  // Insurance fields — all item types
  data.estimated_value = form.value.estimated_value ? Number(form.value.estimated_value) : null
  data.insured = form.value.insured ? 1 : 0

  if (form.value.item_type === 'Appliance') {
    data.status = form.value.status
  }
  if (form.value.item_type === 'Possession') {
    data.condition = form.value.condition || null
  }
  if (form.value.item_type === 'Fixture') {
    data.installed_date = form.value.installed_date || null
    data.material = form.value.material || null
  }

  return data
}

function goBack() {
  if (isEdit.value) {
    router.push(`/home/items/${route.params.name}`)
  } else {
    router.push('/home/items')
  }
}

onMounted(init)
</script>

<template>
  <div class="p-6 max-w-2xl mx-auto">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button
        @click="goBack"
        class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        <ArrowLeft class="w-5 h-5 text-gray-500 dark:text-gray-400" />
      </button>
      <h1 class="text-h1 text-gray-900 dark:text-gray-100">
        {{ isEdit ? __('Edit Item') : __('Add Item') }}
      </h1>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <template v-else>
      <!-- Error banner -->
      <div
        v-if="error"
        class="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm"
      >
        {{ error }}
      </div>

      <form @submit.prevent="save" class="space-y-5">
        <!-- Item Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ __('Item Name') }} <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.item_name"
            type="text"
            required
            :placeholder="__('e.g. Bosch Dishwasher, Leather sofa, Front door')"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 px-3 py-2 text-sm
                   text-gray-900 dark:text-gray-100
                   placeholder-gray-400 dark:placeholder-gray-500
                   focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
          />
        </div>

        <!-- Item Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ __('Type') }} <span class="text-red-500">*</span>
          </label>
          <div class="flex gap-2">
            <button
              v-for="t in ITEM_TYPES"
              :key="t"
              type="button"
              @click="form.item_type = t as any"
              class="px-4 py-2 text-sm rounded-lg border transition-colors"
              :class="form.item_type === t
                ? 'bg-accent-50 dark:bg-accent-900/30 border-accent-500 text-accent-700 dark:text-accent-400'
                : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'"
            >
              {{ __(t) }}
            </button>
          </div>
        </div>

        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ __('Category') }}
          </label>
          <select
            v-model="form.category"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 px-3 py-2 text-sm
                   text-gray-900 dark:text-gray-100
                   focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
          >
            <option value="">{{ __('— Select —') }}</option>
            <option v-for="c in CATEGORIES" :key="c" :value="c">{{ __(c) }}</option>
          </select>
        </div>

        <!-- Room -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ __('Room') }}
          </label>
          <select
            v-model="form.room"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 px-3 py-2 text-sm
                   text-gray-900 dark:text-gray-100
                   focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
          >
            <option v-for="r in roomOptions" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
        </div>

        <!-- Brand + Model -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ __('Brand') }}
            </label>
            <input
              v-model="form.brand"
              type="text"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800 px-3 py-2 text-sm
                     text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ __('Model') }}
            </label>
            <input
              v-model="form.model"
              type="text"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800 px-3 py-2 text-sm
                     text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
            />
          </div>
        </div>

        <!-- Serial Number -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ __('Serial Number') }}
          </label>
          <input
            v-model="form.serial_number"
            type="text"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 px-3 py-2 text-sm
                   text-gray-900 dark:text-gray-100
                   focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
          />
        </div>

        <!-- Purchase Date + Price -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ __('Purchase Date') }}
            </label>
            <input
              v-model="form.purchase_date"
              type="date"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800 px-3 py-2 text-sm
                     text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ __('Purchase Price') }}
            </label>
            <input
              v-model="form.purchase_price"
              type="number"
              step="0.01"
              min="0"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800 px-3 py-2 text-sm
                     text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
            />
          </div>
        </div>

        <!-- Appliance fields -->
        <div v-if="form.item_type === 'Appliance'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ __('Status') }}
          </label>
          <select
            v-model="form.status"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 px-3 py-2 text-sm
                   text-gray-900 dark:text-gray-100
                   focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
          >
            <option v-for="s in STATUSES" :key="s" :value="s">{{ __(s) }}</option>
          </select>
        </div>

        <!-- Possession fields -->
        <template v-if="form.item_type === 'Possession'">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ __('Condition') }}
            </label>
            <select
              v-model="form.condition"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800 px-3 py-2 text-sm
                     text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
            >
              <option value="">{{ __('— Select —') }}</option>
              <option v-for="c in CONDITIONS" :key="c" :value="c">{{ __(c) }}</option>
            </select>
          </div>
        </template>

        <!-- Fixture fields -->
        <template v-if="form.item_type === 'Fixture'">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ __('Installed Date') }}
              </label>
              <input
                v-model="form.installed_date"
                type="date"
                class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-800 px-3 py-2 text-sm
                       text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ __('Material') }}
              </label>
              <input
                v-model="form.material"
                type="text"
                :placeholder="__('e.g. Oak, PVC, Brick')"
                class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-800 px-3 py-2 text-sm
                       text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
              />
            </div>
          </div>
        </template>

        <!-- Insurance (all item types) -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
          <h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-3">{{ __('Insurance') }}</h3>
          <div class="grid grid-cols-2 gap-4 mb-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ __('Estimated Value') }}
              </label>
              <input
                v-model="form.estimated_value"
                type="number"
                step="0.01"
                min="0"
                class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-800 px-3 py-2 text-sm
                       text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
              />
            </div>
            <div class="flex items-end pb-2">
              <div class="flex items-center gap-2">
                <input
                  v-model="form.insured"
                  type="checkbox"
                  id="insured"
                  class="rounded border-gray-300 dark:border-gray-600 text-accent-600 focus:ring-accent-500"
                />
                <label for="insured" class="text-sm text-gray-700 dark:text-gray-300">
                  {{ __('Specifically insured') }}
                </label>
              </div>
            </div>
          </div>
          <p class="text-xs text-gray-400 dark:text-gray-500">
            {{ __('\"Specifically insured\" means this item is individually listed on your insurance policy.') }}
          </p>
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ __('Notes') }}
          </label>
          <textarea
            v-model="form.notes"
            rows="3"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600
                   bg-white dark:bg-gray-800 px-3 py-2 text-sm
                   text-gray-900 dark:text-gray-100
                   placeholder-gray-400 dark:placeholder-gray-500
                   focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
          />
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-3 pt-2">
          <button
            type="submit"
            class="rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50"
            :disabled="saving"
          >
            {{ saving ? __('Saving…') : (isEdit ? __('Save Changes') : __('Create Item')) }}
          </button>
          <button
            type="button"
            class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            @click="goBack"
          >
            {{ __('Cancel') }}
          </button>
        </div>
      </form>
    </template>
  </div>
</template>
