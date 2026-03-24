<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Frame share panel — read-only guest link for property (Feature 55).
  Owner-only. Hidden when Frame is not installed.
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { Share2, Copy, Check, RefreshCw } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  frameToken: string | null
  isOwner: boolean
}>()

const emit = defineEmits<{ 'token-regenerated': [] }>()

const frameInstalled = computed(() =>
  !!(window as any).frappe?.boot?.dock?.installed_apps?.includes?.('frame')
    || (window as any).frappe?.boot?.installed_apps?.includes?.('frame')
)

const copied = ref(false)
const regenerating = ref(false)
const showConfirm = ref(false)

const guestUrl = computed(() => {
  if (!props.frameToken) return ''
  const site = window.location.origin
  return `${site}/frame/home-property/${props.frameToken}`
})

async function copyUrl() {
  if (!guestUrl.value) return
  try {
    await navigator.clipboard.writeText(guestUrl.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback for non-HTTPS
    const input = document.createElement('input')
    input.value = guestUrl.value
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
      url: '/api/method/home.api.frame.regenerate_token',
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
  <section
    v-if="frameInstalled && isOwner && frameToken"
    class="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
  >
    <div class="flex items-center gap-2 mb-3">
      <Share2 class="w-4 h-4 text-gray-400" />
      <h2 class="text-sm font-semibold text-gray-800 dark:text-gray-200">
        {{ __('Share property') }}
      </h2>
    </div>

    <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
      {{ __('Share a read-only link to this property\'s appliances, maintenance history, and warranties. No login required.') }}
    </p>

    <!-- URL + copy -->
    <div class="flex items-center gap-2 mb-3">
      <input
        :value="guestUrl"
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
        {{ copied ? __('Copied') : __('Copy') }}
      </button>
    </div>

    <!-- Regenerate -->
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
        {{ __('This will invalidate the current link. Continue?') }}
      </span>
      <Button variant="solid" size="sm" :loading="regenerating" @click="regenerateToken">
        {{ __('Yes, regenerate') }}
      </Button>
      <button
        @click="showConfirm = false"
        class="text-xs text-gray-400 hover:text-gray-600"
      >
        {{ __('Cancel') }}
      </button>
    </div>
  </section>
</template>
