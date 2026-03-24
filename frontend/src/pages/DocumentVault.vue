<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Document vault — grouped view over all attached files with upload (Feature 34).
-->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest, useFileUpload } from 'frappe-ui'
import {
  ArrowLeft, FolderOpen, FileText, BookOpen, Image,
  Shield, Receipt, Home, File, Plus, Upload, X,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'
import { useHouseholdRole } from '@/composables/useHouseholdRole'

const router = useRouter()
const { propertyName, load: loadPropertyName } = useProperty()
const { isAdultOrAbove, isChild, load: loadRole } = useHouseholdRole()
const fileUploader = useFileUpload()

// --- Types ---

interface VaultFile {
  file_name: string
  file_url: string
  file_size: number
  added: string
  source_doctype: string
  source_name: string
  source_label: string
  vault_category: string
  repo_title?: string
  repo_summary?: string
  repo_tags?: string[]
}

interface LinkTarget {
  doctype: string
  label: string
  records: { name: string; label: string }[]
}

// --- State ---

const groups = ref<Record<string, VaultFile[]>>({})
const total = ref(0)
const repoActive = ref(false)
const loading = ref(true)
const activeCategory = ref('all')
const propertyLabel = ref('')

// Upload dialog state
const showUploadDialog = ref(false)
const uploadFile = ref<File | null>(null)
const uploadFileName = ref('')
const uploading = ref(false)
const uploadError = ref('')
const linkTargets = ref<LinkTarget[]>([])
const selectedDoctype = ref('')
const selectedRecord = ref('')

// --- Constants ---

const categoryOrder = ['Manuals & Receipts', 'Warranties', 'Insurance', 'Receipts & Invoices', 'Property', 'Other']

const categoryIcons: Record<string, any> = {
  'Manuals & Receipts': BookOpen,
  'Warranties': Shield,
  'Insurance': Shield,
  'Receipts & Invoices': Receipt,
  'Property': Home,
  'Other': File,
}

const categoryDefaults: Record<string, string> = {
  'Manuals & Receipts': 'Home Item',
  'Warranties': 'Home Warranty',
  'Insurance': 'Home Insurance Policy',
  'Receipts & Invoices': 'Home Maintenance',
  'Property': 'Home Property',
}

// --- Computed ---

const orderedCategories = computed(() => {
  const cats: string[] = []
  for (const cat of categoryOrder) {
    if (groups.value[cat]?.length) cats.push(cat)
  }
  // Add any unexpected categories
  for (const cat of Object.keys(groups.value)) {
    if (!cats.includes(cat) && groups.value[cat]?.length) cats.push(cat)
  }
  return cats
})

const visibleGroups = computed(() => {
  if (activeCategory.value === 'all') return groups.value
  const cat = activeCategory.value
  if (groups.value[cat]) return { [cat]: groups.value[cat] }
  return {}
})

const availableRecords = computed(() => {
  const target = linkTargets.value.find(t => t.doctype === selectedDoctype.value)
  return target?.records || []
})

// --- API calls ---

async function loadVault() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    if (!propName) {
      loading.value = false
      return
    }

    const res = await frappeRequest({
      url: '/api/method/home.api.document_vault.get_vault',
      params: { property: propName },
    })

    groups.value = res?.groups || {}
    total.value = res?.total || 0
    repoActive.value = res?.repo_active || false
  } catch {
    groups.value = {}
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function loadLinkTargets() {
  if (!propertyName.value) return
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.document_vault.get_link_targets',
      params: { property: propertyName.value },
    })
    linkTargets.value = res?.targets || []
  } catch {
    linkTargets.value = []
  }
}

// --- Upload flow ---

function openUploadDialog() {
  uploadFile.value = null
  uploadFileName.value = ''
  uploading.value = false
  uploadError.value = ''

  // Smart default: if on a category tab, pre-select matching DocType
  const defaultDoctype = activeCategory.value !== 'all'
    ? categoryDefaults[activeCategory.value] || ''
    : ''
  selectedDoctype.value = defaultDoctype
  selectedRecord.value = ''

  loadLinkTargets()
  showUploadDialog.value = true
}

function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 25 * 1024 * 1024) {
    uploadError.value = __('File must be smaller than 25 MB')
    input.value = ''
    return
  }
  uploadFile.value = file
  uploadFileName.value = file.name
  uploadError.value = ''
}

function onFileDrop(event: DragEvent) {
  event.preventDefault()
  const file = event.dataTransfer?.files?.[0]
  if (!file) return
  if (file.size > 25 * 1024 * 1024) {
    uploadError.value = __('File must be smaller than 25 MB')
    return
  }
  uploadFile.value = file
  uploadFileName.value = file.name
  uploadError.value = ''
}

