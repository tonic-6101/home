<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  iCal subscribe panel — household calendar export (Feature 56).
  Visible to all household members. Regenerate is Owner-only.
-->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { Calendar, Copy, Check, RefreshCw, ExternalLink } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  propertyName: string
  icalToken: string | null
  isOwner: boolean
}>()

const emit = defineEmits<{ 'token-regenerated': [] }>()

const expanded = ref(false)
const copied = ref(false)
const regenerating = ref(false)
const showConfirm = ref(false)

const feedUrl = computed(() => {
  if (!props.icalToken) return ''
  return `${window.location.origin}/api/method/home.api.ical.get_property_feed?token=${props.icalToken}`
})

const webcalUrl = computed(() => {
  if (!feedUrl.value) return ''
  return feedUrl.value.replace(/^https?:/, 'webcal:')
})

const googleCalUrl = computed(() => {
  if (!feedUrl.value) return ''
  return `https://calendar.google.com/calendar/r?cid=${encodeURIComponent(webcalUrl.value)}`
})

async function copyUrl() {
  if (!feedUrl.value) return
  try {
    await navigator.clipboard.writeText(feedUrl.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    const input = document.createElement('input')
    input.value = feedUrl.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

async function regenerateToken() {
  regenerating.value = true
  try {
    await frappeRequest({
      url: '/api/method/home.api.ical.regenerate_token',
      params: { property: props.property },
    })
    showConfirm.value = false
    emit('token-regenerated')
  } catch (e: any) {
    alert(e.message || __('Failed to regenerate link'))
  } finally {
    regenerating.value = false
  }
}
</script>

<template>
  <div v-if="icalToken">
    <!-- Inline toggle -->
    <button
      @click="expanded = !expanded"
      class="flex items-center gap-1.5 text-sm text-accent-600 dark:text-accent-400
             hover:text-accent-700 dark:hover:text-accent-300 transition-colors"
    >
      <Calendar class="w-4 h-4" />
      {{ __('Subscribe to calendar') }}
    </button>

    <!-- Expanded panel -->
    <div
      v-if="expanded"
      class="mt-3 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">
        {{ __('Subscribe to household calendar') }}
      </h3>
      <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
        {{ __('Copy this URL into any calendar app:') }}
      </p>

      <!-- URL + copy -->
      <div class="flex items-center gap-2 mb-3">
        <input
          :value="feedUrl"
          readonly
          class="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-xs
                 bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400 truncate"
        />
        <button
          @click="copyUrl"
          class="flex items-center gap-1 px-3 py-2 text-sm rounded-lg
                 bg-accent-50 dark:bg-accent-900/20 text-accent-600 dark:text-accent-400
                 hover:bg-accent-100 dark:hover:bg-accent-900/30 transition-colors"
        >
          <component :is="copied ? Check : Copy" class="w-3.5 h-3.5" />
          {{ copied ? __('Copied') : __('Copy URL') }}
        </button>
      </div>

      <!-- Quick subscribe buttons -->
      <div class="flex flex-wrap gap-2 mb-3">
        <a
          :href="googleCalUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border
                 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300
                 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors no-underline"
        >
          <ExternalLink class="w-3 h-3" />
          {{ __('Open in Google Calendar') }}
        </a>
        <a
          :href="webcalUrl"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border
                 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300
                 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors no-underline"
        >
          <ExternalLink class="w-3 h-3" />
          {{ __('Open in Apple Calendar') }}
        </a>
      </div>

      <!-- Regenerate (Owner only) -->
      <div v-if="isOwner">
        <div v-if="!showConfirm">
          <button
            @click="showConfirm = true"
            class="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600
                   dark:hover:text-gray-300 transition-colors"
          >
            <RefreshCw class="w-3 h-3" />
            {{ __('Regenerate link') }}
          </button>
        </div>
        <div v-else class="flex items-center gap-2">
          <span class="text-xs text-amber-600 dark:text-amber-400">
            {{ __('Existing subscriptions will stop working. Continue?') }}
          </span>
          <button
            class="rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50"
            :disabled="regenerating"
            @click="regenerateToken"
          >
            {{ regenerating ? __('Regenerating…') : __('Yes') }}
          </button>
          <button @click="showConfirm = false" class="text-xs text-gray-400 hover:text-gray-600">
            {{ __('Cancel') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
