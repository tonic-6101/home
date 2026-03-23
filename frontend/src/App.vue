<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic
-->
<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted } from 'vue'
import HomeSidebar from './components/HomeSidebar.vue'
import { useSidebar } from './composables/useSidebar'
import { useOnboardingTour } from './composables/useOnboardingTour'

const { mobileOpen, closeMobile } = useSidebar()
const { initTour } = useOnboardingTour()

onMounted(() => {
  initTour()
})

const dockInstalled = computed(() =>
  !!(window as any).frappe?.boot?.dock?.installed
)

const dynImport = new Function('u', 'return import(u)') as (u: string) => Promise<any>

const NavbarComponent = dockInstalled.value
  ? defineAsyncComponent(() =>
      dynImport('/assets/dock/js/dock-navbar.esm.js').then((m: any) => m.DockNavbar)
    )
  : defineAsyncComponent(() => import('./components/HomeNavbar.vue'))
</script>

<template>
  <div class="h-screen flex flex-col bg-[var(--home-bg-secondary)] transition-colors">
    <component :is="NavbarComponent" />

    <div class="flex flex-1 overflow-hidden">
      <!-- Mobile backdrop -->
      <div
        v-if="mobileOpen"
        class="fixed inset-0 bg-black/50 z-30 sm:hidden"
        @click="closeMobile()"
      />

      <HomeSidebar @close="closeMobile" />

      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>
