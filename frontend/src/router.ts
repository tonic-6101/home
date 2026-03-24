// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { createRouter, createWebHistory, type RouteRecordRaw, type Router, type RouteLocationNormalized } from 'vue-router'
import { __ } from './composables/useTranslate'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    dockShared?: boolean
  }
}

// Dock shared pages — calendar, people, discussions, notes, etc. rendered inside Home's layout.
// Each route lazily loads its component from Dock's ESM bundle at navigation time.
const dockEsm = '/assets/dock/js/dock-navbar.esm.js'
const dockInstalled = !!(window as any).frappe?.boot?.dock?.installed
  || !!(window as any).dockBoot?.installed

const dockSharedRoutes: RouteRecordRaw[] = dockInstalled ? [
  {
    path: '/home/account',
    name: 'dock-account',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-account').component()),
    meta: { dockShared: true, title: 'My Account' },
  },
  {
    path: '/home/calendar',
    name: 'dock-calendar',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-calendar').component()),
    meta: { dockShared: true, title: 'Calendar' },
  },
  {
    path: '/home/people',
    name: 'dock-people',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-people').component()),
    meta: { dockShared: true, title: 'People' },
  },
  {
    path: '/home/people/:name',
    name: 'dock-person',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-person').component()),
    meta: { dockShared: true, title: 'Contact' },
  },
  {
    path: '/home/notifications',
    name: 'dock-notifications',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-notifications').component()),
    meta: { dockShared: true, title: 'Notifications' },
  },
  {
    path: '/home/bookmarks',
    name: 'dock-bookmarks',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-bookmarks').component()),
    meta: { dockShared: true, title: 'Bookmarks' },
  },
  {
    path: '/home/notes',
    name: 'dock-notes',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-notes').component()),
    meta: { dockShared: true, title: 'Notes' },
  },
  {
    path: '/home/activity',
    name: 'dock-activity',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-activity').component()),
    meta: { dockShared: true, title: 'Activity' },
  },
  {
    path: '/home/discussions',
    name: 'dock-discussions',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-discussions').component()),
    meta: { dockShared: true, title: 'Discussions' },
  },
  {
    path: '/home/discussions/:name',
    name: 'dock-discussion-detail',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-discussion-detail').component()),
    meta: { dockShared: true, title: 'Discussion' },
  },
  {
    path: '/home/bin',
    name: 'dock-bin',
    component: () => import(/* @vite-ignore */ dockEsm).then(m => m.dockSharedRoutes('/home').find((r: any) => r.name === 'dock-bin').component()),
    meta: { dockShared: true, title: 'Bin' },
  },
] : []

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/home' },

  {
    path: '/home',
    name: 'MyHome',
    component: () => import('./pages/Dashboard.vue'),
    meta: { title: 'My Home' }
  },
  {
    path: '/home/household/settings',
    beforeEnter() { window.location.href = '/dock/settings/app/home' },
    component: () => import('./pages/NotFound.vue'),
  },
  {
    path: '/home/items',
    name: 'ItemList',
    component: () => import('./pages/ItemList.vue'),
    meta: { title: 'Items' }
  },
  {
    path: '/home/items/new',
    name: 'ItemNew',
    component: () => import('./pages/ItemForm.vue'),
    meta: { title: 'Add Item' }
  },
  {
    path: '/home/items/scan',
    name: 'ItemScan',
    component: () => import('./pages/ApplianceScan.vue'),
    meta: { title: 'Scan to Register' }
  },
  {
    path: '/home/items/:name/edit',
    name: 'ItemEdit',
    component: () => import('./pages/ItemForm.vue'),
    meta: { title: 'Edit Item' }
  },
  {
    path: '/home/items/:name',
    name: 'ItemDetail',
    component: () => import('./pages/ItemDetail.vue'),
    meta: { title: 'Item' }
  },
  // Legacy redirects for old routes
  { path: '/home/appliances', redirect: '/home/items' },
  { path: '/home/inventory', redirect: '/home/items' },
  { path: '/home/contractors', redirect: '/home' },
  { path: '/home/contractors/:name', redirect: '/home' },
  {
    path: '/home/maintenance',
    name: 'MaintenanceList',
    component: () => import('./pages/MaintenanceList.vue'),
    meta: { title: 'Maintenance' }
  },
  {
    path: '/home/maintenance/:name',
    name: 'MaintenanceDetail',
    component: () => import('./pages/MaintenanceDetail.vue'),
    meta: { title: 'Maintenance Task' }
  },
  // Warranties live on the Items page as a tab — no standalone page
  { path: '/home/warranties', redirect: '/home/items?tab=warranties' },
  { path: '/home/warranty/:name', redirect: '/home/items?tab=warranties' },
  // InventoryList removed — merged into /home/items
  {
    path: '/home/settings',
    beforeEnter() { window.location.href = '/dock/settings/app/home' },
    component: () => import('./pages/NotFound.vue'),
  },
  {
    path: '/home/preferences',
    name: 'Preferences',
    component: () => import('./pages/HomePreferences.vue'),
    meta: { title: 'Preferences' }
  },
  {
    path: '/home/budget',
    name: 'BudgetOverview',
    component: () => import('./pages/BudgetOverview.vue'),
    meta: { title: 'Budget' }
  },
  {
    path: '/home/wishlist',
    name: 'WishlistOverview',
    component: () => import('./pages/WishlistOverview.vue'),
    meta: { title: 'Wishlist' }
  },
  {
    path: '/home/returns',
    name: 'ReturnList',
    component: () => import('./pages/ReturnList.vue'),
    meta: { title: 'Purchase Returns' }
  },
  {
    path: '/home/insurance',
    name: 'InsuranceList',
    component: () => import('./pages/InsuranceList.vue'),
    meta: { title: 'Insurance' }
  },
  {
    path: '/home/insurance/:name',
    name: 'InsuranceDetail',
    component: () => import('./pages/InsuranceDetail.vue'),
    meta: { title: 'Insurance Policy' }
  },
  {
    path: '/home/utilities',
    name: 'UtilityBillList',
    component: () => import('./pages/UtilityBillList.vue'),
    meta: { title: 'Utility Bills' }
  },
  {
    path: '/home/utilities/trends',
    name: 'UtilityTrends',
    component: () => import('./pages/UtilityTrends.vue'),
    meta: { title: 'Utility Trends' }
  },
  {
    path: '/home/cost-report',
    name: 'CostReport',
    component: () => import('./pages/CostReport.vue'),
    meta: { title: 'Cost Report' }
  },
  {
    path: '/home/equity',
    name: 'EquityTracker',
    component: () => import('./pages/EquityTracker.vue'),
    meta: { title: 'Home Equity' }
  },
  {
    path: '/home/documents',
    name: 'DocumentVault',
    component: () => import('./pages/DocumentVault.vue'),
    meta: { title: 'Documents' }
  },
  {
    path: '/home/letters',
    name: 'CorrespondenceList',
    component: () => import('./pages/CorrespondenceList.vue'),
    meta: { title: 'Correspondence' }
  },
  {
    path: '/home/passport',
    name: 'PropertyPassport',
    component: () => import('./pages/PropertyPassport.vue'),
    meta: { title: 'Property Passport' }
  },
  {
    path: '/home/moving',
    name: 'MovingChecklist',
    component: () => import('./pages/MovingChecklist.vue'),
    meta: { title: 'Moving Checklist' }
  },
  {
    path: '/home/photos',
    name: 'PhotoGallery',
    component: () => import('./pages/PhotoGallery.vue'),
    meta: { title: 'Photos' }
  },

  // Legacy redirects for old multi-property URLs
  { path: '/home/properties', redirect: '/home' },
  { path: '/home/property/:name', redirect: '/home' },
  { path: '/home/property/:name/budget', redirect: '/home/budget' },
  { path: '/home/property/:name/wishlist', redirect: '/home/wishlist' },
  { path: '/home/property/:property/returns', redirect: '/home/returns' },
  { path: '/home/property/:property/insurance', redirect: '/home/insurance' },

  // Dock shared pages (calendar, people, discussions, etc.)
  ...dockSharedRoutes,

  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('./pages/NotFound.vue'),
    meta: { title: 'Page Not Found' }
  },
]

const router: Router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to: RouteLocationNormalized, _from, next) => {
  const isGuest = (window as any).frappe?.session?.user === 'Guest'

  if (to.meta.requiresAuth !== false && isGuest) {
    return next('/login')
  }

  next()
})

router.afterEach((to: RouteLocationNormalized) => {
  const title = to.meta.title
  document.title = title ? `${__(title)} | Home` : 'Home'
})

export default router
