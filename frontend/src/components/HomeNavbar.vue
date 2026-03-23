<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Home fallback navbar — renders when Dock is not installed.
  Follows ecosystem top-bar spec: ecosystem.localhost/spec/design/ui-specs/top-bar.md
-->
<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Menu, Search, Bell, Grip, Sun, Monitor, Moon, LogOut } from 'lucide-vue-next'
import { __ } from '@/composables/useTranslate'
import { useSidebar } from '@/composables/useSidebar'
import { useTheme } from '@/composables/useTheme'

// ── App-specific constants ──────────────────────────────────────────────
const APP_NAME   = 'Home'
const APP_ICON   = '/assets/home/images/home_logo.svg'
const APP_COLOR  = '#f59e0b'
const APP_ROUTE  = '/home'
const FRAPPE_LOGO = '/assets/frappe/images/frappe-framework-logo.svg'
const SEARCH_SECTIONS = ['Properties', 'Items']
// ────────────────────────────────────────────────────────────────────────

const sidebar = useSidebar()
const { theme, setTheme } = useTheme()
const scrolled = ref(false)
const searchQuery = ref('')
const searchScope = ref('')
const searchInput = ref<HTMLInputElement | null>(null)
const switcherTrigger = ref<HTMLButtonElement | null>(null)
const isMobile = ref(window.innerWidth < 640)

// Hardcoded ecosystem apps — fallback only (no dynamic registry without Dock)
const ecosystemApps = [
  { name: 'home',    label: 'Home',    route: '/home',    color: '#f59e0b' },
  { name: 'orga',    label: 'Orga',    route: '/orga',    color: '#16a34a' },
  { name: 'micro',   label: 'Micro',   route: '/micro',   color: '#2563eb' },
  { name: 'faktura', label: 'Faktura', route: '/faktura', color: '#dc2626' },
  { name: 'tender',  label: 'Tender',  route: '/tender',  color: '#ea580c' },
  { name: 'repo',    label: 'Repo',    route: '/repo',    color: '#0d9488' },
  { name: 'jana',    label: 'Jana',    route: '/jana',    color: '#7c3aed' },
]

// Dropdown state — mutual exclusion (spec §8)
const bellOpen     = ref(false)
const switcherOpen = ref(false)
const menuOpen     = ref(false)

function closeAll() {
  const wasOpen = switcherOpen.value || bellOpen.value || menuOpen.value
  bellOpen.value     = false
  switcherOpen.value = false
  menuOpen.value     = false
  // Return focus to trigger on close (WCAG 2.4.3)
  if (wasOpen) switcherTrigger.value?.focus()
}

function handleResize() {
  isMobile.value = window.innerWidth < 640
}

function toggleDropdown(which: 'bell' | 'switcher' | 'menu') {
  const refs = { bell: bellOpen, switcher: switcherOpen, menu: menuOpen }
  const next = !refs[which].value
  closeAll()
  refs[which].value = next
}

// User info
const user = (window as any).frappe?.session?.user ?? 'Guest'
const userFullName = (window as any).frappe?.boot?.user?.full_name ?? user
const userImage = (window as any).frappe?.boot?.user?.user_image ?? null
const userInitial = computed(() => userFullName.charAt(0).toUpperCase())
const unreadCount = ref(0)

function handleScroll() {
  scrolled.value = window.scrollY > 4
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    closeAll()
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    if (window.innerWidth >= 768) {
      searchInput.value?.focus()
    }
  }
}

function handleOutsideClick(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('[data-dropdown]')) {
    closeAll()
  }
}

function logout() {
  window.location.href = '/api/method/logout'
}

