import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

// Type for frappe-ui vite plugin
type FrappeUIVitePlugin = (options?: {
  frappeProxy?: boolean
  lucideIcons?: boolean
  jinjaBootData?: boolean
}) => Plugin

// Try to load frappe-ui vite plugin
let frappeui: FrappeUIVitePlugin | undefined
try {
  const module = await import('frappe-ui/vite')
  frappeui = module.default as FrappeUIVitePlugin
} catch {
  console.warn('frappe-ui vite plugin not found, continuing without it')
}

// Type for bundle chunk
interface BundleChunk {
  type: 'asset' | 'chunk'
  fileName: string
  isEntry?: boolean
}

// Type for manifest
interface FrappeManifest {
  js?: string
  css?: string
}

// Plugin to generate assets manifest for Frappe
function frappeManifestPlugin(): Plugin {
  return {
    name: 'frappe-manifest',
    writeBundle(options, bundle: Record<string, BundleChunk>): void {
      const manifest: FrappeManifest = {}
      const cssFiles: string[] = []

      for (const [fileName, chunk] of Object.entries(bundle)) {
        if (chunk.type === 'asset' || chunk.type === 'chunk') {
          if (fileName.endsWith('.js') && chunk.isEntry) {
            manifest.js = fileName
          }
          if (fileName.endsWith('.css')) {
            cssFiles.push(fileName)
          }
        }
      }
      manifest.css = cssFiles.find(f => f.includes('main-')) || cssFiles[0]

      // Write manifest
      const manifestPath = path.resolve(options.dir || '', 'manifest.json')
      fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2))

      // Generate home.html for Frappe www
      const jsFile = manifest.js?.replace('assets/', '') || ''
      const cssFile = manifest.css?.replace('assets/', '') || ''
      const htmlContent = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Home</title>
    <meta name="description" content="Home - Household Management" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
    <link rel="icon" type="image/svg+xml" href="/assets/home/images/home_logo.svg" />
    <script type="module" crossorigin src="/assets/home/frontend/assets/${jsFile}"></script>
    <link rel="stylesheet" crossorigin href="/assets/home/frontend/assets/${cssFile}">
  </head>
  <body>
    <script>
      (function() {
        var stored = localStorage.getItem('dock-theme');
        var isDark = stored === 'dark' ||
          (!stored || stored === 'auto') && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (isDark) document.documentElement.classList.add('dark');
      })();
    </script>
    <div id="app" class="h-screen"></div>
    <div id="modals"></div>
    <div id="popovers"></div>
    <script>
      window.csrf_token = "{{ csrf_token }}"
    </script>
    {% for key in boot %}
    <script>
      window["{{ key }}"] = {{ boot[key] | tojson }};
    </script>
    {% endfor %}
  </body>
</html>`

      const htmlPath = path.resolve(__dirname, '../home/www/home.html')
      fs.mkdirSync(path.dirname(htmlPath), { recursive: true })
      fs.writeFileSync(htmlPath, htmlContent)
      console.log('Generated home.html with assets:', manifest)
    }
  }
}

export default defineConfig({
  base: '/assets/home/frontend/',
  plugins: [
    vue(),
    frappeui && frappeui({
      frappeProxy: true,
      lucideIcons: true,
      jinjaBootData: true
    }),
    frappeManifestPlugin()
  ].filter(Boolean) as Plugin[],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: '../home/public/frontend',
    emptyOutDir: true,
    target: 'es2015',
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      external: [/^\/assets\/dock\//],
      input: {
        main: path.resolve(__dirname, 'index.html')
      },
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  server: {
    host: true,
    port: 5174,
    proxy: {
      '^/(api|assets|files)': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  optimizeDeps: {
    include: ['frappe-ui', 'vue', 'vue-router']
  }
})
