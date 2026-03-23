// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { ref, onUnmounted, type Ref } from 'vue'

export interface BarcodeScanResult {
  text: string
  format: string
}

/**
 * Composable for client-side barcode scanning using @zxing/library.
 *
 * Decodes EAN-13, UPC-A, QR, and Data Matrix barcodes from the device
 * camera entirely in the browser — no server round-trip for the decode step.
 */
export function useBarcodeScanner() {
  const isScanning: Ref<boolean> = ref(false)
  const error: Ref<string> = ref('')
  let codeReader: any = null

  async function startScanning(
    videoElement: HTMLVideoElement,
    onResult: (result: BarcodeScanResult) => void
  ): Promise<void> {
    error.value = ''

    try {
      const zxing = await import('@zxing/library')

      const ReaderClass = zxing.BrowserMultiFormatReader
      codeReader = new ReaderClass()
      isScanning.value = true

      await codeReader.decodeFromVideoDevice(
        undefined,
        videoElement,
        (result: any, err: any) => {
          if (result) {
            const text: string = result.getText()
            const format: string = result.getBarcodeFormat?.()?.toString() || 'unknown'
            stopScanning()
            onResult({ text, format })
          }
          // err is expected when no barcode is in frame — ignore
        }
      )
    } catch (e: any) {
      isScanning.value = false
      if (e.name === 'NotAllowedError') {
        error.value = 'camera_denied'
      } else if (e.name === 'NotFoundError') {
        error.value = 'no_camera'
      } else {
        error.value = 'scan_failed'
      }
    }
  }

  function stopScanning(): void {
    isScanning.value = false
    if (codeReader) {
      try {
        codeReader.reset()
      } catch {
        // ignore reset errors
      }
      codeReader = null
    }
  }

  onUnmounted(() => {
    stopScanning()
  })

  return {
    isScanning,
    error,
    startScanning,
    stopScanning,
  }
}
