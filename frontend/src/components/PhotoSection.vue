<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Reusable photo section — embedded in property, room, item, and maintenance detail pages.
  Shows a thumbnail strip with upload capability. Links to full gallery for browse-all.
-->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest, useFileUpload } from 'frappe-ui'
import { Camera, Plus, X, ChevronRight } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{
  property: string
  room?: string
  item?: string
  maintenance?: string
  canEdit: boolean
  maxThumbnails?: number
}>()

const router = useRouter()
const fileUploader = useFileUpload()

interface Photo {
  name: string
  photo: string
  caption: string
  purpose: string
  photo_date: string
  before_after: string | null
  pair_ref: string | null
}

const photos = ref<Photo[]>([])
const loading = ref(true)
const uploading = ref(false)
const showUpload = ref(false)
const uploadFile = ref<File | null>(null)
const uploadPreview = ref('')
const uploadCaption = ref('')
const uploadPurpose = ref('General')
const lightboxPhoto = ref<Photo | null>(null)

const maxCount = computed(() => props.maxThumbnails ?? 6)
const visiblePhotos = computed(() => photos.value.slice(0, maxCount.value))
const hasMore = computed(() => photos.value.length > maxCount.value)

const purposes = ['General', 'Condition', 'Damage', 'Renovation', 'Move-in', 'Move-out']
const purposeColors: Record<string, string> = {
  General: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  Condition: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  Damage: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  Renovation: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  'Move-in': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  'Move-out': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
}

async function loadPhotos() {
  loading.value = true
  try {
    const params: Record<string, string> = { property: props.property }
    if (props.room) params.room = props.room
    if (props.item) params.item = props.item
    if (props.maintenance) params.maintenance = props.maintenance

    const res = await frappeRequest({
      url: '/api/method/home.api.photo.get_photos',
      params,
    })
    photos.value = res || []
  } catch {
    photos.value = []
  } finally {
    loading.value = false
  }
}

function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    alert(__('Image must be smaller than 10 MB'))
    input.value = ''
    return
  }
  uploadFile.value = file
  uploadPreview.value = URL.createObjectURL(file)
  showUpload.value = true
}

async function uploadPhoto() {
  if (!uploadFile.value) return
  uploading.value = true
  try {
    const uploadResult = await fileUploader.upload(uploadFile.value, {
      doctype: 'Home Property',
      docname: props.property,
      private: false,
    })

    const fileUrl = uploadResult?.file_url
    if (!fileUrl) throw new Error(__('Upload failed'))

    await frappeRequest({
      url: '/api/method/home.api.photo.create_photo',
      params: {
        property: props.property,
        photo: fileUrl,
        caption: uploadCaption.value || '',
        purpose: uploadPurpose.value,
        room: props.room || '',
        item: props.item || '',
        maintenance: props.maintenance || '',
      },
    })

    resetUpload()
    await loadPhotos()
  } catch (e: any) {
    alert(e.message || __('Failed to upload photo'))
  } finally {
    uploading.value = false
  }
}

function resetUpload() {
  showUpload.value = false
  uploadFile.value = null
  uploadPreview.value = ''
  uploadCaption.value = ''
  uploadPurpose.value = 'General'
}

function openLightbox(photo: Photo) {
  lightboxPhoto.value = photo
}

function goToGallery() {
  const query: Record<string, string> = {}
  if (props.room) query.room = props.room
  if (props.item) query.item = props.item
  if (props.maintenance) query.maintenance = props.maintenance
  router.push({ path: '/home/photos', query })
}

watch(() => [props.property, props.room, props.item, props.maintenance], () => {
  if (props.property) loadPhotos()
})

