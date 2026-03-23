<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  displayName: string
  avatar?: string | null
  size?: 'sm' | 'md' | 'lg'
}>()

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-8 h-8 text-xs'
    case 'lg': return 'w-12 h-12 text-base'
    default: return 'w-10 h-10 text-sm'
  }
})

const initials = computed(() => {
  const parts = props.displayName.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  }
  return props.displayName.slice(0, 2).toUpperCase()
})

const bgColor = computed(() => {
  const colors = [
    'bg-amber-500', 'bg-blue-500', 'bg-emerald-500', 'bg-purple-500',
    'bg-rose-500', 'bg-cyan-500', 'bg-orange-500', 'bg-indigo-500',
  ]
  let hash = 0
  for (const ch of props.displayName) {
    hash = ch.charCodeAt(0) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
})
</script>

<template>
  <img
    v-if="avatar"
    :src="avatar"
    :alt="displayName"
    :class="[sizeClass, 'rounded-full object-cover']"
  />
  <div
    v-else
    :class="[sizeClass, bgColor, 'rounded-full flex items-center justify-center text-white font-medium select-none']"
    :title="displayName"
  >
    {{ initials }}
  </div>
</template>
