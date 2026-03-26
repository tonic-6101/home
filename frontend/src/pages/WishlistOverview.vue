<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Improvement wishlist page (Feature 45) — grouped by priority with total estimated cost.
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  ArrowLeft, Plus, Circle, ChevronDown, ChevronRight,
  ExternalLink, Wrench, FolderKanban, Eye, EyeOff,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useHouseholdRole } from '@/composables/useHouseholdRole'
import { useProperty } from '@/composables/useProperty'
import AddWishDialog from '@/components/AddWishDialog.vue'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()
const { isAdultOrAbove, isChild, load: loadRole } = useHouseholdRole()

const data = ref<any>(null)
const loading = ref(true)
const error = ref('')
const showDone = ref(false)
const showAbandoned = ref(false)
const showAddDialog = ref(false)
const editingWish = ref<any>(null)

// Detail expand
const expandedWish = ref<string | null>(null)
const convertingMaint = ref(false)
const creatingOrga = ref(false)
const updatingStatus = ref(false)

const priorityIcons: Record<string, { color: string; label: string }> = {
  Urgent: { color: 'text-red-500', label: 'Urgent' },
  Important: { color: 'text-amber-500', label: 'Important' },
  'Nice to have': { color: 'text-gray-400', label: 'Nice to have' },
}

const statusColors: Record<string, string> = {
  Wishlist: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  Planned: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  'In Progress': 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  Done: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  Abandoned: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-500',
}

function formatCurrency(value: number | null): string {
  if (value == null) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

async function loadWishlist() {
  loading.value = true
  error.value = ''
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.wishlist.get_wishlist',
      params: { property: propName },
    })
    data.value = res
  } catch (e: any) {
    error.value = e.message || __('Failed to load wishlist')
  } finally {
    loading.value = false
  }
}

function toggleExpand(name: string) {
  expandedWish.value = expandedWish.value === name ? null : name
}

function onSaved() {
  showAddDialog.value = false
  editingWish.value = null
  loadWishlist()
}

function editWish(wish: any) {
  editingWish.value = wish
  showAddDialog.value = true
}

async function updateStatus(wishName: string, status: string) {
  updatingStatus.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.wishlist.update_wish_status',
      params: { name: wishName, status },
    })
    await loadWishlist()
    expandedWish.value = null
  } catch (e: any) {
    alert(e.message || __('Failed to update status'))
  } finally {
    updatingStatus.value = false
  }
}

async function convertToTask(wishName: string) {
  convertingMaint.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.wishlist.convert_to_task',
      params: { wish_name: wishName },
    })
    if (!res?.already_exists) {
      await loadWishlist()
    }
    router.push(`/orga/my-tasks`)
  } catch (e: any) {
    alert(e.message || __('Failed to convert'))
  } finally {
    convertingMaint.value = false
  }
}

async function createOrgaProject(wishName: string) {
  creatingOrga.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.wishlist.create_orga_from_wish',
      params: { wish_name: wishName },
    })
    await loadWishlist()
    if (!res?.already_exists) {
      expandedWish.value = null
    }
  } catch (e: any) {
    alert(e.message || __('Failed to create project'))
  } finally {
    creatingOrga.value = false
  }
}

// Find a wish by name across all groups
function findWish(name: string): any {
  if (!data.value) return null
  for (const wishes of Object.values(data.value.by_priority) as any[][]) {
    const found = wishes.find((w: any) => w.name === name)
    if (found) return found
  }
  return data.value.done?.find((w: any) => w.name === name)
    || data.value.abandoned?.find((w: any) => w.name === name)
    || null
}