async function submitUpload() {
  if (!uploadFile.value || !selectedDoctype.value || !selectedRecord.value) return

  uploading.value = true
  uploadError.value = ''
  try {
    // Step 1: Upload file via Frappe's standard upload
    const uploadResult = await fileUploader.upload(uploadFile.value, {
      doctype: selectedDoctype.value,
      docname: selectedRecord.value,
      private: false,
    })

    const fileUrl = uploadResult?.file_url
    if (!fileUrl) throw new Error(__('Upload failed'))

    // Step 2: Re-attach to the chosen record
    await frappeRequest({
      url: '/api/method/home.api.document_vault.upload_to_record',
      params: {
        property: propertyName.value,
        doctype: selectedDoctype.value,
        record: selectedRecord.value,
        file_url: fileUrl,
      },
    })

    showUploadDialog.value = false
    await loadVault()
  } catch (e: any) {
    uploadError.value = e.message || __('Failed to upload document')
  } finally {
    uploading.value = false
  }
}

// Auto-select record when doctype changes and only one record exists
watch(selectedDoctype, () => {
  selectedRecord.value = ''
  if (availableRecords.value.length === 1) {
    selectedRecord.value = availableRecords.value[0].name
  }
})

// --- Helpers ---

function formatDate(d: string): string {
  if (!d) return ''
  return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatSize(bytes: number): string {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function fileIcon(fileName: string) {
  const ext = fileName?.split('.').pop()?.toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext || '')) return Image
  return FileText
}

function sourceRoute(doctype: string, name: string): string {
  const routes: Record<string, string> = {
    'Home Property': '/home',
    'Home Item': `/home/items/${name}`,
    'Home Maintenance': `/home/maintenance/${name}`,
    'Home Warranty': `/home/items?tab=warranties`,
    'Home Insurance Policy': `/home/insurance/${name}`,
    'Home Utility Bill': '/home/utilities',
    'Home Purchase Return': '/home/returns',
  }
  return routes[doctype] || '/home'
}

