<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Maintenance task detail page (Feature 11) with Orga/Tender integration (Features 42/43).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  ArrowLeft, Pencil, Calendar, User, MapPin, Wrench,
  RefreshCw, ExternalLink,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useHouseholdRole } from '@/composables/useHouseholdRole'
import CompleteTaskDialog from '@/components/CompleteTaskDialog.vue'
import PhotoSection from '@/components/PhotoSection.vue'

const route = useRoute()
const router = useRouter()
const taskName = computed(() => route.params.name as string)
const { isAdultOrAbove, isChild, load: loadRole } = useHouseholdRole()

const task = ref<any>(null)
const loading = ref(true)
const error = ref('')
const showCompleteDialog = ref(false)
const creatingOrga = ref(false)
const creatingTender = ref(false)

const statusDot: Record<string, string> = {
  Scheduled: 'bg-gray-400',
  'In Progress': 'bg-amber-400',
  Completed: 'bg-green-500',
  Cancelled: 'bg-gray-300',
}

const statusLabel = computed(() => {
  if (!task.value) return ''
  if (task.value.overdue) return __('Overdue')
  if (task.value.is_today) return __('Today')
  return __(task.value.status)
})

const statusDotClass = computed(() => {
  if (!task.value) return ''
  if (task.value.overdue) return 'bg-red-500'
  if (task.value.is_today) return 'bg-blue-500'
  return statusDot[task.value.status] || 'bg-gray-400'
})

function formatDate(date: string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatCurrency(value: number | null): string {
  if (value == null) return ''
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' }).format(value)
}

async function loadTask() {
  loading.value = true
  error.value = ''
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.maintenance.get_task',
      params: { name: taskName.value },
    })
    task.value = res
  } catch (e: any) {
    error.value = e.message || __('Failed to load task')
  } finally {
    loading.value = false
  }
}

async function setStatus(status: string) {
  try {
    await frappeRequest({
      url: '/api/method/frappe.client.set_value',
      params: {
        doctype: 'Home Maintenance',
        name: taskName.value,
        fieldname: 'status',
        value: status,
      },
    })
    await loadTask()
  } catch (e: any) {
    alert(e.message || __('Failed to update status'))
  }
}

async function onCompleted() {
  showCompleteDialog.value = false
  await loadTask()
}

async function createOrgaProject() {
  creatingOrga.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.integrations.create_orga_project',
      params: { maintenance_name: taskName.value },
    })
    task.value.orga_project = res?.orga_project
    if (!res?.already_exists) {
      await loadTask()
    }
  } catch (e: any) {
    alert(e.message || __('Failed to create project'))
  } finally {
    creatingOrga.value = false
  }
}

async function createTenderPost() {
  creatingTender.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.integrations.create_tender_post',
      params: { maintenance_name: taskName.value },
    })
    task.value.tender_post = res?.tender_post
  } catch (e: any) {
    alert(e.message || __('Failed to create post'))
  } finally {
    creatingTender.value = false
  }
}

function editTask() {
  window.location.href = `/app/home-maintenance/${taskName.value}`
  // TODO: replace with SPA form route when MaintenanceForm.vue is created
}