onMounted(() => {
  if (props.property) loadPhotos()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-h4 text-gray-800 dark:text-gray-200">{{ __('Photos') }}</h2>
      <div class="flex items-center gap-2">
        <label v-if="canEdit" class="cursor-pointer">
          <span
            class="flex items-center gap-1 px-2 py-1 text-xs text-accent-600 dark:text-accent-400
                   hover:bg-accent-50 dark:hover:bg-accent-900/20 rounded-lg transition-colors"
          >
            <Plus class="w-3.5 h-3.5" />
            {{ __('Add') }}
          </span>
          <input type="file" accept="image/*" class="hidden" @change="onFileSelected" />
        </label>
        <button
          v-if="photos.length"
          class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400
                 hover:text-gray-700 dark:hover:text-gray-300"
          @click="goToGallery"
        >
          {{ __('View all') }}
          <ChevronRight class="w-3 h-3" />
        </button>
      </div>
    </div>

    <!-- Inline upload form -->
    <div
      v-if="showUpload"
      class="bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700
             p-3 mb-3 space-y-2"
    >
      <img
        v-if="uploadPreview"
        :src="uploadPreview"
        class="w-full max-h-40 object-contain rounded-lg bg-gray-100 dark:bg-gray-900"
      />
      <input
        v-model="uploadCaption"
        type="text"
        :placeholder="__('Caption (optional)')"
        class="w-full border border-gray-300 dark:border-gray-600 rounded px-2 py-1.5 text-xs
               bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
      />
      <select
        v-model="uploadPurpose"
        class="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-xs
               bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
      >
        <option v-for="p in purposes" :key="p" :value="p">{{ __(p) }}</option>
      </select>
      <div class="flex gap-2">
        <Button size="sm" variant="solid" :loading="uploading" :disabled="!uploadFile" @click="uploadPhoto">
          {{ __('Upload') }}
        </Button>
        <Button size="sm" variant="ghost" @click="resetUpload">
          {{ __('Cancel') }}
        </Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-xs text-gray-400 dark:text-gray-500">{{ __('Loading…') }}</div>

    <!-- Empty state -->
    <div
      v-else-if="!photos.length && !showUpload"
      class="text-center py-6 text-gray-400 dark:text-gray-500"
    >
      <Camera class="w-6 h-6 mx-auto mb-1.5" />
      <p class="text-xs">{{ __('No photos yet') }}</p>
    </div>

    <!-- Thumbnail strip -->
    <div v-else class="flex gap-2 overflow-x-auto pb-1">
      <div
        v-for="photo in visiblePhotos"
        :key="photo.name"
        class="relative flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800
               cursor-pointer group"
        @click="openLightbox(photo)"
      >
        <img
          :src="photo.photo"
          :alt="photo.caption || __('Photo')"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
        />
        <span
          class="absolute bottom-0.5 left-0.5 text-[9px] px-1 py-0.5 rounded"
          :class="purposeColors[photo.purpose] || purposeColors.General"
        >
          {{ __(photo.purpose) }}
        </span>
      </div>

      <!-- "More" tile -->
      <button
        v-if="hasMore"
        class="flex-shrink-0 w-20 h-20 rounded-lg bg-gray-100 dark:bg-gray-800
               flex items-center justify-center text-xs text-gray-500 dark:text-gray-400
               hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        @click="goToGallery"
      >
        +{{ photos.length - maxCount }}
      </button>
    </div>

    <!-- Lightbox -->
    <div
      v-if="lightboxPhoto"
      class="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
      @click.self="lightboxPhoto = null"
    >
      <button
        class="absolute top-4 right-4 text-white/70 hover:text-white"
        @click="lightboxPhoto = null"
      >
        <X class="w-6 h-6" />
      </button>
      <div class="max-w-3xl w-full">
        <img
          :src="lightboxPhoto.photo"
          :alt="lightboxPhoto.caption"
          class="max-h-[80vh] mx-auto rounded-lg"
        />
        <div class="text-center mt-3">
          <p v-if="lightboxPhoto.caption" class="text-white text-sm">{{ lightboxPhoto.caption }}</p>
          <p class="text-white/60 text-xs mt-1">
            {{ lightboxPhoto.photo_date }}
            <span
              class="ml-2 px-1.5 py-0.5 rounded-full text-xs"
              :class="purposeColors[lightboxPhoto.purpose] || purposeColors.General"
            >
              {{ __(lightboxPhoto.purpose) }}
            </span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
