// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { type Component } from 'vue'
import {
  Droplets, Zap, Paintbrush, Hammer, Flame,
  Home, SprayCan, TreePine, Bug, Wrench, HelpCircle,
} from 'lucide-vue-next'

const tradeIcons: Record<string, Component> = {
  Plumber: Droplets,
  Electrician: Zap,
  Painter: Paintbrush,
  Carpenter: Hammer,
  'HVAC & Heating': Flame,
  Roofer: Home,
  Cleaner: SprayCan,
  'Garden & Landscaping': TreePine,
  'Pest Control': Bug,
  General: Wrench,
  Other: HelpCircle,
}

export function tradeIcon(trade: string): Component {
  return tradeIcons[trade] || Wrench
}
