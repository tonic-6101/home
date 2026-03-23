<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { __ } from '@/composables/useTranslate'
import { useBarcodeScanner } from '@/composables/useBarcodeScanner'
import ScanConfirmationDialog from '@/components/ScanConfirmationDialog.vue'
import type { ScanResult, ConfirmedResult } from '@/components/ScanConfirmationDialog.vue'

type Step = 'choice' | 'camera_ocr' | 'camera_barcode' | 'confirming' | 'recall_warning' | 'saving'

const route = useRoute()
const router = useRouter()
const propertyName = computed(() => route.query.property as string || '')

const step = ref<Step>('choice')
const scanResult = ref<ScanResult | null>(null)
const confirmedData = ref<ConfirmedResult | null>(null)
const imagePreview = ref<string>('')
const lifespanYears = ref<number | null>(null)
const recallInfo = ref<{ title: string; url: string } | null>(null)
const loading = ref(false)
const errorMessage = ref('')

// Camera refs
const videoRef = ref<HTMLVideoElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
let mediaStream: MediaStream | null = null

const { isScanning, error: scannerError, startScanning, stopScanning } = useBarcodeScanner()

// --- OCR flow ---

function startOcrScan(): void {
  step.value = 'camera_ocr'
  errorMessage.value = ''
  nextTick(() => {
    fileInputRef.value?.click()
  })
}

function onImageCaptured(event: Event): void {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) {
    step.value = 'choice'
    return
  }

  loading.value = true
  errorMessage.value = ''

  const reader = new FileReader()
  reader.onload = async () => {
    const dataUrl = reader.result as string
    imagePreview.value = dataUrl
    const b64 = dataUrl.split(',')[1]

    try {
      const result = await extractFromImage.submit({ image_b64: b64, property: propertyName.value })
      if (result.brand || result.model || result.serial_number) {
        scanResult.value = result as ScanResult
        lifespanYears.value = null
        step.value = 'confirming'
      } else {
        errorMessage.value = __('We couldn\'t read the label — enter details manually')
        step.value = 'choice'
      }
    } catch {
      errorMessage.value = __('We couldn\'t read the label — enter details manually')
      step.value = 'choice'
    } finally {
      loading.value = false
    }
  }
  reader.readAsDataURL(file)
}

const extractFromImage = createResource({
  url: 'home.api.item.extract_from_image',
  makeParams: (params: { image_b64: string; property: string }) => params,
})

// --- Barcode flow ---

async function startBarcodeScan(): Promise<void> {
  step.value = 'camera_barcode'
  errorMessage.value = ''

  await nextTick()
  if (!videoRef.value) return

  startScanning(videoRef.value, async (result) => {
    loading.value = true
    try {
      const lookupResult = await lookupBarcode.submit({
        barcode: result.text,
        property: propertyName.value,
      })
      if (lookupResult.found) {
        scanResult.value = {
          brand: lookupResult.brand || '',
          model: lookupResult.model || '',
          serial_number: '',
          category: lookupResult.category || '',
          confidence: {
            brand: lookupResult.brand ? 'high' : 'low',
            model: lookupResult.model ? 'high' : 'low',
            serial_number: 'low',
            category: 'low',
          },
          method: 'barcode',
        }
        lifespanYears.value = null
        imagePreview.value = ''
        step.value = 'confirming'
      } else {
        errorMessage.value = __('Product not found — enter details manually')
        step.value = 'choice'
      }
    } catch {
      errorMessage.value = __('Product not found — enter details manually')
      step.value = 'choice'
    } finally {
      loading.value = false
      stopCamera()
    }
  })
}

const lookupBarcode = createResource({
  url: 'home.api.item.lookup_barcode',
  makeParams: (params: { barcode: string; property: string }) => params,
})

// --- Recall check + confirm ---

async function onConfirmed(data: ConfirmedResult): Promise<void> {
  confirmedData.value = data
  loading.value = true

  try {
    const result = await checkRecall.submit({ brand: data.brand, model: data.model })
    if (result.recall_found) {
      recallInfo.value = { title: result.title, url: result.url }
      step.value = 'recall_warning'
      loading.value = false
      return
    }
  } catch {
    // Recall check failure is silent
  }

  await saveAppliance(data)
}

const checkRecall = createResource({
  url: 'home.api.item.check_recall',
  makeParams: (params: { brand: string; model: string }) => params,
})

async function saveAppliance(data: ConfirmedResult): Promise<void> {
  step.value = 'saving'
  loading.value = true

  try {
    // Build recalls child table if a recall was found at registration
    const recalls: Record<string, any>[] = []
    if (recallInfo.value) {
      recalls.push({
        recall_id: `scan-${Date.now()}`,
        title: recallInfo.value.title,
        brand: data.brand,
        category: data.category,
        severity: 'Unknown',
        detail_url: recallInfo.value.url,
        dismissed: 0,
      })
    }

    const doc = await createApplianceResource.submit({
      doc: {
        doctype: 'Home Item',
        item_name: `${data.brand} ${data.model}`.trim() || __('New Appliance'),
        item_type: 'Appliance',
        property: propertyName.value,
        brand: data.brand,
        model: data.model,
        serial_number: data.serial_number,
        category: data.category || 'Other',
        status: 'Working',
        expected_lifespan_years: data.expected_lifespan_years,
        recalls,
      },
    })
    router.push(`/home/items/${doc.name}`)
  } catch (e: any) {
    errorMessage.value = e.message || __('Failed to save item')
    step.value = 'choice'
    loading.value = false
  }
}

