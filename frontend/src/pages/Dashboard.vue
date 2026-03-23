<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  My Home — single property view with inline setup (Features 2, 3).
-->
<script setup lang="ts">
import { ref, computed, onMounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest, useFileUpload } from 'frappe-ui'
import {
  Home, Building2, DoorOpen, Store, HelpCircle,
  Wrench, HardHat, Shield, MoreVertical,
  Pencil, Wallet, Lightbulb, RotateCcw,
  Zap, FileText, BookOpen, Camera, PiggyBank, Truck, Mail,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useHouseholdRole } from '@/composables/useHouseholdRole'
import { useProperty } from '@/composables/useProperty'
import HouseholdMemberAvatar from '@/components/HouseholdMemberAvatar.vue'
import RoomCardGrid from '@/components/RoomCardGrid.vue'
import HealthScoreWidget from '@/components/HealthScoreWidget.vue'
import FrameSharePanel from '@/components/FrameSharePanel.vue'
import ICalSubscribePanel from '@/components/ICalSubscribePanel.vue'
import PhotoSection from '@/components/PhotoSection.vue'
import AddMaintenanceDialog from '@/components/AddMaintenanceDialog.vue'

const router = useRouter()
const { propertyName: cachedPropertyName, load: loadPropertyName, reset: resetPropertyCache } = useProperty()

const property = ref<any>(null)
const loading = ref(true)
const error = ref('')
const menuOpen = ref(false)

const showMaintenanceDialog = ref(false)

// Setup form state
const showSetup = ref(false)
const setupName = ref('')
const setupType = ref('House')
const setupOwnership = ref('Owner-occupied')
const setupSaving = ref(false)
const setupError = ref('')

const propertyTypes = ['House', 'Apartment', 'Studio', 'Commercial', 'Other']
const ownershipStatuses = ['Owner-occupied', 'Rented', 'Renting Out', 'Vacant']

const { isAdultOrAbove, load: loadRole } = useHouseholdRole()
const coverUploader = useFileUpload()

const currentUser = (window as any).frappe?.session?.user || ''
const isOwner = computed(() =>
  property.value?.members?.some(
    (m: any) => m.user === currentUser && m.role === 'Owner'
  )
)

const typeIcon = computed<Component>(() => {
  const map: Record<string, Component> = {
    House: Home,
    Apartment: Building2,
    Studio: DoorOpen,
    Commercial: Store,
  }
  return map[property.value?.property_type] || HelpCircle
})

const gradientClass = computed(() => {
  const map: Record<string, string> = {
    House: 'from-amber-400 to-amber-600',
    Apartment: 'from-blue-400 to-blue-600',
    Studio: 'from-purple-400 to-purple-600',
    Commercial: 'from-gray-400 to-gray-600',
  }
  return map[property.value?.property_type] || 'from-gray-400 to-gray-600'
})

async function loadProperty() {
  loading.value = true
  error.value = ''
  try {
    const name = await loadPropertyName()
    if (!name) {
      showSetup.value = true
      property.value = null
      return
    }
    const res = await frappeRequest({
      url: '/api/method/home.api.property.get_property',
      params: { name },
    })
    property.value = res
    showSetup.value = false
  } catch (e: any) {
    error.value = e.message || __('Failed to load property')
  } finally {
    loading.value = false
  }
}

async function createProperty() {
  if (!setupName.value.trim()) return
  setupSaving.value = true
  setupError.value = ''
  try {
    const created = await frappeRequest({
      url: '/api/method/home.api.property.create_property',
      params: {
        property_name: setupName.value.trim(),
        property_type: setupType.value,
        ownership_status: setupOwnership.value,
      },
    })
    // Use the returned property name directly instead of re-querying
    resetPropertyCache()
    if (created?.name) {
      const res = await frappeRequest({
        url: '/api/method/home.api.property.get_property',
        params: { name: created.name },
      })
      property.value = res
      showSetup.value = false
      loading.value = false
    } else {
      await loadProperty()
    }
  } catch (e: any) {
    setupError.value = e.message || __('Failed to create property')
  } finally {
    setupSaving.value = false
  }
}

