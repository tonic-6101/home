<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Unified item list page — appliances, possessions, fixtures, warranties (Feature 5).
-->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { Refrigerator, Package, Check, Scale, X } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'

interface HomeItem {
  name: string
  item_name: string
  item_type: 'Appliance' | 'Possession' | 'Fixture'
  category: string
  brand: string | null
  model: string | null
  status: string | null
  condition: string | null
  room: string | null
  insured: boolean
  material: string | null
  installed_date: string | null
}

interface WarrantyRow {
  warranty_name: string
  item: string
  item_name: string
  warranty_type: string
  provider: string | null
  end_date: string
  burden_of_proof_date: string | null
  expiry_status: 'active' | 'expiring_soon' | 'expired'
  days_remaining: number
}

interface ItemsData {
  items: HomeItem[]
  warranties: WarrantyRow[]
  total_estimated_value: number
  insured_value: number
  insured_count: number
}

type TabKey = 'all' | 'Appliance' | 'Possession' | 'Fixture' | 'warranties'

const router = useRouter()
const route = useRoute()
const { load: loadProperty } = useProperty()
const data = ref<ItemsData | null>(null)
const loading = ref(true)
const noProperty = ref(false)
const activeTab = ref<TabKey>((route.query.tab as TabKey) || 'all')
const roomFilter = ref<string | null>((route.query.room as string) || null)
const roomFilterLabel = computed(() => {
  if (!roomFilter.value) return ''
  if (roomFilter.value === 'unassigned') return __('Unassigned')
  return (route.query.room_name as string) || roomFilter.value
})

async function loadItems() {
  loading.value = true
  try {
    const property = await loadProperty()
    if (!property) {
      noProperty.value = true
      return
    }
    const params: Record<string, string> = { property }
    if (roomFilter.value && roomFilter.value !== 'unassigned') {
      params.room = roomFilter.value
    }
    const res = await frappeRequest({
      url: '/api/method/home.api.item.get_items',
      params,
    })
    data.value = res

    // For "unassigned", client-side filter items with no room
    if (roomFilter.value === 'unassigned' && data.value) {
      data.value = {
        ...data.value,
        items: data.value.items.filter(i => !i.room),
      }
    }
  } catch {
    data.value = null
  } finally {
    loading.value = false
  }
}

function clearRoomFilter() {
  roomFilter.value = null
  const { room, room_name, ...rest } = route.query
  router.replace({ path: '/home/items', query: rest })
  loadItems()
}

watch(() => route.query.room, (newRoom) => {
  const val = (newRoom as string) || null
  if (val !== roomFilter.value) {
    roomFilter.value = val
    loadItems()
  }
})

const filteredItems = computed(() => {
  if (!data.value?.items) return []
  if (activeTab.value === 'all') return data.value.items
  if (activeTab.value === 'warranties') return [] // warranties tab uses its own data
  return data.value.items.filter(i => i.item_type === activeTab.value)
})

const filteredWarranties = computed(() => {
  if (!data.value?.warranties) return []
  return data.value.warranties
})

const statusColors: Record<string, string> = {
  Working: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  'Needs Repair': 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  Broken: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  Disposed: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
}

const warrantyStatusColors: Record<string, string> = {
  active: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  expiring_soon: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  expired: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
}

const conditionColors: Record<string, string> = {
  New: 'text-green-600 dark:text-green-400',
  Good: 'text-blue-600 dark:text-blue-400',
  Fair: 'text-amber-600 dark:text-amber-400',
  Poor: 'text-red-600 dark:text-red-400',
}

function formatCurrency(value: number): string {
  if (!value) return '—'
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
  }).format(value)
}

function formatDate(date: string | null): string {
  if (!date) return '—'
  return new Date(date).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function warrantyStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    active: __('Active'),
    expiring_soon: __('Expiring soon'),
    expired: __('Expired'),
  }
  return labels[status] || status
}

const tabs: { key: TabKey; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'Appliance', label: 'Appliances' },
  { key: 'Possession', label: 'Possessions' },
  { key: 'Fixture', label: 'Fixtures' },
  { key: 'warranties', label: 'Warranties' },
]

function addItem() {
  router.push('/home/items/new')
}

