<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
import { __ } from '@/composables/useTranslate'
</script>

<template>
  <div class="flex flex-col items-center justify-center h-full p-6">
    <h1 class="text-display text-gray-400 dark:text-gray-600">404</h1>
    <p class="text-body text-gray-600 dark:text-gray-400 mt-2">
      {{ __('Page not found') }}
    </p>
    <router-link
      to="/home"
      class="mt-4 px-4 py-2 bg-home-500 text-white rounded-lg hover:bg-home-600 transition-colors"
    >
      {{ __('Go to Dashboard') }}
    </router-link>
  </div>
</template>
