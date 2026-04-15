<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Purchase returns list — property-scoped (Feature 18).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { RotateCcw, ArrowLeft } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'
import ReturnCard, { type ReturnSummary } from '@/components/ReturnCard.vue'
import CreateReturnDialog from '@/components/CreateReturnDialog.vue'
import MarkReceivedDialog from '@/components/MarkReceivedDialog.vue'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()

const returns = ref<ReturnSummary[]>([])
const loading = ref(true)
const showCreateDialog = ref(false)
const markReceivedTarget = ref<string | null>(null)

async function loadReturns() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.returns.get_returns',
      params: { property: propName },
    })
    returns.value = res?.returns || []
  } catch {
    returns.value = []
  } finally {
    loading.value = false
  }
}

function onCreated() {
  showCreateDialog.value = false
  loadReturns()
}

function onMarkReceived(name: string) {
  markReceivedTarget.value = name
}

function onRefundSaved() {
  markReceivedTarget.value = null
  loadReturns()
}

const pendingCount = computed(() =>
  returns.value.filter(r => r.refund_status === 'Pending').length,
)

const overdueCount = computed(() =>
  returns.value.filter(r => r.overdue_followup).length,
)

onMounted(loadReturns)
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <!-- Back link -->
    <button
      class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
             hover:text-gray-700 dark:hover:text-gray-300 mb-4"
      @click="router.push('/home')"
    >
      <ArrowLeft class="w-4 h-4" />
      {{ __('My Home') }}
    </button>

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-h1 text-gray-900 dark:text-gray-100">
        {{ __('Purchase Returns') }}
      </h1>
      <button
        class="rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50"
        @click="showCreateDialog = true"
      >
        {{ __('+ Add') }}
      </button>
    </div>

    <!-- Summary bar -->
    <div
      v-if="!loading && returns.length"
      class="flex gap-4 mb-4 text-sm text-gray-500 dark:text-gray-400"
    >
      <span>{{ returns.length }} {{ returns.length === 1 ? __('return') : __('returns') }}</span>
      <span v-if="pendingCount">{{ pendingCount }} {{ __('pending') }}</span>
      <span v-if="overdueCount" class="text-amber-600 dark:text-amber-400">
        {{ overdueCount }} {{ __('overdue') }}
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- Empty -->
    <div v-else-if="!returns.length" class="text-center py-12">
      <RotateCcw class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No returns yet') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400 mb-4">
        {{ __('Track items returned to retailers and follow up on refunds.') }}
      </p>
      <button
        class="rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50"
        @click="showCreateDialog = true"
      >
        {{ __('Add Return') }}
      </button>
    </div>

    <!-- Return cards -->
    <div v-else class="space-y-3">
      <ReturnCard
        v-for="r in returns"
        :key="r.name"
        :return-item="r"
        @mark-received="onMarkReceived"
      />
    </div>

    <!-- Create dialog -->
    <CreateReturnDialog
      v-if="showCreateDialog"
      :property="propertyName"
      @close="showCreateDialog = false"
      @created="onCreated"
    />

    <!-- Mark received dialog -->
    <MarkReceivedDialog
      v-if="markReceivedTarget"
      :return-name="markReceivedTarget"
      @close="markReceivedTarget = null"
      @saved="onRefundSaved"
    />
  </div>
</template>
