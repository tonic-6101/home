<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Insurance policy list — property-scoped (Feature 28).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { Shield, ArrowLeft } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'
import InsuranceCard, { type PolicySummary } from '@/components/InsuranceCard.vue'
import CreatePolicyDialog from '@/components/CreatePolicyDialog.vue'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()

const policies = ref<PolicySummary[]>([])
const totalPremium = ref(0)
const loading = ref(true)
const showCreateDialog = ref(false)

async function loadPolicies() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.insurance.get_policies',
      params: { property: propName },
    })
    policies.value = res?.policies || []
    totalPremium.value = res?.total_annual_premium || 0
  } catch {
    policies.value = []
  } finally {
    loading.value = false
  }
}

function onCreated() {
  showCreateDialog.value = false
  loadPolicies()
}

function formatCurrency(amount: number): string {
  if (!amount) return ''
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
  }).format(amount)
}

const renewingSoonCount = computed(() =>
  policies.value.filter(p => p.renewal_status === 'renewing_soon').length,
)

onMounted(loadPolicies)
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
        {{ __('Insurance') }}
      </h1>
      <Button variant="solid" @click="showCreateDialog = true">
        {{ __('+ Add') }}
      </Button>
    </div>

    <!-- Summary bar -->
    <div
      v-if="!loading && policies.length"
      class="flex gap-4 mb-4 text-sm text-gray-500 dark:text-gray-400"
    >
      <span>{{ policies.length }} {{ policies.length === 1 ? __('policy') : __('policies') }}</span>
      <span v-if="totalPremium">{{ formatCurrency(totalPremium) }}/{{ __('yr') }} {{ __('total') }}</span>
      <span v-if="renewingSoonCount" class="text-amber-600 dark:text-amber-400">
        {{ renewingSoonCount }} {{ __('renewing soon') }}
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      {{ __('Loading…') }}
    </div>

    <!-- Empty -->
    <div v-else-if="!policies.length" class="text-center py-12">
      <Shield class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('No insurance policies yet') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400 mb-4">
        {{ __('Track your property insurance policies and renewal dates.') }}
      </p>
      <Button variant="solid" @click="showCreateDialog = true">
        {{ __('Add Policy') }}
      </Button>
    </div>

    <!-- Policy cards -->
    <div v-else class="space-y-3">
      <InsuranceCard
        v-for="p in policies"
        :key="p.name"
        :policy="p"
      />
    </div>

    <!-- Create dialog -->
    <CreatePolicyDialog
      v-if="showCreateDialog"
      :property="propertyName"
      @close="showCreateDialog = false"
      @created="onCreated"
    />
  </div>
</template>