async function uploadCover(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (file.size > 10 * 1024 * 1024) {
    alert(__('Image must be smaller than 10 MB'))
    input.value = ''
    return
  }

  try {
    const uploadResult = await coverUploader.upload(file, {
      doctype: 'Home Property',
      docname: cachedPropertyName.value,
      private: false,
    })

    const fileUrl = uploadResult?.file_url
    if (fileUrl) {
      await frappeRequest({
        url: '/api/method/home.api.property.update_property',
        params: { name: cachedPropertyName.value, cover_image: fileUrl },
      })
      await loadProperty()
    }
  } catch (e: any) {
    alert(e.message || __('Failed to upload cover'))
  } finally {
    input.value = ''
  }
}

function formatAddress(): string {
  const p = property.value
  const parts = [p.address_line1, p.address_line2, p.city, p.postal_code, p.country].filter(Boolean)
  return parts.join(', ')
}

onMounted(() => {
  loadRole()
  loadProperty()
})
</script>

<template>
  <div class="max-w-5xl mx-auto">
    <!-- Loading -->
    <div v-if="loading" class="p-6 text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- Error -->
    <div v-else-if="error" class="p-6 text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <!-- Setup form — no property yet -->
    <div v-else-if="showSetup" data-tour="dashboard" class="p-6">
      <div class="max-w-md mx-auto text-center py-16">
        <div class="text-6xl mb-4">🏠</div>
        <h1 class="text-h1 text-gray-900 dark:text-gray-100 mb-2">
          {{ __('Set up your property') }}
        </h1>
        <p class="text-body text-gray-500 dark:text-gray-400 mb-8">
          {{ __('Tell us about your home to get started.') }}
        </p>

        <div class="space-y-4 text-left">
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Property Name') }}
            </label>
            <input
              v-model="setupName"
              type="text"
              :placeholder="__('e.g. Our House')"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              @keyup.enter="createProperty"
            />
          </div>

          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Property Type') }}
            </label>
            <select
              v-model="setupType"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option v-for="t in propertyTypes" :key="t" :value="t">{{ __(t) }}</option>
            </select>
          </div>

          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Ownership Status') }}
            </label>
            <select
              v-model="setupOwnership"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option v-for="s in ownershipStatuses" :key="s" :value="s">{{ __(s) }}</option>
            </select>
          </div>
        </div>

        <p v-if="setupError" class="mt-3 text-sm text-red-600 dark:text-red-400">{{ setupError }}</p>

        <div class="mt-6">
          <Button variant="solid" :loading="setupSaving" @click="createProperty" data-tour="add-property">
            {{ __('Create Property') }}
          </Button>
        </div>
      </div>
    </div>

    <!-- Property view -->
    <template v-else-if="property">
      <!-- Hero -->
      <div class="relative h-48 md:h-64 overflow-hidden group">
        <img
          v-if="property.cover_image"
          :src="property.cover_image"
          :alt="property.property_name"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          :class="['w-full h-full bg-gradient-to-br flex items-center justify-center', gradientClass]"
        >
          <component :is="typeIcon" class="w-16 h-16 text-white/40" />
        </div>

        <!-- Cover upload overlay (Owner only) -->
        <label
          v-if="isOwner"
          class="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/30
                 cursor-pointer transition-colors"
        >
          <span class="text-white opacity-0 group-hover:opacity-100 transition-opacity text-sm font-medium">
            {{ __('Change cover') }}
          </span>
          <input type="file" accept="image/*" class="hidden" @change="uploadCover" />
        </label>

        <!-- Name overlay -->
        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4 md:p-6">
          <h1 class="text-xl md:text-2xl font-bold text-white">{{ property.property_name }}</h1>
          <p v-if="formatAddress()" class="text-sm text-white/80 mt-1">
            {{ formatAddress() }}
          </p>
        </div>

        <!-- Kebab menu -->
        <div v-if="isOwner" class="absolute top-3 right-3" data-dropdown>
          <button
            @click="menuOpen = !menuOpen"
            class="w-8 h-8 flex items-center justify-center rounded-full bg-black/30 text-white
                   hover:bg-black/50 transition-colors"
          >
            <MoreVertical class="w-4 h-4" />
          </button>
          <div
            v-if="menuOpen"
            class="absolute right-0 mt-1 w-48 rounded-lg shadow-lg border
                   border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 py-1"
          >
            <button
              class="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300
                     hover:bg-gray-100 dark:hover:bg-gray-700"
              @click="menuOpen = false"
            >
              <Pencil class="w-4 h-4" />
              {{ __('Edit details') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Stats bar -->
      <div class="flex items-center gap-6 px-6 py-3 border-b border-gray-200 dark:border-gray-700
                  bg-white dark:bg-gray-800">
        <div class="flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-400">
          <Wrench class="w-4 h-4" />
          <span>{{ property.appliance_count }} {{ __('appliances') }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-400">
          <HardHat class="w-4 h-4" />
          <span>{{ property.open_maintenance_count }} {{ __('open tasks') }}</span>
        </div>
        <button
          v-if="isAdultOrAbove"
          @click="showMaintenanceDialog = true"
          class="flex items-center gap-1.5 text-sm text-home-600 dark:text-home-400
                 hover:text-home-700 dark:hover:text-home-300 transition-colors"
        >
          <HardHat class="w-4 h-4" />
          <span>{{ __('Log maintenance') }}</span>
        </button>
        <div
          v-if="property.upcoming_warranty_expiry"
          class="flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-400"
        >
          <Shield class="w-4 h-4" />
          <span>{{ __('Warranty expires') }} {{ property.upcoming_warranty_expiry }}</span>
        </div>
        <router-link
          v-if="isAdultOrAbove"
          to="/home/budget"
          class="flex items-center gap-1.5 text-sm text-home-600 dark:text-home-400
                 hover:text-home-700 dark:hover:text-home-300 no-underline ml-auto"
        >
          <Wallet class="w-4 h-4" />
          <span>{{ __('Budget') }}</span>
        </router-link>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-8">
        <!-- Health Score (Feature 36) -->
        <section>
          <HealthScoreWidget :property="property.name" />
        </section>

        <!-- Overview section -->
        <section>
          <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-3">{{ __('Overview') }}</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="text-gray-500 dark:text-gray-400 block">{{ __('Type') }}</span>
              <span class="text-gray-900 dark:text-gray-100">{{ __(property.property_type) }}</span>
            </div>
            <div>
              <span class="text-gray-500 dark:text-gray-400 block">{{ __('Status') }}</span>
              <span class="text-gray-900 dark:text-gray-100">{{ __(property.ownership_status) }}</span>
            </div>
            <div v-if="property.area_sqm">
              <span class="text-gray-500 dark:text-gray-400 block">{{ __('Area') }}</span>
              <span class="text-gray-900 dark:text-gray-100">{{ property.area_sqm }} m²</span>
            </div>
            <div v-if="property.move_in_date">
              <span class="text-gray-500 dark:text-gray-400 block">{{ __('Move-in') }}</span>
              <span class="text-gray-900 dark:text-gray-100">{{ property.move_in_date }}</span>
            </div>
          </div>
        </section>

        <!-- Rooms section (Feature 3) -->
        <section>
          <RoomCardGrid
            :property="property.name"
            :property-type="property.property_type"
            :is-owner="isOwner"
            :is-archived="false"
          />
        </section>

        <!-- Quick links — Financial (Owner/Adult only) -->
        <section v-if="isAdultOrAbove">
          <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-3">{{ __('Finances & Documents') }}</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <router-link
              to="/home/budget"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <Wallet class="w-4 h-4 text-home-500 flex-shrink-0" />
              {{ __('Budget') }}
            </router-link>
            <router-link
              to="/home/utilities"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <Zap class="w-4 h-4 text-amber-500 flex-shrink-0" />
              {{ __('Utility Bills') }}
            </router-link>
            <router-link
              to="/home/insurance"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <Shield class="w-4 h-4 text-green-500 flex-shrink-0" />
              {{ __('Insurance') }}
            </router-link>
            <router-link
              to="/home/cost-report"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <FileText class="w-4 h-4 text-blue-500 flex-shrink-0" />
              {{ __('Cost Report') }}
            </router-link>
            <router-link
              v-if="property.ownership_status === 'Owner-occupied'"
              to="/home/equity"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <PiggyBank class="w-4 h-4 text-purple-500 flex-shrink-0" />
              {{ __('Home Equity') }}
            </router-link>
            <router-link
              to="/home/returns"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <RotateCcw class="w-4 h-4 text-red-500 flex-shrink-0" />
              {{ __('Returns') }}
            </router-link>
            <router-link
              to="/home/documents"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <BookOpen class="w-4 h-4 text-gray-500 flex-shrink-0" />
              {{ __('Documents') }}
            </router-link>
            <router-link
              to="/home/letters"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <Mail class="w-4 h-4 text-indigo-500 flex-shrink-0" />
              {{ __('Letters') }}
            </router-link>
          </div>
        </section>

        <!-- Photos (Feature 59) -->
        <section>
          <PhotoSection
            :property="property.name"
            :can-edit="isAdultOrAbove"
            :max-thumbnails="8"
          />
        </section>

        <!-- Quick links — All roles -->
        <section>
          <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-3">{{ __('Home Life') }}</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <router-link
              to="/home/wishlist"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <Lightbulb class="w-4 h-4 text-amber-500 flex-shrink-0" />
              {{ __('Wishlist') }}
            </router-link>
            <router-link
              to="/home/passport"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <BookOpen class="w-4 h-4 text-teal-500 flex-shrink-0" />
              {{ __('Passport') }}
            </router-link>
            <router-link
              to="/home/moving"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white dark:bg-gray-800
                     border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300
                     hover:border-home-300 dark:hover:border-home-600 transition-colors no-underline"
            >
              <Truck class="w-4 h-4 text-orange-500 flex-shrink-0" />
              {{ __('Moving') }}
            </router-link>
          </div>
        </section>

        <!-- Sharing & Calendar (Features 55, 56) -->
        <section class="space-y-4">
          <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-1">{{ __('Sharing') }}</h2>

          <!-- Frame share panel — Owner only, hidden when Frame absent -->
          <FrameSharePanel
            :property="property.name"
            :frame-token="property.frame_token"
            :is-owner="isOwner"
            @token-regenerated="loadProperty"
          />

          <!-- iCal subscribe — all members -->
          <ICalSubscribePanel
            :property="property.name"
            :property-name="property.property_name"
            :ical-token="property.ical_token"
            :is-owner="isOwner"
            @token-regenerated="loadProperty"
          />
        </section>

        <!-- Members -->
        <section>
          <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-3">{{ __('Members') }}</h2>
          <div class="flex flex-wrap gap-3">
            <div
              v-for="member in property.members"
              :key="member.user || member.display_name"
              class="flex items-center gap-2"
            >
              <HouseholdMemberAvatar
                :display-name="member.display_name"
                :avatar="member.avatar"
                size="sm"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ member.display_name }}</span>
            </div>
          </div>
          <router-link
            to="/home/household/settings"
            class="text-sm text-home-600 dark:text-home-400 hover:underline mt-2 inline-block"
          >
            {{ __('Manage in Household Settings') }}
          </router-link>
        </section>
      </div>

      <!-- Add Maintenance Dialog -->
      <AddMaintenanceDialog
        v-if="showMaintenanceDialog"
        :property="property.name"
        @close="showMaintenanceDialog = false"
        @created="showMaintenanceDialog = false; loadProperty()"
      />
    </template>
  </div>
</template>
