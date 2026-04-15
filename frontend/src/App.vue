<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
import { onMounted } from 'vue'
// @ts-ignore — served by Dock's built assets
import { DockLayout, DockSidebarShell } from '/assets/dock/js/dock-navbar.esm.js'
import {
  LayoutDashboard, LayoutList, Wallet, BookOpen,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useOnboardingTour } from './composables/useOnboardingTour'

const { initTour } = useOnboardingTour()

onMounted(() => {
  initTour()
})

const navItems = [
  { key: 'dashboard',   label: __('Dashboard'),    icon: LayoutDashboard, path: '/home',              exact: true },
  { key: 'items',       label: __('Items'),         icon: LayoutList,  path: '/home/items' },
  { key: 'finances',    label: __('Finances'),      icon: Wallet,     path: '/home/budget' },
  { key: 'passport',    label: __('Passport'),      icon: BookOpen,   path: '/home/passport' },
]

declare const __APP_VERSION__: string

const footer = {
  edition: __('Community Edition'),
  version: __APP_VERSION__,
  sourceUrl: 'https://github.com/tonic-6101/home',
}
</script>

<template>
  <DockLayout>
    <DockSidebarShell
      color="#f59e0b"
      :items="navItems"
      :footer="footer"
      aria-label="Home navigation"
    />
    <main class="flex-1 overflow-y-auto">
      <router-view />
    </main>
  </DockLayout>
</template>