onMounted(() => {
  loadRole()
  loadWishlist()
})
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <template v-else-if="data">
      <!-- Back -->
      <button
        @click="router.push('/home')"
        class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
               hover:text-gray-700 dark:hover:text-gray-200 mb-4"
      >
        <ArrowLeft class="w-4 h-4" />
        {{ __('My Home') }}
      </button>

      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div>
          <h1 class="text-h1 text-gray-900 dark:text-gray-100">
            {{ __('Improvement Wishlist') }}
          </h1>

          <!-- Total estimated cost (Adult+ only) -->
          <div v-if="isAdultOrAbove && data.total_active > 0" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            <span class="font-medium text-gray-700 dark:text-gray-300">
              {{ __('Total estimated') }}: {{ formatCurrency(data.total_estimated) }}
            </span>
            <span v-if="data.items_without_estimate > 0" class="ml-2">
              ({{ data.items_without_estimate }} {{ __('without estimate') }})
            </span>
          </div>
        </div>

        <Button
          v-if="isAdultOrAbove"
          variant="solid"
          @click="editingWish = null; showAddDialog = true"
        >
          <template #prefix><Plus class="w-4 h-4" /></template>
          {{ __('Add') }}
        </Button>
      </div>

      <!-- Empty state -->
      <div
        v-if="data.total_active === 0 && data.done.length === 0 && data.abandoned.length === 0"
        class="text-center py-12 text-gray-500 dark:text-gray-400"
      >
        <p class="text-lg mb-2">{{ __('No improvement wishes yet') }}</p>
        <p v-if="isAdultOrAbove" class="text-sm">
          {{ __('Add ideas for home improvements you\'d like to make.') }}
        </p>
      </div>

      <!-- Priority groups -->
      <div v-for="(wishes, priority) in data.by_priority" :key="priority" class="mb-6">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 mb-2">
          {{ __(priority as string) }}
        </h2>

        <div class="space-y-2">
          <div
            v-for="wish in wishes"
            :key="wish.name"
            class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            <!-- Wish row -->
            <button
              class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
              @click="toggleExpand(wish.name)"
            >
              <Circle
                class="w-3 h-3 flex-shrink-0 fill-current"
                :class="priorityIcons[priority as string]?.color || 'text-gray-400'"
              />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {{ wish.title }}
                  </span>
                  <span
                    class="text-xs px-1.5 py-0.5 rounded-full flex-shrink-0"
                    :class="statusColors[wish.status] || statusColors.Wishlist"
                  >
                    {{ __(wish.status) }}
                  </span>
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {{ __(wish.category) }}
                  <template v-if="wish.room"> · {{ wish.room }}</template>
                  <template v-if="!isChild && wish.estimated_cost">
                    · ~{{ formatCurrency(wish.estimated_cost) }}
                  </template>
                </div>
              </div>
              <ChevronDown
                class="w-4 h-4 text-gray-400 transition-transform flex-shrink-0"
                :class="{ 'rotate-180': expandedWish === wish.name }"
              />
            </button>

            <!-- Expanded detail -->
            <div
              v-if="expandedWish === wish.name"
              class="border-t border-gray-200 dark:border-gray-700 px-4 py-3 space-y-3"
            >
              <!-- Cost (Adult+) -->
              <div v-if="isAdultOrAbove && wish.estimated_cost" class="text-sm text-gray-700 dark:text-gray-300">
                {{ __('Estimated cost') }}: {{ formatCurrency(wish.estimated_cost) }}
              </div>

              <!-- Notes -->
              <div v-if="wish.notes" class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line">
                {{ wish.notes }}
              </div>

              <!-- Linked records -->
              <div v-if="wish.linked_task" class="flex items-center gap-2 text-sm">
                <Wrench class="w-4 h-4 text-gray-400" />
                <a
                  href="/orga/my-tasks"
                  class="text-accent-600 dark:text-accent-400 hover:underline"
                >
                  {{ __('View task') }}
                </a>
              </div>
              <div v-if="wish.linked_orga_project" class="flex items-center gap-2 text-sm">
                <FolderKanban class="w-4 h-4 text-gray-400" />
                <a
                  :href="`/app/orga-project/${wish.linked_orga_project}`"
                  class="text-accent-600 dark:text-accent-400 hover:underline"
                >
                  {{ __('View Orga Project') }}
                </a>
              </div>

              <!-- Actions (Adult+ only) -->
              <div v-if="isAdultOrAbove" class="flex flex-wrap gap-2 pt-1">
                <Button
                  v-if="wish.status !== 'Done' && wish.status !== 'Abandoned'"
                  variant="outline"
                  size="sm"
                  @click="editWish(wish)"
                >
                  {{ __('Edit') }}
                </Button>
                <Button
                  v-if="!wish.linked_task && wish.status !== 'Done' && wish.status !== 'Abandoned'"
                  variant="outline"
                  size="sm"
                  :loading="convertingMaint"
                  @click="convertToTask(wish.name)"
                >
                  <template #prefix><Wrench class="w-3.5 h-3.5" /></template>
                  {{ __('Convert to task') }}
                </Button>
                <Button
                  v-if="!wish.linked_orga_project && wish.status !== 'Done' && wish.status !== 'Abandoned' && data.has_orga"
                  variant="outline"
                  size="sm"
                  :loading="creatingOrga"
                  @click="createOrgaProject(wish.name)"
                >
                  <template #prefix><FolderKanban class="w-3.5 h-3.5" /></template>
                  {{ __('Create Orga project') }}
                </Button>
                <Button
                  v-if="wish.status !== 'Done' && wish.status !== 'Abandoned'"
                  variant="outline"
                  size="sm"
                  :loading="updatingStatus"
                  @click="updateStatus(wish.name, 'Done')"
                >
                  {{ __('Mark as Done') }}
                </Button>
                <Button
                  v-if="wish.status !== 'Done' && wish.status !== 'Abandoned'"
                  variant="ghost"
                  size="sm"
                  :loading="updatingStatus"
                  @click="updateStatus(wish.name, 'Abandoned')"
                >
                  {{ __('Abandon') }}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Done section -->
      <div v-if="data.done.length > 0" class="mb-6">
        <button
          class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider
                 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 mb-2"
          @click="showDone = !showDone"
        >
          <ChevronRight class="w-3.5 h-3.5 transition-transform" :class="{ 'rotate-90': showDone }" />
          {{ __('Done') }} ({{ data.done.length }})
        </button>

        <div v-if="showDone" class="space-y-2">
          <div
            v-for="wish in data.done"
            :key="wish.name"
            class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
                   px-4 py-3 opacity-70"
          >
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-700 dark:text-gray-300 line-through">{{ wish.title }}</span>
              <span class="text-xs px-1.5 py-0.5 rounded-full" :class="statusColors.Done">
                {{ __('Done') }}
              </span>
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {{ __(wish.category) }}
              <template v-if="!isChild && wish.estimated_cost">
                · ~{{ formatCurrency(wish.estimated_cost) }}
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Abandoned section -->
      <div v-if="data.abandoned.length > 0" class="mb-6">
        <button
          class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider
                 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 mb-2"
          @click="showAbandoned = !showAbandoned"
        >
          <component :is="showAbandoned ? Eye : EyeOff" class="w-3.5 h-3.5" />
          {{ __('Show abandoned') }} ({{ data.abandoned.length }})
        </button>

        <div v-if="showAbandoned" class="space-y-2">
          <div
            v-for="wish in data.abandoned"
            :key="wish.name"
            class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
                   px-4 py-3 opacity-50"
          >
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 dark:text-gray-400 line-through">{{ wish.title }}</span>
              <span class="text-xs px-1.5 py-0.5 rounded-full" :class="statusColors.Abandoned">
                {{ __('Abandoned') }}
              </span>
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {{ __(wish.category) }}
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Add/Edit dialog -->
    <AddWishDialog
      v-if="showAddDialog"
      :property="propertyName"
      :wish="editingWish"
      @close="showAddDialog = false; editingWish = null"
      @saved="onSaved"
    />
  </div>
</template>
