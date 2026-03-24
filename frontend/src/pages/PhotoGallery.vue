<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Photo gallery — property, room, and item photos with timeline (Feature 59).
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { frappeRequest, useFileUpload } from 'frappe-ui'
import {
  ArrowLeft, Camera, Plus, X, Image as ImageIcon,
  ArrowLeftRight,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useProperty } from '@/composables/useProperty'
import { useHouseholdRole } from '@/composables/useHouseholdRole'

const router = useRouter()
const route = useRoute()
const { propertyName, load: loadPropertyName } = useProperty()
const { isAdultOrAbove, load: loadRole } = useHouseholdRole()
const fileUploader = useFileUpload()

interface Photo {
  name: string
  photo: string
  caption: string
  purpose: string
  photo_date: string
  room: string | null
  item: string | null
  before_after: string | null
  pair_ref: string | null
}

const photos = ref<Photo[]>([])
const loading = ref(true)
const filter = ref('All')
const lightboxPhoto = ref<Photo | null>(null)

// Upload state
const showUpload = ref(false)
const uploadFile = ref<File | null>(null)
const uploadPreview = ref('')
const uploadCaption = ref('')
const uploadPurpose = ref('General')
const uploadBeforeAfter = ref('')
const uploadPairRef = ref('')
const uploading = ref(false)

// Unpaired photos for pairing picker
const unpairedPhotos = ref<Photo[]>([])
const loadingUnpaired = ref(false)

const purposes = ['All', 'General', 'Condition', 'Damage', 'Renovation', 'Move-in', 'Move-out']
const purposeColors: Record<string, string> = {
  General: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  Condition: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  Damage: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  Renovation: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  'Move-in': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  'Move-out': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
}

