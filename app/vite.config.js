import { defineConfig } from 'vite';

export default defineConfig({
  base: process.env.NODE_ENV === 'production' ? '/training-tesseract-js/' : '/',
  server: {
    host: '0.0.0.0', // Docker内からアクセスできるように
    port: 3333,
    open: false, // Docker環境ではブラウザを自動で開かない
    watch: {
      usePolling: true, // Dockerでのホットリロード用
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
});
