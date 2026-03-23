<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Moving house wizard — checklist with progress tracking (Feature 46).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  ArrowLeft, Truck, Check, SkipForward, Plus, ChevronDown,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'
import { useHouseholdRole } from '@/composables/useHouseholdRole'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()
const { isAdultOrAbove, load: loadRole } = useHouseholdRole()

const checklist = ref<any>(null)
const loading = ref(true)
const generating = ref(false)
const expandedPhase = ref<string | null>('Before')

// Add task form
const showAddTask = ref(false)
const newTitle = ref('')
const newPhase = ref('Before')
const newCategory = ref('Other')
const addingTask = ref(false)

const phases = ['Before', 'Moving day', 'After']
const categories = ['Utilities', 'Finance', 'Admin', 'Insurance', 'Logistics', 'Technology', 'Security', 'Safety', 'Health', 'Community', 'Other']

async function loadChecklist() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.moving.get_checklist',
      params: { property: propName },
    })
    checklist.value = res
  } catch {
    checklist.value = null
  } finally {
    loading.value = false
  }
}

async function generateChecklist() {
  generating.value = true
  try {
    const propName = await loadPropertyName()
    await frappeRequest({
      url: '/api/method/home.api.moving.generate_checklist',
      params: { property: propName },
    })
    await loadChecklist()
  } catch (e: any) {
    alert(e.message || __('Failed to generate checklist'))
  } finally {
    generating.value = false
  }
}

async function updateTask(idx: number, status: string) {
  try {
    const propName = await loadPropertyName()
    await frappeRequest({
      url: '/api/method/home.api.moving.update_task_status',
      params: { property: propName, idx, status },
    })
    await loadChecklist()
  } catch (e: any) {
    alert(e.message || __('Failed to update'))
  }
}

async function addTask() {
  if (!newTitle.value.trim()) return
  addingTask.value = true
  try {
    const propName = await loadPropertyName()
    await frappeRequest({
      url: '/api/method/home.api.moving.add_custom_task',
      params: {
        property: propName,
        title: newTitle.value.trim(),
        phase: newPhase.value,
        category: newCategory.value,
      },
    })
    newTitle.value = ''
    showAddTask.value = false
    await loadChecklist()
  } catch (e: any) {
    alert(e.message || __('Failed to add task'))
  } finally {
    addingTask.value = false
  }
}

const progress = computed(() => {
  if (!checklist.value?.tasks?.length) return 0
  const tasks = checklist.value.tasks
  const done = tasks.filter((t: any) => t.status === 'Done').length
  const total = tasks.filter((t: any) => t.status !== 'Skipped').length
  return total > 0 ? Math.round((done / total) * 100) : 0
})

function tasksByPhase(phase: string) {
  if (!checklist.value?.tasks) return []
  return checklist.value.tasks.filter((t: any) => t.phase === phase)
}

onMounted(() => {
  loadRole()
  loadChecklist()
})
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <button
      class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
             hover:text-gray-700 dark:hover:text-gray-300 mb-4"
      @click="router.push('/home')"
    >
      <ArrowLeft class="w-4 h-4" />
      {{ __('My Home') }}
    </button>

    <h1 class="text-h1 text-gray-900 dark:text-gray-100 mb-6">{{ __('Moving Checklist') }}</h1>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <!-- No checklist yet -->
    <div v-else-if="!checklist?.tasks?.length" class="text-center py-12">
      <Truck class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">{{ __('Moving soon?') }}</h2>
      <p class="text-body text-gray-500 dark:text-gray-400 mb-4">
        {{ __('Generate a checklist of common tasks for your move.') }}
      </p>
      <Button variant="solid" :loading="generating" @click="generateChecklist">
        {{ __('Generate Checklist') }}
      </Button>
    </div>

    <template v-else>
      <!-- Progress bar -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ progress }}% {{ __('complete') }}
          </span>
          <Button v-if="isAdultOrAbove" variant="ghost" size="sm" @click="showAddTask = !showAddTask">
            <template #prefix><Plus class="w-3.5 h-3.5" /></template>
            {{ __('Add task') }}
          </Button>
        </div>
        <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-home-500 rounded-full transition-all duration-500"
            :style="{ width: progress + '%' }"
          />
        </div>
      </div>

      <!-- Add task form -->
      <div v-if="showAddTask" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4 space-y-3">
        <input
          v-model="newTitle"
          type="text"
          :placeholder="__('Task title')"
          class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          @keyup.enter="addTask"
        />
        <div class="flex gap-2">
          <select
            v-model="newPhase"
            class="border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1.5 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option v-for="p in phases" :key="p" :value="p">{{ __(p) }}</option>
          </select>
          <select
            v-model="newCategory"
            class="border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1.5 text-sm
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
          </select>
        </div>
        <div class="flex gap-2">
          <Button variant="solid" size="sm" :loading="addingTask" @click="addTask">{{ __('Add') }}</Button>
          <Button variant="ghost" size="sm" @click="showAddTask = false">{{ __('Cancel') }}</Button>
        </div>
      </div>

      <!-- Phase groups -->
      <div v-for="phase in phases" :key="phase" class="mb-4">
        <button
          class="flex items-center gap-2 w-full text-left mb-2"
          @click="expandedPhase = expandedPhase === phase ? null : phase"
        >
          <ChevronDown
            class="w-4 h-4 text-gray-400 transition-transform"
            :class="{ 'rotate-180': expandedPhase !== phase }"
          />
          <span class="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
            {{ __(phase) }}
          </span>
          <span class="text-xs text-gray-400 dark:text-gray-500">
            ({{ tasksByPhase(phase).filter((t: any) => t.status === 'Done').length }}/{{ tasksByPhase(phase).filter((t: any) => t.status !== 'Skipped').length }})
          </span>
        </button>

        <div v-if="expandedPhase === phase" class="space-y-1">
          <div
            v-for="task in tasksByPhase(phase)"
            :key="task.idx"
            class="flex items-center gap-3 px-3 py-2 rounded-lg"
            :class="task.status === 'Done'
              ? 'bg-green-50 dark:bg-green-900/10'
              : task.status === 'Skipped'
                ? 'bg-gray-50 dark:bg-gray-800 opacity-50'
                : 'bg-white dark:bg-gray-800'"
          >
            <button
              v-if="task.status === 'To do' && isAdultOrAbove"
              class="w-5 h-5 rounded border-2 border-gray-300 dark:border-gray-600 flex items-center justify-center
                     hover:border-green-500 transition-colors flex-shrink-0"
              @click="updateTask(task.idx, 'Done')"
              :title="__('Mark done')"
            />
            <Check
              v-else-if="task.status === 'Done'"
              class="w-5 h-5 text-green-500 flex-shrink-0"
            />
            <SkipForward
              v-else-if="task.status === 'Skipped'"
              class="w-5 h-5 text-gray-400 flex-shrink-0"
            />

            <span
              class="flex-1 text-sm"
              :class="task.status === 'Done'
                ? 'text-gray-500 dark:text-gray-400 line-through'
                : task.status === 'Skipped'
                  ? 'text-gray-400 dark:text-gray-500 line-through'
                  : 'text-gray-900 dark:text-gray-100'"
            >
              {{ task.title }}
            </span>

            <button
              v-if="task.status === 'To do' && isAdultOrAbove"
              class="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              @click="updateTask(task.idx, 'Skipped')"
            >
              {{ __('Skip') }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
