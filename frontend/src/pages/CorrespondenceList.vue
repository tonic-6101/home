<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Household correspondence — letter templates and generated letters (Feature 35).
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { ArrowLeft, Mail, FileText, Download, Copy, ChevronDown } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()

interface LetterTemplate {
  name: string
  template_name: string
  situation_type: string
  is_system_template: boolean
}

interface TemplateGroup {
  situation_type: string
  templates: LetterTemplate[]
}

const groups = ref<TemplateGroup[]>([])
const loading = ref(true)

// Preview state
const previewTemplate = ref<string | null>(null)
const previewData = ref<any>(null)
const previewLoading = ref(false)
const exporting = ref(false)

async function loadTemplates() {
  loading.value = true
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.correspondence.get_templates',
    })
    // Group by situation_type
    const map: Record<string, LetterTemplate[]> = {}
    for (const t of (res?.templates || [])) {
      if (!map[t.situation_type]) map[t.situation_type] = []
      map[t.situation_type].push(t)
    }
    groups.value = Object.entries(map).map(([k, v]) => ({
      situation_type: k,
      templates: v,
    }))
  } catch {
    groups.value = []
  } finally {
    loading.value = false
  }
}

async function previewLetter(templateName: string) {
  if (previewTemplate.value === templateName) {
    previewTemplate.value = null
    previewData.value = null
    return
  }
  previewTemplate.value = templateName
  previewLoading.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.correspondence.render_draft',
      params: { template: templateName, record_doctype: 'Home Property', record_name: propName },
    })
    previewData.value = res
  } catch {
    previewData.value = { subject: __('Preview failed'), body: '' }
  } finally {
    previewLoading.value = false
  }
}

async function exportPdf() {
  if (!previewData.value) return
  exporting.value = true
  try {
    const propName = await loadPropertyName()
    const res = await frappeRequest({
      url: '/api/method/home.api.correspondence.export_pdf',
      params: {
        subject: previewData.value.subject,
        body: previewData.value.body,
        property: propName,
      },
    })
    if (res?.file_url) {
      window.open(res.file_url, '_blank')
    }
  } catch (e: any) {
    alert(e.message || __('Export failed'))
  } finally {
    exporting.value = false
  }
}

function copyToClipboard() {
  if (!previewData.value) return
  const text = `${previewData.value.subject}\n\n${previewData.value.body}`
  navigator.clipboard.writeText(text)
}

onMounted(loadTemplates)
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

    <h1 class="text-h1 text-gray-900 dark:text-gray-100 mb-2">{{ __('Correspondence') }}</h1>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
      {{ __('Letter templates pre-filled from your Home data.') }}
    </p>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <div v-else-if="!groups.length" class="text-center py-12">
      <Mail class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <p class="text-gray-500 dark:text-gray-400">{{ __('No letter templates available.') }}</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="group in groups" :key="group.situation_type">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 mb-2">
          {{ __(group.situation_type) }}
        </h2>

        <div class="space-y-2">
          <div
            v-for="tmpl in group.templates"
            :key="tmpl.name"
            class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            <button
              class="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
              @click="previewLetter(tmpl.name)"
            >
              <FileText class="w-5 h-5 text-gray-400 flex-shrink-0" />
              <span class="flex-1 text-sm font-medium text-gray-900 dark:text-gray-100 text-left">
                {{ tmpl.template_name }}
              </span>
              <span v-if="tmpl.is_system_template" class="text-xs text-gray-400 dark:text-gray-500">
                {{ __('System') }}
              </span>
              <ChevronDown
                class="w-4 h-4 text-gray-400 transition-transform"
                :class="{ 'rotate-180': previewTemplate === tmpl.name }"
              />
            </button>

            <!-- Preview -->
            <div
              v-if="previewTemplate === tmpl.name"
              class="border-t border-gray-200 dark:border-gray-700 px-4 py-4"
            >
              <div v-if="previewLoading" class="text-sm text-gray-500 dark:text-gray-400">
                {{ __('Rendering preview…') }}
              </div>
              <template v-else-if="previewData">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                  {{ previewData.subject }}
                </div>
                <div
                  class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line mb-4
                         max-h-64 overflow-y-auto"
                  v-html="previewData.body"
                />
                <div class="flex gap-2">
                  <Button variant="outline" size="sm" :loading="exporting" @click="exportPdf">
                    <template #prefix><Download class="w-3.5 h-3.5" /></template>
                    {{ __('Download PDF') }}
                  </Button>
                  <Button variant="outline" size="sm" @click="copyToClipboard">
                    <template #prefix><Copy class="w-3.5 h-3.5" /></template>
                    {{ __('Copy') }}
                  </Button>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
