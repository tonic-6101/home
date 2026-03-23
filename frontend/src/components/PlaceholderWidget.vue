<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
defineProps<{ label: string; icon: string }>()
</script>

<template>
  <div class="rounded-xl border border-dashed border-gray-200 p-4 opacity-50 select-none">
    <component :is="icon" class="w-5 h-5 text-gray-400 mb-2" />
    <p class="text-sm text-gray-400">{{ label }}</p>
  </div>
</template>