function formatDate(d: string): string {
  if (!d) return ''
  return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

// Query param filters from detail pages (e.g. ?room=ROOM-001&item=ITEM-001)
const queryRoom = computed(() => (route.query.room as string) || '')
const queryItem = computed(() => (route.query.item as string) || '')
const queryMaintenance = computed(() => (route.query.maintenance as string) || '')
const contextLabel = computed(() => {
  if (queryItem.value) return __('for this item')
  if (queryMaintenance.value) return __('for this task')
  if (queryRoom.value) return __('for this room')
  return ''
})

async function loadPhotos() {
  loading.value = true
  try {
    const propName = await loadPropertyName()
    const params: Record<string, string> = { property: propName }
    if (queryRoom.value) params.room = queryRoom.value
    if (queryItem.value) params.item = queryItem.value
    if (queryMaintenance.value) params.maintenance = queryMaintenance.value

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

const filteredPhotos = computed(() => {
  if (filter.value === 'All') return photos.value
  return photos.value.filter(p => p.purpose === filter.value)
})

async function loadUnpairedPhotos() {
  if (uploadPurpose.value !== 'Renovation' || !uploadBeforeAfter.value) {
    unpairedPhotos.value = []
    return
  }
  loadingUnpaired.value = true
  try {
    const propName = await loadPropertyName()
    // If uploading "After", fetch unpaired "Before" photos (and vice versa)
    const opposite = uploadBeforeAfter.value === 'After' ? 'Before' : 'After'
    const res = await frappeRequest({
      url: '/api/method/home.api.photo.get_unpaired_photos',
      params: { property: propName, before_after: opposite },
    })
    unpairedPhotos.value = res || []
    // Auto-select the most recent one
    uploadPairRef.value = unpairedPhotos.value.length ? unpairedPhotos.value[0].name : ''
  } catch {
    unpairedPhotos.value = []
  } finally {
    loadingUnpaired.value = false
  }
}

function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploadFile.value = file
  uploadPreview.value = URL.createObjectURL(file)
}

async function uploadPhoto() {
  if (!uploadFile.value) return
  uploading.value = true
  try {
    const propName = await loadPropertyName()

    // Upload file using FrappeUI's upload utility
    const uploadResult = await fileUploader.upload(uploadFile.value, {
      doctype: 'Home Property',
      docname: propName,
      private: false,
    })

    const fileUrl = uploadResult?.file_url
    if (!fileUrl) throw new Error(__('Upload failed'))

    // Create Home Photo record via proper API
    await frappeRequest({
      url: '/api/method/home.api.photo.create_photo',
      params: {
        property: propName,
        photo: fileUrl,
        caption: uploadCaption.value || '',
        purpose: uploadPurpose.value,
        before_after: uploadPurpose.value === 'Renovation' ? uploadBeforeAfter.value : '',
        pair_ref: uploadPurpose.value === 'Renovation' ? uploadPairRef.value : '',
        room: queryRoom.value,
        item: queryItem.value,
        maintenance: queryMaintenance.value,
      },
    })

    // Reset form
    showUpload.value = false
    uploadFile.value = null
    uploadPreview.value = ''
    uploadCaption.value = ''
    uploadPurpose.value = 'General'
    uploadBeforeAfter.value = ''
    uploadPairRef.value = ''
    unpairedPhotos.value = []
    await loadPhotos()
  } catch (e: any) {
    alert(e.message || __('Failed to upload photo'))
  } finally {
    uploading.value = false
  }
}

function openLightbox(photo: Photo) {
  lightboxPhoto.value = photo
}

function closeLightbox() {
  lightboxPhoto.value = null
}

function getPairedPhoto(pairRef: string | null): Photo | null {
  if (!pairRef) return null
  return photos.value.find(p => p.name === pairRef) || null
}

onMounted(() => {
  loadRole()
  loadPhotos()
})
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <button
      class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400
             hover:text-gray-700 dark:hover:text-gray-300 mb-4"
      @click="router.push('/home')"
    >
      <ArrowLeft class="w-4 h-4" />
      {{ __('My Home') }}
    </button>

    <div class="flex items-center justify-between mb-4">
      <div>
        <h1 class="text-h1 text-gray-900 dark:text-gray-100">{{ __('Photos') }}</h1>
        <p v-if="contextLabel" class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          {{ contextLabel }}
          <button
            class="text-accent-600 dark:text-accent-400 hover:underline ml-1"
            @click="router.push('/home/photos')"
          >{{ __('Show all') }}</button>
        </p>
      </div>
      <Button v-if="isAdultOrAbove" variant="solid" @click="showUpload = true">
        <template #prefix><Plus class="w-4 h-4" /></template>
        {{ __('Add Photo') }}
      </Button>
    </div>

    <!-- Purpose filter -->
    <div class="flex flex-wrap gap-1.5 mb-6">
      <button
        v-for="p in purposes"
        :key="p"
        class="px-3 py-1 text-xs rounded-full transition-colors"
        :class="filter === p
          ? 'bg-accent-500 text-white'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'"
        @click="filter = p"
      >
        {{ __(p) }}
      </button>
    </div>

    <!-- Upload form -->
    <div v-if="showUpload" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6 space-y-3">
      <div v-if="!uploadPreview" class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
        <Camera class="w-8 h-8 mx-auto mb-2 text-gray-400" />
        <label class="cursor-pointer text-sm text-accent-600 dark:text-accent-400 hover:underline">
          {{ __('Choose photo') }}
          <input type="file" accept="image/*" class="hidden" @change="onFileSelected" />
        </label>
      </div>
      <div v-else>
        <img :src="uploadPreview" class="w-full max-h-64 object-contain rounded-lg bg-gray-100 dark:bg-gray-900" />
      </div>
      <input
        v-model="uploadCaption"
        type="text"
        :placeholder="__('Caption (optional)')"
        class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
               bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
      />
      <div class="flex gap-2">
        <select
          v-model="uploadPurpose"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1.5 text-sm
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        >
          <option v-for="p in purposes.slice(1)" :key="p" :value="p">{{ __(p) }}</option>
        </select>
        <select
          v-if="uploadPurpose === 'Renovation'"
          v-model="uploadBeforeAfter"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1.5 text-sm
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          @change="loadUnpairedPhotos"
        >
          <option value="">{{ __('Select…') }}</option>
          <option value="Before">{{ __('Before') }}</option>
          <option value="After">{{ __('After') }}</option>
        </select>
      </div>
      <!-- Pair picker: show unpaired opposite photos -->
      <div v-if="uploadPurpose === 'Renovation' && uploadBeforeAfter && unpairedPhotos.length" class="space-y-1.5">
        <label class="text-xs text-gray-500 dark:text-gray-400">
          {{ __('Pair with {0} photo:', [uploadBeforeAfter === 'After' ? __('Before') : __('After')]) }}
        </label>
        <div class="flex gap-2 overflow-x-auto pb-1">
          <button
            v-for="up in unpairedPhotos"
            :key="up.name"
            type="button"
            class="relative flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-colors"
            :class="uploadPairRef === up.name
              ? 'border-accent-500'
              : 'border-gray-200 dark:border-gray-600 hover:border-gray-400'"
            @click="uploadPairRef = uploadPairRef === up.name ? '' : up.name"
          >
            <img :src="up.photo" class="w-full h-full object-cover" />
          </button>
        </div>
      </div>
      <div class="flex gap-2">
        <Button variant="solid" :loading="uploading" :disabled="!uploadFile" @click="uploadPhoto">
          {{ __('Upload') }}
        </Button>
        <Button variant="ghost" @click="showUpload = false; uploadFile = null; uploadPreview = ''">
          {{ __('Cancel') }}
        </Button>
      </div>
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">{{ __('Loading…') }}</div>

    <div v-else-if="!photos.length" class="text-center py-12">
      <Camera class="w-10 h-10 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">{{ __('No photos yet') }}</h2>
      <p class="text-body text-gray-500 dark:text-gray-400">
        {{ __('Capture move-in photos, renovation before/after, and damage documentation.') }}
      </p>
    </div>

    <!-- Photo grid -->
    <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-3">
      <div
        v-for="photo in filteredPhotos"
        :key="photo.name"
        class="group relative aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800 cursor-pointer"
        @click="openLightbox(photo)"
      >
        <img
          :src="photo.photo"
          :alt="photo.caption || __('Photo')"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
        />
        <!-- Overlay -->
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent
                    opacity-0 group-hover:opacity-100 transition-opacity">
          <div class="absolute bottom-0 left-0 right-0 p-2">
            <span v-if="photo.caption" class="text-xs text-white block truncate">
              {{ photo.caption }}
            </span>
            <span class="text-xs text-white/70">{{ formatDate(photo.photo_date) }}</span>
          </div>
        </div>
        <!-- Purpose badge -->
        <span
          class="absolute top-2 left-2 text-xs px-1.5 py-0.5 rounded-full"
          :class="purposeColors[photo.purpose] || purposeColors.General"
        >
          {{ __(photo.purpose) }}
        </span>
        <!-- Before/After badge -->
        <span
          v-if="photo.before_after"
          class="absolute top-2 right-2 text-xs px-1.5 py-0.5 rounded-full bg-black/50 text-white flex items-center gap-1"
        >
          {{ __(photo.before_after) }}
          <ArrowLeftRight v-if="photo.pair_ref" class="w-3 h-3" />
        </span>
      </div>
    </div>

    <!-- Lightbox -->
    <div
      v-if="lightboxPhoto"
      class="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
      @click.self="closeLightbox"
    >
      <button
        class="absolute top-4 right-4 text-white/70 hover:text-white"
        @click="closeLightbox"
      >
        <X class="w-6 h-6" />
      </button>

      <div class="max-w-4xl w-full">
        <!-- Before/After side by side -->
        <div
          v-if="lightboxPhoto.pair_ref && getPairedPhoto(lightboxPhoto.pair_ref)"
          class="grid grid-cols-2 gap-4"
        >
          <div>
            <img
              :src="lightboxPhoto.before_after === 'Before' ? lightboxPhoto.photo : getPairedPhoto(lightboxPhoto.pair_ref)!.photo"
              class="w-full rounded-lg"
            />
            <span class="text-white/70 text-sm mt-1 block text-center">{{ __('Before') }}</span>
          </div>
          <div>
            <img
              :src="lightboxPhoto.before_after === 'After' ? lightboxPhoto.photo : getPairedPhoto(lightboxPhoto.pair_ref)!.photo"
              class="w-full rounded-lg"
            />
            <span class="text-white/70 text-sm mt-1 block text-center">{{ __('After') }}</span>
          </div>
        </div>
        <!-- Single photo -->
        <img
          v-else
          :src="lightboxPhoto.photo"
          :alt="lightboxPhoto.caption"
          class="max-h-[80vh] mx-auto rounded-lg"
        />

        <div class="text-center mt-3">
          <p v-if="lightboxPhoto.caption" class="text-white text-sm">{{ lightboxPhoto.caption }}</p>
          <p class="text-white/60 text-xs mt-1">
            {{ formatDate(lightboxPhoto.photo_date) }}
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
