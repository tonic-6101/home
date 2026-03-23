<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Maintenance list page — grouped status sections (Feature 11).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { Wrench, ChevronRight, Plus, RefreshCw, X } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'
import { useHouseholdRole } from '@/composables/useHouseholdRole'
import AddMaintenanceDialog from '@/components/AddMaintenanceDialog.vue'

interface MaintenanceTask {
  name: string
  title: string
  category: string
  status: string
  maintenance_type: string
  recurrence: string | null
  scheduled_date: string | null
  completed_date: string | null
  room: string | null
  room_name?: string
  item: string | null
  item_name?: string
  contractor: string | null
  contractor_name?: string
  cost: number | null
  overdue?: boolean
  is_today?: boolean
}

interface MaintenanceData {
  overdue: MaintenanceTask[]
  today: MaintenanceTask[]
  scheduled: MaintenanceTask[]
  in_progress: MaintenanceTask[]
  completed: MaintenanceTask[]
  cancelled: MaintenanceTask[]
}

interface RoomOption {
  name: string
  room_name: string
}

interface ItemOption {
  name: string
  item_name: string
}

const { load: loadProperty } = useProperty()
const { isAdultOrAbove, isChild, load: loadRole } = useHouseholdRole()
const data = ref<MaintenanceData | null>(null)
const loading = ref(true)
const noProperty = ref(false)
const propertyName = ref('')
const showCompleted = ref(false)
const showCancelled = ref(false)
const showAddDialog = ref(false)

// Filters
const filterCategory = ref<string[]>([])
const filterRoom = ref<string[]>([])
const filterItem = ref<string[]>([])
const roomOptions = ref<RoomOption[]>([])
const itemOptions = ref<ItemOption[]>([])

const categories = [
  'Plumbing', 'Electrical', 'HVAC & Heating', 'Painting & Decorating',
  'Carpentry', 'Roofing & Gutters', 'Cleaning', 'Garden & Landscaping',
  'Pest Control', 'Inspection', 'General Repair', 'Other',
]

const hasActiveFilters = computed(() =>
  filterCategory.value.length > 0 || filterRoom.value.length > 0 || filterItem.value.length > 0
)

function matchesFilters(task: MaintenanceTask): boolean {
  if (filterCategory.value.length && !filterCategory.value.includes(task.category)) return false
  if (filterRoom.value.length && (!task.room || !filterRoom.value.includes(task.room))) return false
  if (filterItem.value.length && (!task.item || !filterItem.value.includes(task.item))) return false
  return true
}

function filterGroup(tasks: MaintenanceTask[]): MaintenanceTask[] {
  if (!hasActiveFilters.value) return tasks
  return tasks.filter(matchesFilters)
}

const filtered = computed(() => {
  if (!data.value) return null
  return {
    overdue: filterGroup(data.value.overdue),
    today: filterGroup(data.value.today),
    scheduled: filterGroup(data.value.scheduled),
    in_progress: filterGroup(data.value.in_progress),
    completed: filterGroup(data.value.completed),
    cancelled: filterGroup(data.value.cancelled),
  }
})

const allEmpty = computed(() => {
  if (!filtered.value) return true
  const d = filtered.value
  return !d.overdue.length && !d.today.length && !d.scheduled.length
    && !d.in_progress.length && !d.completed.length && !d.cancelled.length
})

// Resolve display names for rooms, items, contractors
const roomNameMap = ref<Record<string, string>>({})
const itemNameMap = ref<Record<string, string>>({})
const contractorNameMap = ref<Record<string, string>>({})

function getRoomName(task: MaintenanceTask): string {
  if (!task.room) return ''
  return roomNameMap.value[task.room] || ''
}

function getItemName(task: MaintenanceTask): string {
  if (!task.item) return ''
  return itemNameMap.value[task.item] || ''
}

function getContractorName(task: MaintenanceTask): string {
  if (!task.contractor) return ''
  return contractorNameMap.value[task.contractor] || ''
}

function contextParts(task: MaintenanceTask): string {
  const parts: string[] = []
  const room = getRoomName(task)
  const item = getItemName(task)
  if (room) parts.push(room)
  if (item) parts.push(item)
  return parts.join(' · ')
}

function removeFilter(type: 'category' | 'room' | 'item', value: string) {
  if (type === 'category') filterCategory.value = filterCategory.value.filter(v => v !== value)
  if (type === 'room') filterRoom.value = filterRoom.value.filter(v => v !== value)
  if (type === 'item') filterItem.value = filterItem.value.filter(v => v !== value)
}

