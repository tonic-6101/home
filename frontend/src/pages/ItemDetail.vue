<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Item detail page — appliance, possession, or fixture (Feature 5).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  ArrowLeft, Pencil, MapPin, Refrigerator, Package, Home,
  Shield, Check,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useHouseholdRole } from '@/composables/useHouseholdRole'
import WarrantyCard, { type WarrantySummary } from '@/components/WarrantyCard.vue'
import RecallBanner from '@/components/RecallBanner.vue'
interface ItemDetail {
  name: string
  item_name: string
  item_type: 'Appliance' | 'Possession' | 'Fixture'
  category: string
  brand: string | null
  model: string | null
  serial_number: string | null
  status: string | null
  condition: string | null
  room: string | null
  room_name: string | null
  property: string
  purchase_date: string | null
  purchase_price: number | null
  estimated_value: number | null
  insured: boolean
  notes: string | null
  // Appliance + Fixture
  expected_lifespan_years: number | null
  install_date: string | null
  energy_rating: string | null
  recall_active: boolean
  recalls: { recall_id: string; title: string; severity: string; detail_url: string; dismissed: boolean }[]
  warranties: WarrantySummary[]
  // Fixture-specific
  installed_date: string | null
  material: string | null
}

const route = useRoute()
const router = useRouter()
const itemName = computed(() => route.params.name as string)
const { isAdultOrAbove, isChild, load: loadRole } = useHouseholdRole()

const item = ref<ItemDetail | null>(null)
const loading = ref(true)
const error = ref('')
const statusColors: Record<string, string> = {
  Working: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  'Needs Repair': 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  Broken: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  Disposed: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
}

const conditionColors: Record<string, string> = {
  New: 'text-green-600 dark:text-green-400',
  Good: 'text-blue-600 dark:text-blue-400',
  Fair: 'text-amber-600 dark:text-amber-400',
  Poor: 'text-red-600 dark:text-red-400',
}

function formatDate(date: string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatCurrency(value: number | null): string {
  if (value == null) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

async function loadItem() {
  loading.value = true
  error.value = ''
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.item.get_item',
      params: { name: itemName.value },
    })
    item.value = res
  } catch (e: any) {
    error.value = e.message || __('Failed to load item')
  } finally {
    loading.value = false
  }
}

function editItem() {
  router.push(`/home/items/${itemName.value}/edit`)
}

