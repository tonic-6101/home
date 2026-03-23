<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Recall warning banner for appliance detail page (Feature 57).
  Visible to all roles. Dismiss is Adult+ only. Check is Adult+ only.
-->
<script setup lang="ts">
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { AlertTriangle, ExternalLink, X, Search } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

interface RecallEntry {
  recall_id: string
  recall_title: string
  recall_url: string
  match_confidence: string
  notified_date: string
  dismissed: boolean
}

const props = defineProps<{
  itemName: string
  itemType: string
  recalls: RecallEntry[]
  isAdultOrAbove: boolean
}>()

const emit = defineEmits<{ reload: [] }>()

const dismissing = ref<string | null>(null)
const checking = ref(false)
const checkResult = ref('')

const undismissedRecalls = ref<RecallEntry[]>(
  props.recalls.filter(r => !r.dismissed)
)

async function dismissRecall(recallId: string) {
  dismissing.value = recallId
  try {
    await frappeRequest({
      url: '/api/method/home.api.recall.dismiss_recall',
      params: { item_name: props.itemName, recall_id: recallId },
    })
    undismissedRecalls.value = undismissedRecalls.value.filter(r => r.recall_id !== recallId)
  } catch (e: any) {
    alert(e.message || __('Failed to dismiss recall'))
  } finally {
    dismissing.value = null
  }
}

async function checkForRecalls() {
  checking.value = true
  checkResult.value = ''
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.recall.check_single_appliance_recall',
      params: { appliance_name: props.itemName },
    })
    if (res.matches_found > 0) {
      checkResult.value = __('Found {0} possible recall(s) — see above.', [res.matches_found])
      emit('reload')
    } else {
      checkResult.value = __('No new recalls found.')
    }
    setTimeout(() => { checkResult.value = '' }, 5000)
  } catch (e: any) {
    checkResult.value = e.message || __('Recall check failed')
  } finally {
    checking.value = false
  }
}
</script>

<template>
  <!-- Recall warning banners -->
  <div
    v-if="itemType === 'Appliance' && undismissedRecalls.length"
    class="mb-4 space-y-2"
  >
    <div
      v-for="recall in undismissedRecalls"
      :key="recall.recall_id"
      class="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-300 dark:border-amber-700 rounded-lg"
    >
      <div class="flex items-start gap-2">
        <AlertTriangle class="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
        <div class="flex-1">
          <h3 class="font-semibold text-amber-900 dark:text-amber-200 text-sm">
            {{ __('Possible safety recall') }}
          </h3>
          <p class="text-sm text-amber-800 dark:text-amber-300 mt-1">
            {{ recall.recall_title }}
          </p>
          <p class="text-xs text-amber-700 dark:text-amber-400 mt-1">
            {{ __('This may or may not affect your specific model — check the EU Safety Gate to confirm.') }}
          </p>
          <div class="flex items-center gap-3 mt-2">
            <a
              v-if="recall.recall_url"
              :href="recall.recall_url"
              target="_blank"
              rel="noopener noreferrer"
              class="flex items-center gap-1 text-xs text-amber-700 dark:text-amber-400 hover:underline"
            >
              <ExternalLink class="w-3 h-3" />
              {{ __('View recall details') }}
            </a>
            <button
              v-if="isAdultOrAbove"
              @click="dismissRecall(recall.recall_id)"
              :disabled="dismissing === recall.recall_id"
              class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400
                     hover:text-gray-700 dark:hover:text-gray-200 disabled:opacity-50"
            >
              <X class="w-3 h-3" />
              {{ dismissing === recall.recall_id ? __('Dismissing…') : __('Dismiss') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Check for recalls button (Adult+ only, Appliance only) -->
  <div v-if="itemType === 'Appliance' && isAdultOrAbove" class="mb-4">
    <button
      @click="checkForRecalls"
      :disabled="checking"
      class="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400
             hover:text-gray-700 dark:hover:text-gray-200 disabled:opacity-50 transition-colors"
    >
      <Search class="w-4 h-4" :class="{ 'animate-pulse': checking }" />
      {{ checking ? __('Checking…') : __('Check for recalls') }}
    </button>
    <p v-if="checkResult" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
      {{ checkResult }}
    </p>
  </div>
</template>
