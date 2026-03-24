<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Home Settings panel — alert thresholds, lifespans, preferences (Feature 38).
  Owner-only. Embedded in HouseholdSettings page.
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'
import { useOnboardingTour } from '@/composables/useOnboardingTour'

const props = defineProps<{ household: string; section?: string }>()

// When section prop is provided, show only that section. Otherwise show all.
const showAlerts = computed(() => !props.section || props.section === 'alerts')
const showLifespans = computed(() => !props.section || props.section === 'lifespans')
const showPreferences = computed(() => !props.section || props.section === 'preferences')

interface CategoryLifespan {
  category: string
  lifespan_years: number | null
  avg_replacement_cost: number | null
}

interface HomeSettings {
  name: string
  warranty_alert_days_first: number
  warranty_alert_days_second: number
  legal_warranty_months: number
  burden_of_proof_months: number
  burden_of_proof_alert_days: number
  maintenance_reminder_days: number
  refund_alert_days: number
  tenancy_expiry_alert_days: number
  default_currency: string
  financial_visibility: string
  category_lifespans: CategoryLifespan[]
}

const settings = ref<HomeSettings | null>(null)
const loadingSettings = ref(true)
const settingsError = ref('')
const saving = ref(false)
const saveSuccess = ref(false)

const { restartTour } = useOnboardingTour()
const restartingTour = ref(false)

const visibilityOptions = [
  { value: 'Owner and Adult', label: __('Owner and Adult') },
  { value: 'Owner only', label: __('Owner only') },
]

async function loadSettings() {
  loadingSettings.value = true
  settingsError.value = ''
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.settings.get_settings',
    })
    settings.value = res
  } catch (e: any) {
    settingsError.value = e.message || __('Failed to load settings')
  } finally {
    loadingSettings.value = false
  }
}

async function saveSettings() {
  if (!settings.value) return
  saving.value = true
  saveSuccess.value = false
  settingsError.value = ''
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.settings.save_settings',
      params: {
        data: JSON.stringify({
          name: settings.value.name,
          warranty_alert_days_first: settings.value.warranty_alert_days_first,
          warranty_alert_days_second: settings.value.warranty_alert_days_second,
          legal_warranty_months: settings.value.legal_warranty_months,
          burden_of_proof_months: settings.value.burden_of_proof_months,
          burden_of_proof_alert_days: settings.value.burden_of_proof_alert_days,
          maintenance_reminder_days: settings.value.maintenance_reminder_days,
          refund_alert_days: settings.value.refund_alert_days,
          tenancy_expiry_alert_days: settings.value.tenancy_expiry_alert_days,
          default_currency: settings.value.default_currency,
          financial_visibility: settings.value.financial_visibility,
          category_lifespans: settings.value.category_lifespans,
        }),
      },
    })
    settings.value = res
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (e: any) {
    settingsError.value = e.message || __('Failed to save settings')
  } finally {
    saving.value = false
  }
}

async function handleRestartTour() {
  restartingTour.value = true
  await restartTour()
  restartingTour.value = false
}

onMounted(loadSettings)
</script>

<template>
  <!-- Loading -->
  <div v-if="loadingSettings" class="text-gray-500 dark:text-gray-400 text-sm">
    {{ __('Loading settings…') }}
  </div>

  <!-- Error -->
  <div v-else-if="settingsError && !settings" class="text-red-600 dark:text-red-400 text-sm">
    {{ settingsError }}
  </div>

  <template v-else-if="settings">
    <!-- Alerts Section -->
    <section v-if="showAlerts" class="mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-4">{{ __('Alerts') }}</h2>

      <!-- Warranty expiry -->
      <div class="mb-4">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {{ __('Warranty expiry alerts') }}
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('First alert') }}
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="settings.warranty_alert_days_first"
                type="number"
                min="1"
                max="365"
                class="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ __('days before') }}</span>
            </div>
          </div>
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Second alert') }}
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="settings.warranty_alert_days_second"
                type="number"
                min="1"
                max="365"
                class="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ __('days before') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Legal warranty -->
      <div class="mb-4">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {{ __('Legal warranty (Gewährleistung)') }}
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Warranty duration') }}
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="settings.legal_warranty_months"
                type="number"
                min="1"
                max="120"
                class="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ __('months') }}</span>
            </div>
          </div>
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Burden of proof period') }}
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="settings.burden_of_proof_months"
                type="number"
                min="1"
                max="120"
                class="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ __('months') }}</span>
            </div>
          </div>
          <div>
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Alert before proof shift') }}
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="settings.burden_of_proof_alert_days"
                type="number"
                min="1"
                max="365"
                class="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ __('days') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Maintenance + refund -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Maintenance reminder') }}
          </label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="settings.maintenance_reminder_days"
              type="number"
              min="1"
              max="30"
              class="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ __('days before due date') }}</span>
          </div>
        </div>
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Overdue refund re-alert') }}
          </label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="settings.refund_alert_days"
              type="number"
              min="1"
              max="90"
              class="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ __('days after return') }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Item Category Lifespans -->
    <section v-if="showLifespans" class="mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-4">{{ __('Item Lifespans') }}</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
        {{ __('Default lifespan and average replacement cost per item category. Used for health forecasts and replacement planning.') }}
      </p>

      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-caption text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
              <th class="py-2 pr-4">{{ __('Category') }}</th>
              <th class="py-2 pr-4 w-28">{{ __('Lifespan (yr)') }}</th>
              <th class="py-2 w-36">{{ __('Avg replacement cost') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(cat, idx) in settings.category_lifespans"
              :key="idx"
              class="border-b border-gray-100 dark:border-gray-700/50"
            >
              <td class="py-2 pr-4 text-gray-700 dark:text-gray-300">{{ __(cat.category) }}</td>
              <td class="py-2 pr-4">
                <input
                  v-model.number="cat.lifespan_years"
                  type="number"
                  min="1"
                  max="100"
                  class="w-20 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </td>
              <td class="py-2">
                <div class="relative">
                  <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-400">&euro;</span>
                  <input
                    v-model.number="cat.avg_replacement_cost"
                    type="number"
                    min="0"
                    step="50"
                    class="w-28 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 pl-6 text-sm
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Preferences -->
    <section v-if="showPreferences" class="mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-4">{{ __('Preferences') }}</h2>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Default currency') }}
          </label>
          <input
            v-model="settings.default_currency"
            type="text"
            maxlength="3"
            class="w-24 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 uppercase"
          />
        </div>
        <div>
          <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
            {{ __('Cost data visible to') }}
          </label>
          <select
            v-model="settings.financial_visibility"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option v-for="opt in visibilityOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
            {{ __('Controls who can see purchase prices, maintenance costs, and budget data. Children never see financial data.') }}
          </p>
        </div>
      </div>
    </section>

    <!-- Account -->
    <section v-if="showPreferences" class="mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">{{ __('Account') }}</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
        {{ __('Restart the guided onboarding tour to walk through the main features.') }}
      </p>
      <Button variant="outline" :loading="restartingTour" @click="handleRestartTour">
        {{ __('Reset onboarding tour') }}
      </Button>
    </section>

    <!-- Save -->
    <div class="flex items-center gap-3">
      <Button variant="solid" :loading="saving" @click="saveSettings">
        {{ __('Save settings') }}
      </Button>
      <span v-if="saveSuccess" class="text-sm text-green-600 dark:text-green-400">
        {{ __('Saved') }}
      </span>
      <span v-if="settingsError" class="text-sm text-red-600 dark:text-red-400">
        {{ settingsError }}
      </span>
    </div>
  </template>
</template>
