<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Room card grid — lives on the property detail page (Feature 3).
  Includes add room, delete room, drag-to-reorder, and room suggestions.
-->
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import {
  ChefHat, Bed, Bath, Sofa, CarFront, Package, DoorOpen,
  HelpCircle, Plus, GripVertical, MoreVertical, Pencil, Trash2,
  HardHat,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import AddRoomDialog from '@/components/AddRoomDialog.vue'
import DeleteRoomDialog from '@/components/DeleteRoomDialog.vue'

interface Room {
  name: string
  room_name: string
  room_type: string
  area_sqm: number | null
  sort_order: number
  notes: string | null
  item_count: number
  open_task_count: number
}

const props = defineProps<{
  property: string
  propertyType: string
  isOwner: boolean
  isArchived: boolean
}>()

const router = useRouter()

const rooms = ref<Room[]>([])
const unassignedCounts = ref({ item_count: 0 })
const loading = ref(true)
const showAddDialog = ref(false)
const showDeleteDialog = ref(false)
const deleteTarget = ref<Room | null>(null)
const editingRoom = ref<string | null>(null)
const editName = ref('')
const menuOpenRoom = ref<string | null>(null)
const showSuggestions = ref(false)
const suggestions = ref<{ room_name: string; room_type: string }[]>([])
const selectedSuggestions = ref<Set<number>>(new Set())

// Drag state
const draggedIndex = ref<number | null>(null)

const roomTypeIcons: Record<string, Component> = {
  Kitchen: ChefHat,
  Bedroom: Bed,
  Bathroom: Bath,
  'Living Room': Sofa,
  Garage: CarFront,
  Storage: Package,
  Other: DoorOpen,
}

function getRoomIcon(roomType: string): Component {
  return roomTypeIcons[roomType] || DoorOpen
}

const hasUnassigned = computed(() =>
  unassignedCounts.value.item_count > 0
)
const unassignedTotal = computed(() =>
  unassignedCounts.value.item_count
)

// ── Data loading ──

async function loadRooms() {
  loading.value = true
  try {
    const [roomsRes, unassignedRes] = await Promise.all([
      frappeRequest({
        url: '/api/method/home.api.room.get_rooms',
        params: { property: props.property },
      }),
      frappeRequest({
        url: '/api/method/home.api.room.get_unassigned_counts',
        params: { property: props.property },
      }),
    ])
    rooms.value = roomsRes || []
    unassignedCounts.value = unassignedRes || { item_count: 0 }

    // Show suggestions on first load if no rooms exist
    if (rooms.value.length === 0 && !props.isArchived) {
      await loadSuggestions()
    }
  } catch {
    rooms.value = []
  } finally {
    loading.value = false
  }
}

async function loadSuggestions() {
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.room.suggest_rooms',
      params: { property_type: props.propertyType },
    })
    const list = res || []
    if (list.length) {
      suggestions.value = list
      selectedSuggestions.value = new Set(list.map((_: any, i: number) => i))
      showSuggestions.value = true
    }
  } catch {
    // Silently skip suggestions
  }
}

async function acceptSuggestions() {
  for (const idx of selectedSuggestions.value) {
    const s = suggestions.value[idx]
    await frappeRequest({
      url: '/api/method/home.api.room.create_room',
      params: {
        property: props.property,
        room_name: s.room_name,
        room_type: s.room_type,
      },
    })
  }
  showSuggestions.value = false
  await loadRooms()
}

function toggleSuggestion(idx: number) {
  const s = new Set(selectedSuggestions.value)
  if (s.has(idx)) {
    s.delete(idx)
  } else {
    s.add(idx)
  }
  selectedSuggestions.value = s
}

// ── Room CRUD ──

async function onRoomCreated() {
  showAddDialog.value = false
  await loadRooms()
}

function startRename(room: Room) {
  editingRoom.value = room.name
  editName.value = room.room_name
  menuOpenRoom.value = null
}

async function saveRename(roomName: string) {
  if (!editName.value.trim()) return
  try {
    await frappeRequest({
      url: '/api/method/home.api.room.update_room',
      params: { name: roomName, room_name: editName.value.trim() },
    })
    editingRoom.value = null
    await loadRooms()
  } catch (e: any) {
    alert(e.message || __('Failed to rename'))
  }
}