onMounted(() => {
  document.documentElement.style.setProperty('--dock-accent', APP_COLOR)
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('resize', handleResize, { passive: true })
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<template>
  <header
    role="banner"
    :class="[
      'h-14 sticky top-0 z-50 flex items-center gap-2 px-4 select-none',
      'bg-[var(--dock-bg)] text-[var(--dock-text)] transition-shadow duration-150',
      scrolled
        ? 'shadow-sm'
        : 'border-b border-[var(--dock-border)] border-opacity-50'
    ]"
  >
    <!-- 1. Sidebar toggle -->
    <button
      class="flex items-center justify-center w-8 h-8 rounded-md flex-shrink-0
             text-[var(--dock-icon)] hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
      :aria-label="__('Toggle sidebar')"
      :title="__('Toggle sidebar')"
      @click="sidebar.toggle()"
    >
      <Menu class="w-5 h-5" aria-hidden="true" />
    </button>

    <!-- 2. App label -->
    <a
      :href="APP_ROUTE"
      class="flex items-center gap-2 min-w-0 flex-shrink-0 no-underline"
    >
      <img :src="APP_ICON" :alt="APP_NAME" class="w-6 h-6 rounded-md flex-shrink-0" />
      <span class="text-sm font-medium text-[var(--dock-text)] truncate max-w-[140px]">
        {{ APP_NAME }}
      </span>
    </a>

    <!-- 3. Search — center fill -->
    <div class="flex-1 flex justify-center px-4">
      <!-- Desktop inline bar -->
      <div class="hidden md:flex items-center flex-1 max-w-lg mx-4 relative">
        <div
          class="flex items-center w-full h-9 rounded-lg border border-[var(--dock-border)]
                 bg-[var(--dock-bg)] overflow-hidden transition-all
                 focus-within:ring-2 focus-within:ring-[var(--dock-accent)]/30
                 focus-within:border-[var(--dock-accent)]"
        >
          <select
            v-model="searchScope"
            class="h-full px-3 text-sm text-[var(--dock-icon)]
                   bg-black/5 dark:bg-white/5 border-r border-[var(--dock-border)]
                   outline-none cursor-pointer shrink-0"
          >
            <option value="">{{ __('All') }}</option>
            <option v-for="section in SEARCH_SECTIONS" :key="section" :value="section.toLowerCase()">
              {{ __(section) }}
            </option>
          </select>
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search...')"
            class="flex-1 h-full px-3 text-sm bg-transparent
                   text-[var(--dock-text)] placeholder-[var(--dock-icon)]
                   outline-none min-w-0"
          />
          <button
            class="h-full px-3 text-[var(--dock-icon)] hover:text-[var(--dock-text)] transition-colors"
            :aria-label="__('Search')"
          >
            <Search class="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      <!-- Mobile icon button -->
      <button
        class="md:hidden flex items-center justify-center w-8 h-8 rounded-md flex-shrink-0
               text-[var(--dock-icon)] hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
        :aria-label="__('Search')"
        :title="__('Search')"
      >
        <Search class="w-4 h-4" aria-hidden="true" />
      </button>
    </div>

    <!-- Right slot cluster -->
    <div class="flex items-center gap-1 flex-shrink-0">
      <!-- Slots 4 (Timer), 6 (Calendar), 7 (Jana) absent in fallback navbar -->

      <!-- 5. Bell -->
      <div class="relative" data-dropdown>
        <button
          class="flex items-center justify-center w-8 h-8 rounded-md flex-shrink-0
                 text-[var(--dock-icon)] hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
          :aria-expanded="bellOpen"
          :aria-label="__('Notifications')"
          :title="__('Notifications')"
          @click="toggleDropdown('bell')"
        >
          <Bell class="w-4 h-4" aria-hidden="true" />
          <span
            v-if="unreadCount > 0"
            class="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1
                   bg-red-500 text-white text-[10px] font-bold leading-none
                   rounded-full flex items-center justify-center"
            :aria-label="`${unreadCount} ${__('unread notifications')}`"
          >
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </span>
        </button>
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 translate-y-1.5"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0"
        >
          <div
            v-if="bellOpen"
            class="absolute right-0 mt-2 w-72 rounded-lg shadow-lg
                   border border-[var(--dock-border)] bg-[var(--dock-bg)] p-4"
          >
            <p class="text-sm text-[var(--dock-icon)]">{{ __('No notifications') }}</p>
          </div>
        </Transition>
      </div>

      <!-- 8. App switcher -->
      <div class="relative" data-dropdown>
        <button
          ref="switcherTrigger"
          class="flex items-center justify-center w-8 h-8 rounded-md flex-shrink-0
                 text-[var(--dock-icon)] hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
          :aria-expanded="switcherOpen"
          aria-haspopup="true"
          :aria-label="__('Open app switcher')"
          :title="__('App switcher')"
          @click="toggleDropdown('switcher')"
        >
          <Grip class="w-4 h-4" aria-hidden="true" />
        </button>

        <!-- Mobile backdrop -->
        <Transition
          enter-active-class="transition-opacity duration-150 ease-out"
          leave-active-class="transition-opacity duration-100 ease-in"
          enter-from-class="opacity-0"
          leave-to-class="opacity-0"
        >
          <div
            v-if="switcherOpen"
            class="fixed inset-0 bg-black/20 z-30 sm:hidden"
            aria-hidden="true"
            @click="closeAll()"
          />
        </Transition>

        <!-- Panel: bottom sheet (mobile) / popover (desktop) -->
        <Transition
          :enter-active-class="isMobile ? 'transition duration-200 ease-out' : 'transition duration-150 ease-out'"
          :enter-from-class="isMobile ? 'opacity-0 translate-y-full' : 'opacity-0 translate-y-1.5'"
          :enter-to-class="isMobile ? 'opacity-100 translate-y-0' : 'opacity-100 translate-y-0'"
          :leave-active-class="isMobile ? 'transition duration-150 ease-in' : 'transition duration-100 ease-in'"
          :leave-from-class="isMobile ? 'opacity-100 translate-y-0' : 'opacity-100 translate-y-0'"
          :leave-to-class="isMobile ? 'opacity-0 translate-y-full' : 'opacity-0'"
        >
          <div
            v-if="switcherOpen"
            role="dialog"
            :aria-label="__('App switcher')"
            :class="[
              'max-h-[420px] overflow-y-auto bg-[var(--dock-bg)] border border-[var(--dock-border)] shadow-lg p-3',
              'fixed inset-x-0 bottom-0 rounded-t-2xl z-40',
              'sm:absolute sm:inset-x-auto sm:right-0 sm:bottom-auto sm:top-full sm:mt-2 sm:w-72 sm:rounded-lg sm:z-20'
            ]"
          >
            <!-- Mobile drag handle -->
            <div class="flex justify-center mb-3 sm:hidden">
              <div class="w-10 h-1 rounded-full bg-gray-300 dark:bg-gray-600" />
            </div>

            <!-- App grid -->
            <div
              role="grid"
              :aria-label="__('Installed apps')"
              class="grid grid-cols-3 gap-2 mb-3"
            >
              <div role="row" class="contents">
                <a
                  v-for="app in ecosystemApps"
                  :key="app.name"
                  :href="app.route"
                  role="gridcell"
                  :aria-label="app.label"
                  class="flex flex-col items-center gap-1.5 p-2 rounded-lg text-center no-underline
                         hover:bg-black/5 dark:hover:bg-white/10 transition-colors
                         focus-visible:outline-none focus-visible:ring-2
                         focus-visible:ring-[var(--dock-accent)] focus-visible:ring-offset-1"
                >
                  <span
                    class="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden flex-shrink-0 text-white text-xl font-bold"
                    :style="{ backgroundColor: app.color }"
                  >
                    {{ app.label[0] }}
                  </span>
                  <span class="text-xs text-[var(--dock-text)] truncate w-full leading-tight">
                    {{ app.label }}
                  </span>
                </a>
              </div>
            </div>

            <!-- Footer -->
            <div class="border-t border-[var(--dock-border)] pt-2 mt-1 space-y-0.5">
              <a
                href="/app"
                class="flex items-center gap-2 px-2 py-1.5 rounded-lg no-underline
                       hover:bg-black/5 dark:hover:bg-white/10 transition-colors
                       text-sm text-[var(--dock-icon)]"
              >
                <img :src="FRAPPE_LOGO" alt="Frappe" class="w-4 h-4" />
                {{ __('Frappe Desk') }}
              </a>
              <a
                href="https://docs.tonic.dev/dock"
                class="block px-2 py-1.5 text-xs text-gray-400 hover:text-gray-600
                       dark:hover:text-gray-300 transition-colors no-underline"
              >
                {{ __('More with Dock →') }}
              </a>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 9. Avatar -->
      <div class="relative" data-dropdown>
        <button
          class="w-8 h-8 rounded-full overflow-hidden flex-shrink-0
                 bg-black/10 dark:bg-white/20 hover:bg-black/15 dark:hover:bg-white/30
                 transition-colors flex items-center justify-center
                 text-[var(--dock-text)] text-xs font-semibold"
          :aria-expanded="menuOpen"
          aria-haspopup="true"
          :aria-label="__('User menu')"
          :title="userFullName"
          @click="toggleDropdown('menu')"
        >
          <img v-if="userImage" :src="userImage" :alt="userFullName" class="w-full h-full object-cover" />
          <span v-else>{{ userInitial }}</span>
        </button>
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 translate-y-1.5"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0"
        >
          <div
            v-if="menuOpen"
            class="absolute right-0 mt-2 w-56 rounded-lg shadow-lg
                   border border-[var(--dock-border)] bg-[var(--dock-bg)] py-1"
          >
            <!-- User identity -->
            <div class="px-3 py-2 border-b border-[var(--dock-border)]">
              <div class="text-sm font-medium text-[var(--dock-text)] truncate">{{ userFullName }}</div>
              <div class="text-xs text-[var(--dock-icon)] truncate">{{ user }}</div>
            </div>

            <!-- Links -->
            <div class="py-1 border-b border-[var(--dock-border)]">
              <a href="/app/user" class="block px-3 py-1.5 text-sm text-[var(--dock-text)] hover:bg-black/5 dark:hover:bg-white/10 no-underline">
                {{ __('My Profile') }}
              </a>
              <a href="/home/preferences" class="block px-3 py-1.5 text-sm text-[var(--dock-text)] hover:bg-black/5 dark:hover:bg-white/10 no-underline">
                {{ __('Preferences') }}
              </a>
            </div>

            <!-- Theme pill -->
            <div class="px-3 py-2 border-b border-[var(--dock-border)]">
              <div class="flex items-center gap-0.5 bg-black/5 dark:bg-white/5 rounded-lg p-0.5">
                <button
                  :class="[
                    'flex-1 flex items-center justify-center gap-1 py-1 rounded-md text-xs transition-colors',
                    theme === 'light' ? 'bg-[var(--dock-bg)] shadow-sm text-[var(--dock-text)]' : 'text-[var(--dock-icon)]'
                  ]"
                  @click="setTheme('light')"
                  :title="__('Light')"
                >
                  <Sun class="w-3.5 h-3.5" />
                </button>
                <button
                  :class="[
                    'flex-1 flex items-center justify-center gap-1 py-1 rounded-md text-xs transition-colors',
                    theme === 'system' ? 'bg-[var(--dock-bg)] shadow-sm text-[var(--dock-text)]' : 'text-[var(--dock-icon)]'
                  ]"
                  @click="setTheme('system')"
                  :title="__('System')"
                >
                  <Monitor class="w-3.5 h-3.5" />
                </button>
                <button
                  :class="[
                    'flex-1 flex items-center justify-center gap-1 py-1 rounded-md text-xs transition-colors',
                    theme === 'dark' ? 'bg-[var(--dock-bg)] shadow-sm text-[var(--dock-text)]' : 'text-[var(--dock-icon)]'
                  ]"
                  @click="setTheme('dark')"
                  :title="__('Dark')"
                >
                  <Moon class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <!-- Logout -->
            <div class="py-1">
              <button
                @click="logout"
                class="w-full text-left px-3 py-1.5 text-sm text-red-500 hover:bg-black/5 dark:hover:bg-white/10 flex items-center gap-2"
              >
                <LogOut class="w-4 h-4" />
                {{ __('Logout') }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>