onMounted(() => {
  loadRole()
  loadItem()
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

    <template v-else-if="item">
      <!-- Back -->
      <button
        @click="router.push('/home/items')"
        class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
               hover:text-gray-700 dark:hover:text-gray-200 mb-4"
      >
        <ArrowLeft class="w-4 h-4" />
        {{ __('Items') }}
      </button>

      <!-- Header -->
      <div class="flex items-start justify-between mb-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <component
              :is="item.item_type === 'Appliance' ? Refrigerator : item.item_type === 'Fixture' ? Home : Package"
              class="w-5 h-5 text-gray-400"
            />
            <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
              {{ __(item.item_type) }}
            </span>
          </div>
          <h1 class="text-h1 text-gray-900 dark:text-gray-100">
            {{ item.item_name }}
          </h1>
          <div class="flex items-center gap-2 mt-1">
            <!-- Status for appliances -->
            <template v-if="item.item_type === 'Appliance' && item.status">
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :class="statusColors[item.status] || 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'"
              >
                {{ __(item.status) }}
              </span>
            </template>
            <!-- Condition for possessions -->
            <template v-if="item.item_type === 'Possession' && item.condition">
              <span :class="conditionColors[item.condition] || 'text-gray-600 dark:text-gray-400'" class="text-sm font-medium">
                {{ __(item.condition) }}
              </span>
            </template>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ __(item.category) }}</span>
          </div>
        </div>

        <button
          v-if="isAdultOrAbove"
          @click="editItem"
          class="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300
                 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <Pencil class="w-3.5 h-3.5" />
          {{ __('Edit') }}
        </button>
      </div>

      <!-- Recall warning + check button (Feature 57) -->
      <RecallBanner
        v-if="item.recalls?.length || item.item_type === 'Appliance'"
        :item-name="item.name"
        :item-type="item.item_type"
        :recalls="item.recalls || []"
        :is-adult-or-above="isAdultOrAbove"
        @reload="loadItem"
      />

      <!-- Details card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4 space-y-3">
        <!-- Location -->
        <div v-if="item.room_name" class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <MapPin class="w-4 h-4 text-gray-400" />
          <span>{{ item.room_name }}</span>
        </div>

        <!-- Brand / Model -->
        <div v-if="item.brand || item.model" class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <Refrigerator class="w-4 h-4 text-gray-400" />
          <span>
            <template v-if="item.brand">{{ item.brand }}</template>
            <template v-if="item.brand && item.model"> — </template>
            <template v-if="item.model">{{ item.model }}</template>
          </span>
        </div>

        <!-- Serial number -->
        <div v-if="item.serial_number" class="text-sm text-gray-700 dark:text-gray-300">
          <span class="text-gray-500 dark:text-gray-400">{{ __('Serial') }}:</span> {{ item.serial_number }}
        </div>

        <!-- Purchase info (Adult+ only) -->
        <template v-if="!isChild">
          <div v-if="item.purchase_date" class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Purchased') }}:</span> {{ formatDate(item.purchase_date) }}
            <template v-if="item.purchase_price"> — {{ formatCurrency(item.purchase_price) }}</template>
          </div>
        </template>

        <!-- Appliance-specific fields -->
        <template v-if="item.item_type === 'Appliance'">
          <div v-if="item.install_date" class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Installed') }}:</span> {{ formatDate(item.install_date) }}
          </div>
          <div v-if="item.expected_lifespan_years" class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Expected lifespan') }}:</span>
            {{ item.expected_lifespan_years }} {{ __('years') }}
          </div>
          <div v-if="item.energy_rating" class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Energy rating') }}:</span> {{ item.energy_rating }}
          </div>
        </template>

        <!-- Fixture-specific fields -->
        <template v-if="item.item_type === 'Fixture'">
          <div v-if="item.installed_date" class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Installed') }}:</span> {{ formatDate(item.installed_date) }}
          </div>
          <div v-if="item.material" class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Material') }}:</span> {{ item.material }}
          </div>
          <div v-if="item.expected_lifespan_years" class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Expected lifespan') }}:</span>
            {{ item.expected_lifespan_years }} {{ __('years') }}
          </div>
        </template>

        <!-- Possession-specific: condition -->
        <div v-if="item.item_type === 'Possession' && item.condition" class="text-sm text-gray-700 dark:text-gray-300">
          <span class="text-gray-500 dark:text-gray-400">{{ __('Condition') }}:</span>
          <span :class="conditionColors[item.condition]">{{ __(item.condition) }}</span>
        </div>
      </div>

      <!-- Insurance section (all types, Adult+ only) -->
      <div
        v-if="!isChild"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4"
      >
        <h2 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-3">{{ __('Insurance') }}</h2>
        <div class="space-y-3">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            <span class="text-gray-500 dark:text-gray-400">{{ __('Estimated value') }}:</span>
            {{ item.estimated_value ? formatCurrency(item.estimated_value) : '—' }}
          </div>
          <div class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <Shield class="w-4 h-4 text-gray-400" />
            <span v-if="item.insured" class="flex items-center gap-1">
              <Check class="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
              {{ __('Specifically insured') }}
            </span>
            <span v-else class="text-gray-500 dark:text-gray-400">{{ __('Not specifically insured') }}</span>
          </div>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-2">
            {{ __('\"Specifically insured\" means this item is individually listed on your contents or buildings policy (a scheduled item). Most contents policies cover all items up to a limit without needing to list them individually.') }}
          </p>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="item.notes" class="mb-4">
        <h2 class="text-h4 text-gray-800 dark:text-gray-200 mb-2">{{ __('Notes') }}</h2>
        <div
          class="text-sm text-gray-600 dark:text-gray-400 prose prose-sm dark:prose-invert max-w-none"
          v-html="item.notes"
        />
      </div>

      <!-- Warranties (appliances + fixtures) -->
      <div v-if="(item.item_type === 'Appliance' || item.item_type === 'Fixture') && item.warranties?.length" class="mb-4">
        <h2 class="text-h4 text-gray-800 dark:text-gray-200 mb-3">{{ __('Warranties') }}</h2>
        <div class="space-y-3">
          <WarrantyCard
            v-for="w in item.warranties"
            :key="w.name"
            :warranty="w"
          />
        </div>
      </div>

      <!-- Tasks (via Orga) -->
      <div v-if="item.item_type === 'Appliance' || item.item_type === 'Fixture'" class="mb-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-h4 text-gray-800 dark:text-gray-200">{{ __('Tasks') }}</h2>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ __('Manage tasks for this item in') }}
          <a :href="`/orga/my-tasks?home_item=${item.name}`" class="text-accent-600 dark:text-accent-400 hover:underline">Orga</a>.
        </p>
      </div>
    </template>
  </div>
</template>