function clearFilters() {
  filterCategory.value = []
  filterRoom.value = []
  filterItem.value = []
}

function toggleFilter(arr: string[], value: string): string[] {
  return arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value]
}

async function loadTasks() {
  loading.value = true
  try {
    const property = await loadProperty()
    if (!property) {
      noProperty.value = true
      return
    }
    propertyName.value = property
    const [res, rooms, items] = await Promise.all([
      frappeRequest({
        url: '/api/method/home.api.maintenance.get_maintenance_list',
        params: { property },
      }),
      frappeRequest({
        url: '/api/method/home.api.room.get_rooms',
        params: { property },
      }),
      frappeRequest({
        url: '/api/method/home.api.item.get_items',
        params: { property },
      }),
    ])
    data.value = res

    // Build room name map + options
    const roomList = (rooms as any)?.rooms ?? rooms ?? []
    const rMap: Record<string, string> = {}
    const rOpts: RoomOption[] = []
    for (const r of roomList) {
      rMap[r.name] = r.room_name
      rOpts.push({ name: r.name, room_name: r.room_name })
    }
    roomNameMap.value = rMap
    roomOptions.value = rOpts

    // Build item name map + options
    const itemList = (items as any)?.items ?? items ?? []
    const iMap: Record<string, string> = {}
    const iOpts: ItemOption[] = []
    for (const i of itemList) {
      iMap[i.name] = i.item_name
      iOpts.push({ name: i.name, item_name: i.item_name })
    }
    itemNameMap.value = iMap
    itemOptions.value = iOpts

    // Build contractor name map from tasks
    const cMap: Record<string, string> = {}
    const allTasks = [
      ...res.overdue, ...res.today, ...res.scheduled,
      ...res.in_progress, ...res.completed, ...res.cancelled,
    ]
    const contractorIds = [...new Set(allTasks.filter((t: any) => t.contractor).map((t: any) => t.contractor))]
    if (contractorIds.length) {
      try {
        for (const cid of contractorIds) {
          const cRes = await frappeRequest({
            url: '/api/method/frappe.client.get_value',
            params: { doctype: 'Contact', filters: { name: cid }, fieldname: 'full_name' },
          })
          if (cRes?.full_name) cMap[cid] = cRes.full_name
        }
      } catch {
        // Non-critical — rows will simply omit contractor name
      }
    }
    contractorNameMap.value = cMap
  } catch {
    data.value = null
  } finally {
    loading.value = false
  }
}