const createApplianceResource = createResource({
  url: 'frappe.client.insert',
  makeParams: (params: { doc: Record<string, any> }) => params,
})

function continueAfterRecall(): void {
  if (confirmedData.value) {
    saveAppliance(confirmedData.value)
  }
}

// --- Navigation ---

function retry(): void {
  scanResult.value = null
  confirmedData.value = null
  imagePreview.value = ''
  errorMessage.value = ''
  step.value = 'choice'
}

function goManual(): void {
  const query: Record<string, string> = { property: propertyName.value }
  if (scanResult.value) {
    if (scanResult.value.brand) query.brand = scanResult.value.brand
    if (scanResult.value.model) query.model = scanResult.value.model
  }
  router.push({ path: '/home/items/new', query })
}

function stopCamera(): void {
  stopScanning()
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null
  }
}

function goBack(): void {
  stopCamera()
  step.value = 'choice'
}
</script>

<template>
  <div class="p-6 max-w-lg mx-auto min-h-[60vh] flex flex-col">
    <!-- Error banner -->
    <div
      v-if="errorMessage"
      class="mb-4 px-4 py-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg text-sm text-amber-800 dark:text-amber-300"
    >
      {{ errorMessage }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin w-8 h-8 border-2 border-home-500 border-t-transparent rounded-full mx-auto mb-3" />
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ __('Processing...') }}</p>
      </div>
    </div>

    <!-- Step: Choice -->
    <template v-else-if="step === 'choice'">
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
        {{ __('Scan to Register') }}
      </h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
        {{ __('Speed up registration by scanning the appliance label or product barcode.') }}
      </p>

      <div class="space-y-3 flex-1">
        <button
          class="w-full flex items-center gap-4 p-4 border border-gray-200 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left"
          @click="startOcrScan"
        >
          <div class="w-12 h-12 bg-home-50 dark:bg-home-900/20 rounded-lg flex items-center justify-center text-2xl">
            📷
          </div>
          <div>
            <div class="font-medium text-gray-900 dark:text-gray-100">{{ __('Scan rating plate') }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">{{ __('Photograph the label on your appliance') }}</div>
          </div>
        </button>

        <button
          class="w-full flex items-center gap-4 p-4 border border-gray-200 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left"
          @click="startBarcodeScan"
        >
          <div class="w-12 h-12 bg-home-50 dark:bg-home-900/20 rounded-lg flex items-center justify-center text-2xl">
            📦
          </div>
          <div>
            <div class="font-medium text-gray-900 dark:text-gray-100">{{ __('Scan product barcode') }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">{{ __('Point at the barcode on the box') }}</div>
          </div>
        </button>
      </div>

      <button
        class="mt-6 w-full text-center text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
        @click="goManual"
      >
        {{ __('Skip — enter details manually') }}
      </button>
    </template>

    <!-- Step: Camera (barcode) -->
    <template v-else-if="step === 'camera_barcode'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {{ __('Scan Barcode') }}
        </h2>
        <button class="text-sm text-gray-500 hover:text-gray-700" @click="goBack">
          {{ __('Cancel') }}
        </button>
      </div>
      <div class="relative rounded-xl overflow-hidden bg-black aspect-[4/3]">
        <video ref="videoRef" class="w-full h-full object-cover" autoplay playsinline muted />
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="w-48 h-32 border-2 border-white/50 rounded-lg" />
        </div>
      </div>
      <p class="mt-3 text-center text-sm text-gray-500 dark:text-gray-400">
        {{ __('Point the camera at the EAN/UPC barcode') }}
      </p>
    </template>

    <!-- Step: Camera (OCR) — hidden file input -->
    <template v-else-if="step === 'camera_ocr'">
      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        capture="environment"
        class="hidden"
        @change="onImageCaptured"
        @cancel="step = 'choice'"
      />
      <div class="flex-1 flex items-center justify-center">
        <p class="text-sm text-gray-500">{{ __('Opening camera...') }}</p>
      </div>
    </template>

    <!-- Step: Confirmation -->
    <template v-else-if="step === 'confirming' && scanResult">
      <ScanConfirmationDialog
        :result="scanResult"
        :lifespan-years="lifespanYears"
        :image-preview="imagePreview"
        @confirm="onConfirmed"
        @retry="retry"
        @manual="goManual"
      />
    </template>

    <!-- Step: Recall warning -->
    <template v-else-if="step === 'recall_warning' && recallInfo">
      <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-300 dark:border-amber-700 rounded-xl p-6">
        <div class="flex items-start gap-3">
          <span class="text-2xl">⚠</span>
          <div>
            <h3 class="font-semibold text-amber-900 dark:text-amber-200">
              {{ __('Safety recall found') }}
            </h3>
            <p class="mt-1 text-sm text-amber-800 dark:text-amber-300">
              {{ recallInfo.title }}
            </p>
            <div class="mt-4 flex gap-2">
              <a
                v-if="recallInfo.url"
                :href="recallInfo.url"
                target="_blank"
                rel="noopener noreferrer"
                class="px-4 py-2 border border-amber-400 text-amber-800 dark:text-amber-200 rounded-lg text-sm hover:bg-amber-100 dark:hover:bg-amber-800/30"
              >
                {{ __('View recall') }}
              </a>
              <button
                class="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm hover:bg-amber-700"
                @click="continueAfterRecall"
              >
                {{ __('Continue anyway') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Step: Saving -->
    <template v-else-if="step === 'saving'">
      <div class="flex-1 flex items-center justify-center">
        <p class="text-sm text-gray-500">{{ __('Saving item...') }}</p>
      </div>
    </template>
  </div>
</template>