function startDelete(room: Room) {
  deleteTarget.value = room
  showDeleteDialog.value = true
  menuOpenRoom.value = null
}

async function onRoomDeleted() {
  showDeleteDialog.value = false
  deleteTarget.value = null
  await loadRooms()
}

// ── Drag to reorder ──

function onDragStart(idx: number) {
  draggedIndex.value = idx
}

function onDragOver(e: DragEvent, idx: number) {
  e.preventDefault()
  if (draggedIndex.value === null || draggedIndex.value === idx) return

  const reordered = [...rooms.value]
  const [dragged] = reordered.splice(draggedIndex.value, 1)
  reordered.splice(idx, 0, dragged)
  rooms.value = reordered
  draggedIndex.value = idx
}

async function onDragEnd() {
  draggedIndex.value = null
  try {
    await frappeRequest({
      url: '/api/method/home.api.room.reorder_rooms',
      params: {
        property: props.property,
        order: JSON.stringify(rooms.value.map(r => r.name)),
      },
    })
  } catch (e: any) {
    alert(e.message || __('Failed to reorder'))
    await loadRooms()
  }
}

function navigateToRoom(room: Room) {
  if (editingRoom.value || menuOpenRoom.value) return
  router.push({ path: '/home/items', query: { room: room.name, room_name: room.room_name } })
}

function navigateToUnassigned() {
  router.push({ path: '/home/items', query: { room: 'unassigned' } })
}

function onClickOutside(e: MouseEvent) {
  if (menuOpenRoom.value) {
    menuOpenRoom.value = null
  }
}