onMounted(loadItems)
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-h1 text-gray-900 dark:text-gray-100">
        {{ __('Items') }}
      </h1>
      <button
        data-tour="add-item"
        class="rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50"
        @click="addItem"
      >
        {{ __('Add Item') }}
      </button>
    </div>

    <!-- Room filter chip -->
    <div v-if="roomFilter" class="mb-4">
      <span
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm
               bg-accent-100 dark:bg-accent-900/30 text-accent-700 dark:text-accent-300"
      >
        {{ __('Room') }}: {{ roomFilterLabel }}
        <button
          @click="clearRoomFilter"
          class="ml-0.5 p-0.5 rounded-full hover:bg-accent-200 dark:hover:bg-accent-800 transition-colors"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- No property -->
    <div v-else-if="noProperty" class="text-center py-12">
      <Package class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No property yet') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('Set up your property first to manage items.') }}
      </p>
    </div>

    <!-- Empty -->
    <div v-else-if="!data || !data.items.length" class="text-center py-12">
      <Package class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No items') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400 mb-4">
        {{ __('No items registered yet.') }}
      </p>
      <button
        class="rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50"
        @click="addItem"
      >
        {{ __('Add Item') }}
      </button>
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="flex gap-1 mb-4 border-b border-gray-200 dark:border-gray-700">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="px-4 py-2 text-sm font-medium transition-colors -mb-px"
          :class="activeTab === tab.key
            ? 'text-accent-600 dark:text-accent-400 border-b-2 border-accent-500'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="activeTab = tab.key"
        >
          {{ __(tab.label) }}
        </button>
      </div>

      <!-- Summary bar -->
      <div v-if="activeTab !== 'warranties'" class="flex gap-4 mb-4 text-sm text-gray-500 dark:text-gray-400">
        <span>{{ filteredItems.length }} {{ filteredItems.length === 1 ? __('item') : __('items') }}</span>
        <span v-if="data.total_estimated_value">
          {{ __('Total value') }}: {{ formatCurrency(data.total_estimated_value) }}
        </span>
        <span v-if="data.insured_count">
          {{ data.insured_count }} {{ __('insured') }}
          <template v-if="data.insured_value"> ({{ formatCurrency(data.insured_value) }})</template>
        </span>
      </div>
      <div v-else class="flex gap-4 mb-4 text-sm text-gray-500 dark:text-gray-400">
        <span>{{ filteredWarranties.length }} {{ filteredWarranties.length === 1 ? __('warranty') : __('warranties') }}</span>
      </div>

      <!-- Warranties table -->
      <div v-if="activeTab === 'warranties'" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700 text-left">
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Item') }}</th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Type') }}</th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Provider') }}</th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Expires') }}</th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="w in filteredWarranties"
              :key="w.warranty_name"
              class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800
                     cursor-pointer transition-colors"
              @click="router.push(`/home/items/${w.item}?tab=warranty`)"
            >
              <td class="py-3 pr-4">
                <span class="font-medium text-gray-900 dark:text-gray-100">{{ w.item_name }}</span>
              </td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">
                <span class="flex items-center gap-1">
                  <Scale v-if="w.warranty_type === 'Legal'" class="w-3.5 h-3.5 text-gray-400" />
                  {{ __(w.warranty_type) }}
                </span>
              </td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">{{ w.provider || '—' }}</td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">
                {{ formatDate(w.end_date) }}
                <span v-if="w.expiry_status !== 'expired'" class="text-xs ml-1">
                  ({{ w.days_remaining }}d)
                </span>
              </td>
              <td class="py-3 pr-4">
                <span
                  class="text-xs px-2 py-0.5 rounded-full"
                  :class="warrantyStatusColors[w.expiry_status] || warrantyStatusColors.active"
                >
                  {{ warrantyStatusLabel(w.expiry_status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!filteredWarranties.length" class="text-center py-8 text-gray-500 dark:text-gray-400">
          {{ __('No warranties recorded yet.') }}
        </div>
      </div>

      <!-- Items table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700 text-left">
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Item') }}</th>
              <th v-if="activeTab === 'all'" class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Type') }}</th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Category') }}</th>
              <th v-if="activeTab !== 'Possession'" class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Brand') }}</th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">
                <template v-if="activeTab === 'Possession'">{{ __('Condition') }}</template>
                <template v-else-if="activeTab === 'Fixture'">{{ __('Material') }}</template>
                <template v-else>{{ __('Status') }}</template>
              </th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400">{{ __('Room') }}</th>
              <th class="pb-2 font-medium text-gray-500 dark:text-gray-400 text-center">{{ __('Insured') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in filteredItems"
              :key="item.name"
              class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800
                     cursor-pointer transition-colors"
              @click="router.push(`/home/items/${item.name}`)"
            >
              <td class="py-3 pr-4">
                <span class="font-medium text-gray-900 dark:text-gray-100">{{ item.item_name }}</span>
              </td>
              <td v-if="activeTab === 'all'" class="py-3 pr-4 text-gray-600 dark:text-gray-400">
                {{ __(item.item_type) }}
              </td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">{{ __(item.category) }}</td>
              <td v-if="activeTab !== 'Possession'" class="py-3 pr-4 text-gray-600 dark:text-gray-400">
                {{ item.brand || '—' }}
              </td>
              <td class="py-3 pr-4">
                <template v-if="item.item_type === 'Appliance' && item.status">
                  <span
                    class="text-xs px-2 py-0.5 rounded-full"
                    :class="statusColors[item.status] || 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'"
                  >
                    {{ __(item.status) }}
                  </span>
                </template>
                <template v-else-if="item.item_type === 'Possession' && item.condition">
                  <span :class="conditionColors[item.condition] || 'text-gray-600 dark:text-gray-400'">
                    {{ __(item.condition) }}
                  </span>
                </template>
                <template v-else-if="item.item_type === 'Fixture'">
                  {{ item.material || '—' }}
                </template>
                <template v-else>—</template>
              </td>
              <td class="py-3 pr-4 text-gray-600 dark:text-gray-400">{{ item.room || '—' }}</td>
              <td class="py-3 text-center">
                <Check v-if="item.insured" class="w-4 h-4 mx-auto text-green-600 dark:text-green-400" />
                <span v-else class="text-gray-300 dark:text-gray-600">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
