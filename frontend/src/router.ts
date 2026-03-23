// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { createRouter, createWebHistory, type RouteRecordRaw, type Router, type RouteLocationNormalized } from 'vue-router'
import { __ } from './composables/useTranslate'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
  }
}

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
    redirect: '/home/settings',
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
    name: 'HouseholdSettings',
    component: () => import('./pages/HouseholdSettings.vue'),
    meta: { title: 'Settings' }
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