onMounted(() => {
  loadRooms()
  document.addEventListener('click', onClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-h3 text-gray-800 dark:text-gray-200">{{ __('Rooms') }}</h2>
    </div>

    <!-- Suggestions prompt -->
    <div
      v-if="showSuggestions && suggestions.length"
      class="mb-4 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg"
    >
      <p class="text-sm text-amber-800 dark:text-amber-200 mb-3">
        {{ __('Add common rooms for your property?') }}
      </p>
      <div class="flex flex-wrap gap-2 mb-3">
        <label
          v-for="(s, idx) in suggestions"
          :key="idx"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm cursor-pointer transition-colors"
          :class="selectedSuggestions.has(idx)
            ? 'bg-amber-200 dark:bg-amber-800 text-amber-900 dark:text-amber-100'
            : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600'"
        >
          <input
            type="checkbox"
            :checked="selectedSuggestions.has(idx)"
            class="sr-only"
            @change="toggleSuggestion(idx)"
          />
          <component :is="getRoomIcon(s.room_type)" class="w-3.5 h-3.5" />
          {{ __(s.room_name) }}
        </label>
      </div>
      <div class="flex gap-2">
        <Button variant="solid" size="sm" @click="acceptSuggestions">
          {{ __('Add selected') }}
        </Button>
        <Button variant="outline" size="sm" @click="showSuggestions = false">
          {{ __('Skip') }}
        </Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 dark:text-gray-400 text-sm">
      {{ __('Loading rooms…') }}
    </div>

    <!-- Room cards -->
    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      <div
        v-for="(room, idx) in rooms"
        :key="room.name"
        class="relative p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
               hover:shadow-sm hover:border-accent-300 dark:hover:border-accent-600 transition-all cursor-pointer group"
        :draggable="isOwner && !isArchived"
        @click="navigateToRoom(room)"
        @dragstart="onDragStart(idx)"
        @dragover="onDragOver($event, idx)"
        @dragend="onDragEnd"
      >
        <!-- Drag handle -->
        <div
          v-if="isOwner && !isArchived"
          class="absolute top-2 left-2 text-gray-300 dark:text-gray-600 cursor-grab
                 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <GripVertical class="w-4 h-4" />
        </div>

        <!-- Three-dot menu -->
        <div
          v-if="isOwner && !isArchived"
          class="absolute top-2 right-2"
        >
          <button
            @click.stop="menuOpenRoom = menuOpenRoom === room.name ? null : room.name"
            class="w-6 h-6 flex items-center justify-center rounded text-gray-400
                   hover:text-gray-600 dark:hover:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <MoreVertical class="w-3.5 h-3.5" />
          </button>
          <div
            v-if="menuOpenRoom === room.name"
            class="absolute right-0 mt-1 w-36 rounded-lg shadow-lg border
                   border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 py-1 z-10"
          >
            <button
              @click="startRename(room)"
              class="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300
                     hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <Pencil class="w-3.5 h-3.5" />
              {{ __('Rename') }}
            </button>
            <button
              @click="startDelete(room)"
              class="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-red-600 dark:text-red-400
                     hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <Trash2 class="w-3.5 h-3.5" />
              {{ __('Delete') }}
            </button>
          </div>
        </div>

        <!-- Room content -->
        <div class="flex flex-col items-center text-center pt-2">
          <component
            :is="getRoomIcon(room.room_type)"
            class="w-8 h-8 text-gray-400 dark:text-gray-500 mb-2"
          />

          <!-- Inline rename -->
          <template v-if="editingRoom === room.name">
            <input
              v-model="editName"
              type="text"
              class="w-full text-center text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              @keyup.enter="saveRename(room.name)"
              @keyup.escape="editingRoom = null"
            />
            <div class="flex gap-1 mt-1">
              <button
                @click="saveRename(room.name)"
                class="text-xs text-accent-600 dark:text-accent-400 hover:underline"
              >{{ __('Save') }}</button>
              <button
                @click="editingRoom = null"
                class="text-xs text-gray-400 hover:underline"
              >{{ __('Cancel') }}</button>
            </div>
          </template>
          <template v-else>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate w-full">
              {{ room.room_name }}
            </span>
          </template>

          <!-- Counts -->
          <div class="flex items-center gap-3 mt-2 text-xs text-gray-400 dark:text-gray-500">
            <span class="flex items-center gap-0.5" :title="__('Items')">
              <Package class="w-3 h-3" />
              {{ room.item_count }}
            </span>
            <span
              v-if="room.open_task_count > 0"
              class="flex items-center gap-0.5"
              :title="__('Open tasks')"
            >
              <HardHat class="w-3 h-3" />
              {{ room.open_task_count }}
            </span>
          </div>
        </div>
      </div>

      <!-- Unassigned virtual card -->
      <div
        v-if="hasUnassigned"
        class="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-dashed
               border-gray-300 dark:border-gray-600 hover:border-accent-300 dark:hover:border-accent-600
               cursor-pointer transition-all"
        @click="navigateToUnassigned"
      >
        <div class="flex flex-col items-center text-center pt-2">
          <HelpCircle class="w-8 h-8 text-gray-300 dark:text-gray-600 mb-2" />
          <span class="text-sm font-medium text-gray-500 dark:text-gray-400">
            {{ __('Unassigned') }}
          </span>
          <div class="flex items-center gap-3 mt-2 text-xs text-gray-400 dark:text-gray-500">
            <span v-if="unassignedCounts.item_count > 0" class="flex items-center gap-0.5">
              <Package class="w-3 h-3" />
              {{ unassignedCounts.item_count }}
            </span>
          </div>
        </div>
      </div>

      <!-- Add room card -->
      <button
        v-if="!isArchived"
        data-tour="add-room"
        @click="showAddDialog = true"
        class="flex flex-col items-center justify-center gap-2 p-3 rounded-lg
               border-2 border-dashed border-gray-300 dark:border-gray-600
               text-gray-400 dark:text-gray-500
               hover:border-accent-400 hover:text-accent-500 dark:hover:border-accent-500 dark:hover:text-accent-400
               transition-colors min-h-[120px]"
      >
        <Plus class="w-6 h-6" />
        <span class="text-sm">{{ __('Add Room') }}</span>
      </button>
    </div>

    <!-- Add Room Dialog -->
    <AddRoomDialog
      v-if="showAddDialog"
      :property="property"
      @close="showAddDialog = false"
      @created="onRoomCreated"
    />

    <!-- Delete Room Dialog -->
    <DeleteRoomDialog
      v-if="showDeleteDialog && deleteTarget"
      :room="deleteTarget"
      :all-rooms="rooms"
      @close="showDeleteDialog = false"
      @deleted="onRoomDeleted"
    />

  </div>
</template>
