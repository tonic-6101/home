<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { frappeRequest, useFileUpload } from 'frappe-ui'
import HouseholdMemberAvatar from '@/components/HouseholdMemberAvatar.vue'
import { __ } from '@/composables/useTranslate'
import { useOnboardingTour } from '@/composables/useOnboardingTour'

interface MemberProfile {
  name: string
  display_name: string
  role: 'Owner' | 'Adult' | 'Child'
  avatar: string | null
}

const currentUser = (window as any).frappe?.session?.user || ''
const household = ref('')
const profile = ref<MemberProfile | null>(null)
const loading = ref(true)
const error = ref('')

// Profile editing
const editDisplayName = ref('')
const savingProfile = ref(false)
const avatarFileInput = ref<HTMLInputElement | null>(null)
const uploadingAvatar = ref(false)
const avatarUploader = useFileUpload()

// Onboarding tour
const { restartTour } = useOnboardingTour()
const restartingTour = ref(false)

async function handleRestartTour() {
  restartingTour.value = true
  await restartTour()
  restartingTour.value = false
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const households = await frappeRequest({
      url: '/api/method/home.api.permission.get_user_households',
    })
    const list = households || []
    if (!list.length) {
      error.value = __('No household found. Create one in Settings first.')
      loading.value = false
      return
    }
    household.value = list[0]
    await loadProfile()
  } catch (e: any) {
    error.value = e.message || __('Failed to load preferences')
  } finally {
    loading.value = false
  }
}

async function loadProfile() {
  const members = await frappeRequest({
    url: '/api/method/home.api.household.get_members',
    params: { household: household.value },
  })
  const me = (members || []).find((m: any) => m.user === currentUser)
  if (me) {
    profile.value = me
    editDisplayName.value = me.display_name
  }
}

async function saveProfile() {
  if (!editDisplayName.value.trim()) return
  savingProfile.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.household.update_own_profile',
      params: {
        household: household.value,
        display_name: editDisplayName.value.trim(),
      },
    })
    await loadProfile()
  } catch (e: any) {
    alert(e.message || __('Failed to update profile'))
  } finally {
    savingProfile.value = false
  }
}

async function uploadAvatar(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    alert(__('Image must be smaller than 5 MB'))
    input.value = ''
    return
  }

  uploadingAvatar.value = true
  try {
    const uploadResult = await avatarUploader.upload(file, {
      doctype: 'Home Household',
      docname: household.value,
      private: false,
    })

    const fileUrl = uploadResult?.file_url
    if (fileUrl) {
      await frappeRequest({
        url: '/api/method/home.api.household.update_own_profile',
        params: {
          household: household.value,
          avatar: fileUrl,
        },
      })
      await loadProfile()
    }
  } catch (e: any) {
    alert(e.message || __('Failed to upload avatar'))
  } finally {
    uploadingAvatar.value = false
    input.value = ''
  }
}

onMounted(load)
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <h1 class="text-h1 text-gray-900 dark:text-gray-100 mb-6">
      {{ __('Preferences') }}
    </h1>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500">
      {{ __('Loading…') }}
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <template v-else>
      <!-- Profile Section -->
      <section
        v-if="profile"
        class="mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
      >
        <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-4">
          {{ __('Your Profile') }}
        </h2>
        <div class="flex gap-4 items-start">
          <!-- Avatar -->
          <div class="flex flex-col items-center gap-2">
            <HouseholdMemberAvatar
              :display-name="profile.display_name"
              :avatar="profile.avatar"
              size="lg"
            />
            <input
              ref="avatarFileInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="uploadAvatar"
            />
            <button
              @click="avatarFileInput?.click()"
              :disabled="uploadingAvatar"
              class="text-xs text-accent-600 dark:text-accent-400 hover:underline disabled:opacity-50"
            >
              {{ uploadingAvatar ? __('Uploading…') : __('Change photo') }}
            </button>
          </div>

          <!-- Display name -->
          <div class="flex-1">
            <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
              {{ __('Display Name') }}
            </label>
            <input
              v-model="editDisplayName"
              type="text"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              @keyup.enter="saveProfile"
            />
            <div class="text-caption text-gray-400 dark:text-gray-500 mt-1">
              {{ __('Role:') }} {{ profile.role }}
            </div>
            <div class="mt-3">
              <Button
                @click="saveProfile"
                variant="solid"
                :loading="savingProfile"
              >
                {{ __('Save') }}
              </Button>
            </div>
          </div>
        </div>
      </section>

      <!-- Tour Section -->
      <section class="mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
          {{ __('Tour') }}
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
          {{ __('Restart the guided onboarding tour to walk through the main features.') }}
        </p>
        <Button
          variant="outline"
          :loading="restartingTour"
          @click="handleRestartTour"
        >
          {{ __('Restart tour') }}
        </Button>
      </section>
    </template>
  </div>
</template>
