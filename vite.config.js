import { defineConfig } from 'vite';

// Servidor de desenvolvimento do catálogo e da captura. O legado (_arquivo) fica fora.
export default defineConfig({
  server: {
    port: 5173,
    strictPort: false,
    watch: { ignored: ['**/_arquivo/**', '**/catalogo/folhas/**', '**/capturas/**', '**/.git/**'] },
    fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/_arquivo/**'] },
  },
  optimizeDeps: {
    entries: ['catalogo/index.html', 'ferramentas/pagina/captura.html'],
  },
});