onMounted(async () => {
  await loadRole()
  await loadVault()
})
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Back nav -->
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
      <h1 class="text-h1 text-gray-900 dark:text-gray-100">{{ __('Document Vault') }}</h1>
      <button
        v-if="isAdultOrAbove && !loading && propertyName"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
               bg-accent-600 text-white hover:bg-accent-700 transition-colors"
        @click="openUploadDialog"
      >
        <Plus class="w-4 h-4" />
        {{ __('Add') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <!-- Empty state -->
    <div v-else-if="!total" class="text-center py-12">
      <FolderOpen class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">{{ __('No documents yet') }}</h2>
      <p class="text-body text-gray-500 dark:text-gray-400 mb-4">
        {{ __('Attach files to your items, warranties, or maintenance tasks and they will appear here.') }}
      </p>
      <button
        v-if="isAdultOrAbove"
        class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium
               bg-accent-600 text-white hover:bg-accent-700 transition-colors"
        @click="openUploadDialog"
      >
        <Plus class="w-4 h-4" />
        {{ __('Add your first document') }}
      </button>
    </div>

    <!-- Vault content -->
    <div v-else>
      <!-- Category filter chips -->
      <div class="flex flex-wrap gap-2 mb-6">
        <button
          class="px-3 py-1.5 rounded-full text-sm transition-colors"
          :class="activeCategory === 'all'
            ? 'bg-accent-100 dark:bg-accent-900/30 text-accent-700 dark:text-accent-300 font-medium'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'"
          @click="activeCategory = 'all'"
        >
          {{ __('All') }}
          <span class="ml-1 text-xs opacity-60">{{ total }}</span>
        </button>
        <button
          v-for="cat in orderedCategories"
          :key="cat"
          class="px-3 py-1.5 rounded-full text-sm transition-colors"
          :class="activeCategory === cat
            ? 'bg-accent-100 dark:bg-accent-900/30 text-accent-700 dark:text-accent-300 font-medium'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'"
          @click="activeCategory = cat"
        >
          {{ __(cat) }}
          <span class="ml-1 text-xs opacity-60">{{ groups[cat]?.length || 0 }}</span>
        </button>
      </div>

      <!-- Grouped document list -->
      <div class="space-y-6">
        <div v-for="(docs, category) in visibleGroups" :key="category">
          <h2 class="flex items-center gap-2 text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">
            <component :is="categoryIcons[category] || FileText" class="w-4 h-4" />
            {{ __(category) }}
          </h2>

          <div class="space-y-2">
            <div
              v-for="doc in docs"
              :key="doc.file_url"
              class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
                     px-4 py-3 flex items-start gap-3 hover:border-gray-300 dark:hover:border-gray-600
                     transition-colors"
            >
              <component
                :is="fileIcon(doc.file_name)"
                class="w-5 h-5 text-gray-400 dark:text-gray-500 flex-shrink-0 mt-0.5"
              />
              <div class="flex-1 min-w-0">
                <a
                  :href="doc.file_url"
                  target="_blank"
                  class="text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-accent-600
                         dark:hover:text-accent-400 truncate block"
                >
                  {{ doc.repo_title || doc.file_name }}
                </a>
                <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {{ formatDate(doc.added) }}
                  <span v-if="doc.file_size" class="ml-1">· {{ formatSize(doc.file_size) }}</span>
                </div>
                <button
                  class="text-xs text-accent-600 dark:text-accent-400 hover:underline mt-1 inline-block"
                  @click="router.push(sourceRoute(doc.source_doctype, doc.source_name))"
                >
                  → {{ doc.source_doctype.replace('Home ', '') }}: {{ doc.source_label }}
                </button>

                <!-- Repo summary (soft integration) -->
                <details
                  v-if="doc.repo_summary"
                  class="mt-1.5"
                >
                  <summary class="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                    {{ __('Summary (via Repo)') }}
                  </summary>
                  <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 pl-2 border-l-2 border-gray-200 dark:border-gray-700">
                    {{ doc.repo_summary }}
                  </p>
                </details>

                <!-- Repo tags -->
                <div v-if="doc.repo_tags?.length" class="flex gap-1 mt-1.5">
                  <span
                    v-for="tag in doc.repo_tags"
                    :key="tag"
                    class="text-[10px] px-1.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700
                           text-gray-600 dark:text-gray-400"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty category state -->
          <div
            v-if="!docs?.length"
            class="text-sm text-gray-500 dark:text-gray-400 py-4 text-center"
          >
            {{ __('No documents in this category.') }}
            <button
              v-if="isAdultOrAbove"
              class="text-accent-600 dark:text-accent-400 hover:underline ml-1"
              @click="openUploadDialog"
            >
              {{ __('Add one') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload dialog overlay -->
    <div
      v-if="showUploadDialog"
      class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
      @click.self="showUploadDialog = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md">
        <!-- Dialog header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ __('Add Document') }}</h2>
          <button
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            @click="showUploadDialog = false"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Dialog body -->
        <div class="px-5 py-4 space-y-4">
          <!-- File drop zone -->
          <div
            class="border-2 border-dashed rounded-lg p-6 text-center transition-colors"
            :class="uploadFile
              ? 'border-accent-300 dark:border-accent-600 bg-accent-50 dark:bg-accent-900/10'
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'"
            @dragover.prevent
            @drop="onFileDrop"
          >
            <template v-if="uploadFile">
              <component :is="fileIcon(uploadFileName)" class="w-8 h-8 mx-auto mb-2 text-accent-500" />
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ uploadFileName }}</p>
              <button
                class="text-xs text-gray-500 dark:text-gray-400 hover:text-red-500 mt-1"
                @click="uploadFile = null; uploadFileName = ''"
              >
                {{ __('Remove') }}
              </button>
            </template>
            <template v-else>
              <Upload class="w-8 h-8 mx-auto mb-2 text-gray-400 dark:text-gray-500" />
              <label class="cursor-pointer">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {{ __('Drop file here or') }}
                  <span class="text-accent-600 dark:text-accent-400 hover:underline">{{ __('browse') }}</span>
                </span>
                <input type="file" class="hidden" @change="onFileSelected" />
              </label>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ __('Max 25 MB') }}</p>
            </template>
          </div>

          <!-- Link to -->
          <div>
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 block mb-1.5">
              {{ __('Link to') }}
            </label>

            <!-- DocType select -->
            <select
              v-model="selectedDoctype"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 mb-2"
            >
              <option value="" disabled>{{ __('Select type…') }}</option>
              <option
                v-for="target in linkTargets"
                :key="target.doctype"
                :value="target.doctype"
              >
                {{ __(target.label) }}
              </option>
            </select>

            <!-- Record select -->
            <select
              v-model="selectedRecord"
              :disabled="!selectedDoctype || !availableRecords.length"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="" disabled>{{ __('Select record…') }}</option>
              <option
                v-for="rec in availableRecords"
                :key="rec.name"
                :value="rec.name"
              >
                {{ rec.label }}
              </option>
            </select>
          </div>

          <!-- Error -->
          <p v-if="uploadError" class="text-sm text-red-600 dark:text-red-400">{{ uploadError }}</p>
        </div>

        <!-- Dialog footer -->
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-gray-200 dark:border-gray-700">
          <Button size="sm" variant="ghost" @click="showUploadDialog = false">
            {{ __('Cancel') }}
          </Button>
          <Button
            size="sm"
            variant="solid"
            :loading="uploading"
            :disabled="!uploadFile || !selectedDoctype || !selectedRecord"
            @click="submitUpload"
          >
            {{ __('Upload') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