onMounted(() => {
  loadRole()
  loadTask()
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

    <template v-else-if="task">
      <!-- Back -->
      <button
        @click="router.push('/home/maintenance')"
        class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
               hover:text-gray-700 dark:hover:text-gray-200 mb-4"
      >
        <ArrowLeft class="w-4 h-4" />
        {{ __('Maintenance') }}
      </button>

      <!-- Header -->
      <div class="flex items-start justify-between mb-4">
        <div>
          <h1 class="text-h1 text-gray-900 dark:text-gray-100">
            {{ task.title }}
          </h1>
          <div class="flex items-center gap-2 mt-1">
            <span class="w-2.5 h-2.5 rounded-full" :class="statusDotClass" />
            <span
              class="text-sm font-medium"
              :class="{
                'text-red-600 dark:text-red-400': task.overdue,
                'text-blue-600 dark:text-blue-400': task.is_today,
                'text-gray-600 dark:text-gray-400': !task.overdue && !task.is_today,
              }"
            >
              {{ statusLabel }}
            </span>
            <span class="text-sm text-gray-400 dark:text-gray-500">·</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ __(task.category) }}</span>
          </div>
        </div>

        <button
          v-if="isAdultOrAbove && task.status !== 'Completed' && task.status !== 'Cancelled'"
          @click="editTask"
          class="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300
                 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <Pencil class="w-3.5 h-3.5" />
          {{ __('Edit') }}
        </button>
      </div>

      <!-- Details card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4 space-y-3">
        <!-- Location -->
        <div v-if="task.room_name || task.item_name" class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <MapPin class="w-4 h-4 text-gray-400" />
          <span>
            <template v-if="task.room_name">{{ task.room_name }}</template>
            <template v-if="task.room_name && task.item_name"> · </template>
            <template v-if="task.item_name">{{ task.item_name }}</template>
          </span>
        </div>

        <!-- Scheduled date -->
        <div v-if="task.scheduled_date" class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <Calendar class="w-4 h-4 text-gray-400" />
          <span>{{ __('Scheduled') }}: {{ formatDate(task.scheduled_date) }}</span>
        </div>

        <!-- Completed date -->
        <div v-if="task.completed_date" class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <Calendar class="w-4 h-4 text-green-500" />
          <span>{{ __('Completed') }}: {{ formatDate(task.completed_date) }}</span>
        </div>

        <!-- Contractor -->
        <div v-if="task.contractor_name" class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <User class="w-4 h-4 text-gray-400" />
          <a
            :href="`/app/contact/${task.contractor}`"
            class="text-home-600 dark:text-home-400 hover:underline"
          >
            {{ task.contractor_name }}
          </a>
        </div>

        <!-- Cost (Adult+ only) -->
        <div v-if="!isChild && task.cost != null" class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <Wrench class="w-4 h-4 text-gray-400" />
          <span>{{ __('Cost') }}: {{ formatCurrency(task.cost) }}</span>
        </div>

        <!-- Recurring indicator -->
        <div v-if="task.maintenance_type === 'Recurring'" class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <RefreshCw class="w-4 h-4" />
          <span>{{ __(task.recurrence) }} · {{ __('Next occurrence created on completion') }}</span>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="task.notes" class="mb-4">
        <h2 class="text-h4 text-gray-800 dark:text-gray-200 mb-2">{{ __('Notes') }}</h2>
        <div
          class="text-sm text-gray-600 dark:text-gray-400 prose prose-sm dark:prose-invert max-w-none"
          v-html="task.notes"
        />
      </div>

      <!-- Photos (Feature 59) -->
      <div class="mb-4">
        <PhotoSection
          :property="task.property"
          :maintenance="task.name"
          :can-edit="isAdultOrAbove"
        />
      </div>

      <!-- Status actions (Adult+ only) -->
      <div
        v-if="isAdultOrAbove && task.status !== 'Completed' && task.status !== 'Cancelled'"
        class="flex flex-wrap gap-2 mb-6"
      >
        <Button
          v-if="task.status === 'Scheduled'"
          variant="outline"
          @click="setStatus('In Progress')"
        >
          {{ __('Mark as In Progress') }}
        </Button>
        <Button
          variant="solid"
          @click="showCompleteDialog = true"
        >
          {{ __('Mark as Complete') }}
        </Button>
      </div>

      <!-- Soft integration actions (Feature 42/43 — Adult+ only) -->
      <div
        v-if="isAdultOrAbove && (task.has_orga || task.has_tender)"
        class="border-t border-gray-200 dark:border-gray-700 pt-4 space-y-2"
      >
        <div class="text-xs text-gray-400 dark:text-gray-500 font-medium mb-2">
          {{ __('Actions') }}
        </div>

        <!-- Orga integration (Feature 43) -->
        <template v-if="task.has_orga">
          <!-- Already linked — navigate -->
          <a
            v-if="task.orga_project"
            :href="`/app/orga-project/${task.orga_project}`"
            class="flex items-center gap-2 text-sm text-home-600 dark:text-home-400 hover:underline no-underline"
          >
            <ExternalLink class="w-4 h-4" />
            {{ __('View Orga Project') }}
          </a>
          <!-- Create new -->
          <Button
            v-else
            variant="outline"
            :loading="creatingOrga"
            @click="createOrgaProject"
          >
            {{ __('Create Project in Orga') }} →
          </Button>
        </template>

        <!-- Tender integration (Feature 42) -->
        <template v-if="task.has_tender">
          <a
            v-if="task.tender_post"
            :href="`/app/tender-post/${task.tender_post}`"
            class="flex items-center gap-2 text-sm text-home-600 dark:text-home-400 hover:underline no-underline"
          >
            <ExternalLink class="w-4 h-4" />
            {{ __('View Tender Post') }}
          </a>
          <Button
            v-else
            variant="outline"
            :loading="creatingTender"
            @click="createTenderPost"
          >
            {{ __('Get Quotes via Tender') }} →
          </Button>
        </template>
      </div>
    </template>

    <!-- Complete task dialog -->
    <CompleteTaskDialog
      v-if="showCompleteDialog"
      :task-name="taskName"
      @close="showCompleteDialog = false"
      @completed="onCompleted"
    />
  </div>
</template>
