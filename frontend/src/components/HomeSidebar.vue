<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Home sidebar — follows ecosystem sidebar-nav spec.
-->
<script lang="ts" setup>
import { computed, type Component } from 'vue'
import { useRoute } from 'vue-router'
import {
  Home,
  Wrench,
  HardHat,
  Settings,
  Wallet,
  FolderOpen,
  Camera,
  BookOpen,
} from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useSidebar } from '@/composables/useSidebar'

const emit = defineEmits<{ close: [] }>()

const route = useRoute()
const { collapsed, mobileOpen } = useSidebar()

interface NavItem {
  path: string
  name: string
  icon: Component
  tourId?: string
}

const navItems: NavItem[] = [
  { path: '/home', name: __('My Home'), icon: Home },
  { path: '/home/items', name: __('Items'), icon: Wrench, tourId: 'add-item' },
  { path: '/home/maintenance', name: __('Maintenance'), icon: HardHat, tourId: 'add-maintenance' },
  { path: '/home/budget', name: __('Finances'), icon: Wallet },
  { path: '/home/documents', name: __('Documents'), icon: FolderOpen },
  { path: '/home/photos', name: __('Photos'), icon: Camera },
  { path: '/home/passport', name: __('Passport'), icon: BookOpen },
  { path: '/home/settings', name: __('Settings'), icon: Settings },
]

function isActive(item: NavItem): boolean {
  if (item.path === '/home') {
    return route.path === '/home'
  }
  return route.path.startsWith(item.path)
}

function navItemClasses(item: NavItem): string[] {
  const base = [
    'group sidebar-item flex items-center no-underline',
    'transition-all duration-200 rounded-r-lg relative',
    'min-h-[44px]',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50',
    'focus-visible:ring-offset-2 focus-visible:ring-offset-home-500',
  ]

  if (isActive(item)) {
    base.push('bg-white/20 text-white font-semibold border-r-4 border-white')
  } else {
    base.push('text-white/90 hover:bg-white/10 hover:text-white')
  }

  if (collapsed.value) {
    base.push('justify-center px-2 py-3 mx-1')
  } else {
    base.push('gap-3 px-4 py-3 mr-2')
  }

  return base
}

function iconClasses(item: NavItem): string[] {
  return [
    'transition-transform duration-200 flex-shrink-0',
    collapsed.value ? 'w-6 h-6' : 'w-5 h-5',
    isActive(item) ? 'scale-110' : 'group-hover:scale-105',
  ]
}

const APP_VERSION = '0.2.0'
const GITHUB_URL = 'https://github.com/tonic/home'
</script>

<template>
  <aside
    :class="[
      'flex-shrink-0 flex flex-col bg-home-500 transition-all duration-200',
      collapsed ? 'w-16' : 'w-52',
      'max-sm:fixed max-sm:left-0 max-sm:top-14 max-sm:h-[calc(100vh-3.5rem)] max-sm:z-40 max-sm:w-52',
      mobileOpen ? 'max-sm:translate-x-0' : 'max-sm:-translate-x-full',
    ]"
    aria-label="Home navigation"
  >
    <!-- Nav items -->
    <nav class="flex-1 overflow-y-auto py-2">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="navItemClasses(item)"
        :title="collapsed ? item.name : ''"
        :data-tour="item.tourId || undefined"
        @click="emit('close')"
      >
        <component :is="item.icon" :class="iconClasses(item)" />
        <span v-if="!collapsed" class="flex-1 text-sm">{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="py-3 border-t border-home-400">
      <!-- Expanded footer -->
      <template v-if="!collapsed">
        <div class="px-4 pb-2">
          <div class="text-sm font-semibold text-white/80">{{ __('Community Edition') }}</div>
          <div class="text-xs text-home-200">v{{ APP_VERSION }}</div>
        </div>
        <div class="flex items-center gap-4 px-4">
          <a
            :href="GITHUB_URL"
            target="_blank"
            rel="noopener noreferrer"
            class="text-home-200 hover:text-white transition-colors"
            :title="__('Source Code')"
            :aria-label="__('Source Code on GitHub')"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>
        </div>
      </template>

      <!-- Collapsed footer -->
      <template v-else>
        <div class="flex flex-col items-center gap-2">
          <a
            :href="GITHUB_URL"
            target="_blank"
            rel="noopener noreferrer"
            class="text-home-200 hover:text-white transition-colors"
            :title="__('Source Code')"
            :aria-label="__('Source Code on GitHub')"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>
        </div>
      </template>
    </div>
  </aside>
</template>