function formatDate(date: string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatCurrency(value: number | null): string {
  if (value == null) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

async function onTaskCreated() {
  showAddDialog.value = false
  await loadTasks()
}

onMounted(() => {
  loadRole()
  loadTasks()
})
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-h1 text-gray-900 dark:text-gray-100">
        {{ __('Maintenance') }}
      </h1>
      <Button
        v-if="isAdultOrAbove && !noProperty && !loading"
        variant="solid"
        @click="showAddDialog = true"
      >
        <template #prefix><Plus class="w-4 h-4" /></template>
        {{ __('Add task') }}
      </Button>
    </div>

    <!-- Filters -->
    <div v-if="data && !noProperty" class="mb-4 space-y-2">
      <div class="flex flex-wrap gap-2">
        <!-- Category filter -->
        <select
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          @change="(e) => { const v = (e.target as HTMLSelectElement).value; if (v) { filterCategory = toggleFilter(filterCategory, v) }; (e.target as HTMLSelectElement).value = '' }"
        >
          <option value="">{{ __('Category') }}</option>
          <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
        </select>

        <!-- Room filter -->
        <select
          v-if="roomOptions.length"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          @change="(e) => { const v = (e.target as HTMLSelectElement).value; if (v) { filterRoom = toggleFilter(filterRoom, v) }; (e.target as HTMLSelectElement).value = '' }"
        >
          <option value="">{{ __('Room') }}</option>
          <option v-for="r in roomOptions" :key="r.name" :value="r.name">{{ r.room_name }}</option>
        </select>

        <!-- Item filter -->
        <select
          v-if="itemOptions.length"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          @change="(e) => { const v = (e.target as HTMLSelectElement).value; if (v) { filterItem = toggleFilter(filterItem, v) }; (e.target as HTMLSelectElement).value = '' }"
        >
          <option value="">{{ __('Item') }}</option>
          <option v-for="i in itemOptions" :key="i.name" :value="i.name">{{ i.item_name }}</option>
        </select>

        <button
          v-if="hasActiveFilters"
          class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          @click="clearFilters"
        >
          {{ __('Clear all') }}
        </button>
      </div>

      <!-- Active filter chips -->
      <div v-if="hasActiveFilters" class="flex flex-wrap gap-1.5">
        <span
          v-for="c in filterCategory" :key="'cat-' + c"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700
                 text-xs text-gray-700 dark:text-gray-300"
        >
          {{ __(c) }}
          <button @click="removeFilter('category', c)" class="hover:text-gray-900 dark:hover:text-gray-100">
            <X class="w-3 h-3" />
          </button>
        </span>
        <span
          v-for="r in filterRoom" :key="'room-' + r"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700
                 text-xs text-gray-700 dark:text-gray-300"
        >
          {{ roomNameMap[r] || r }}
          <button @click="removeFilter('room', r)" class="hover:text-gray-900 dark:hover:text-gray-100">
            <X class="w-3 h-3" />
          </button>
        </span>
        <span
          v-for="i in filterItem" :key="'item-' + i"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700
                 text-xs text-gray-700 dark:text-gray-300"
        >
          {{ itemNameMap[i] || i }}
          <button @click="removeFilter('item', i)" class="hover:text-gray-900 dark:hover:text-gray-100">
            <X class="w-3 h-3" />
          </button>
        </span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- No property -->
    <div v-else-if="noProperty" class="text-center py-12">
      <Wrench class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No property yet') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('Set up your property first to manage maintenance tasks.') }}
      </p>
    </div>

    <!-- No data -->
    <div v-else-if="!data" class="text-center py-12">
      <Wrench class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No maintenance tasks') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('No maintenance tasks found.') }}
      </p>
    </div>

    <!-- Grouped sections -->
    <div v-else-if="filtered" class="space-y-6">
      <!-- Overdue -->
      <div v-if="filtered.overdue.length">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-red-600 dark:text-red-400 mb-2">
          {{ __('Overdue') }} ({{ filtered.overdue.length }})
        </h2>
        <div class="space-y-2">
          <router-link
            v-for="task in filtered.overdue"
            :key="task.name"
            :to="`/home/maintenance/${task.name}`"
            class="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/10 rounded-lg border
                   border-red-200 dark:border-red-900/30 hover:shadow-sm transition-shadow no-underline"
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <RefreshCw v-if="task.maintenance_type === 'Recurring'" class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ task.title }}</span>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {{ __(task.category) }}
                <template v-if="contextParts(task)"> · {{ contextParts(task) }}</template>
                <template v-if="task.scheduled_date"> · {{ formatDate(task.scheduled_date) }}</template>
                <template v-if="getContractorName(task)"> · {{ getContractorName(task) }}</template>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-3">
              <span v-if="!isChild && task.cost != null" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatCurrency(task.cost) }}
              </span>
              <span class="text-xs font-medium text-red-600 dark:text-red-400">
                {{ __('Overdue') }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Today -->
      <div v-if="filtered.today.length">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400 mb-2">
          {{ __('Today') }} ({{ filtered.today.length }})
        </h2>
        <div class="space-y-2">
          <router-link
            v-for="task in filtered.today"
            :key="task.name"
            :to="`/home/maintenance/${task.name}`"
            class="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border
                   border-blue-200 dark:border-blue-900/30 hover:shadow-sm transition-shadow no-underline"
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <RefreshCw v-if="task.maintenance_type === 'Recurring'" class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ task.title }}</span>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {{ __(task.category) }}
                <template v-if="contextParts(task)"> · {{ contextParts(task) }}</template>
                <template v-if="getContractorName(task)"> · {{ getContractorName(task) }}</template>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-3">
              <span v-if="!isChild && task.cost != null" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatCurrency(task.cost) }}
              </span>
              <span class="text-xs font-medium text-blue-600 dark:text-blue-400">
                {{ __('Today') }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Scheduled -->
      <div v-if="filtered.scheduled.length">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 mb-2">
          {{ __('Scheduled') }} ({{ filtered.scheduled.length }})
        </h2>
        <div class="space-y-2">
          <router-link
            v-for="task in filtered.scheduled"
            :key="task.name"
            :to="`/home/maintenance/${task.name}`"
            class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border
                   border-gray-200 dark:border-gray-700 hover:shadow-sm transition-shadow no-underline"
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <RefreshCw v-if="task.maintenance_type === 'Recurring'" class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ task.title }}</span>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {{ __(task.category) }}
                <template v-if="contextParts(task)"> · {{ contextParts(task) }}</template>
                <template v-if="task.scheduled_date"> · {{ formatDate(task.scheduled_date) }}</template>
                <template v-if="getContractorName(task)"> · {{ getContractorName(task) }}</template>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-3">
              <span v-if="!isChild && task.cost != null" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatCurrency(task.cost) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ __('Scheduled') }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- In Progress -->
      <div v-if="filtered.in_progress.length">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 mb-2">
          {{ __('In Progress') }} ({{ filtered.in_progress.length }})
        </h2>
        <div class="space-y-2">
          <router-link
            v-for="task in filtered.in_progress"
            :key="task.name"
            :to="`/home/maintenance/${task.name}`"
            class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border
                   border-gray-200 dark:border-gray-700 hover:shadow-sm transition-shadow no-underline"
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <RefreshCw v-if="task.maintenance_type === 'Recurring'" class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ task.title }}</span>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {{ __(task.category) }}
                <template v-if="contextParts(task)"> · {{ contextParts(task) }}</template>
                <template v-if="task.scheduled_date"> · {{ formatDate(task.scheduled_date) }}</template>
                <template v-if="getContractorName(task)"> · {{ getContractorName(task) }}</template>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-3">
              <span v-if="!isChild && task.cost != null" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatCurrency(task.cost) }}
              </span>
              <span class="text-xs text-amber-600 dark:text-amber-400">
                {{ __('In Progress') }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Completed (collapsed by default) -->
      <div v-if="filtered.completed.length">
        <button
          class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider
                 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 mb-2"
          @click="showCompleted = !showCompleted"
        >
          <ChevronRight class="w-3.5 h-3.5 transition-transform" :class="{ 'rotate-90': showCompleted }" />
          {{ __('Completed') }} ({{ filtered.completed.length }})
        </button>
        <div v-if="showCompleted" class="space-y-2">
          <router-link
            v-for="task in filtered.completed"
            :key="task.name"
            :to="`/home/maintenance/${task.name}`"
            class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border
                   border-gray-200 dark:border-gray-700 hover:shadow-sm transition-shadow no-underline opacity-70"
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <RefreshCw v-if="task.maintenance_type === 'Recurring'" class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <span class="text-sm text-gray-700 dark:text-gray-300 truncate">{{ task.title }}</span>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {{ __(task.category) }}
                <template v-if="contextParts(task)"> · {{ contextParts(task) }}</template>
                <template v-if="task.completed_date"> · {{ formatDate(task.completed_date) }}</template>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-3">
              <span v-if="!isChild && task.cost != null" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatCurrency(task.cost) }}
              </span>
              <span class="text-xs text-green-600 dark:text-green-400">
                {{ __('Completed') }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Cancelled (collapsed by default) -->
      <div v-if="filtered.cancelled.length">
        <button
          class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider
                 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 mb-2"
          @click="showCancelled = !showCancelled"
        >
          <ChevronRight class="w-3.5 h-3.5 transition-transform" :class="{ 'rotate-90': showCancelled }" />
          {{ __('Cancelled') }} ({{ filtered.cancelled.length }})
        </button>
        <div v-if="showCancelled" class="space-y-2">
          <router-link
            v-for="task in filtered.cancelled"
            :key="task.name"
            :to="`/home/maintenance/${task.name}`"
            class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border
                   border-gray-200 dark:border-gray-700 hover:shadow-sm transition-shadow no-underline opacity-50"
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <RefreshCw v-if="task.maintenance_type === 'Recurring'" class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <span class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ task.title }}</span>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {{ __(task.category) }}
                <template v-if="contextParts(task)"> · {{ contextParts(task) }}</template>
                <template v-if="task.scheduled_date"> · {{ formatDate(task.scheduled_date) }}</template>
              </div>
            </div>
            <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 ml-3">
              {{ __('Cancelled') }}
            </span>
          </router-link>
        </div>
      </div>

      <!-- All empty -->
      <div v-if="allEmpty" class="text-center py-12">
        <Wrench class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
        <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
          {{ hasActiveFilters ? __('No matching tasks') : __('No maintenance tasks') }}
        </h2>
        <p class="text-body text-gray-500 dark:text-gray-400">
          {{ hasActiveFilters ? __('Try adjusting your filters.') : __('No maintenance tasks found.') }}
        </p>
      </div>
    </div>

    <!-- Add task dialog -->
    <AddMaintenanceDialog
      v-if="showAddDialog"
      :property="propertyName"
      @close="showAddDialog = false"
      @created="onTaskCreated"
    />
  </div>
</template>
