<script setup>
import { RouterView } from 'vue-router'
import AppNavbar from './components/AppNavbar.vue'
</script>

<template>
  <div class="min-h-screen bg-bg text-text">
    <AppNavbar />
    <main class="p-6">
      <RouterView />
    </main>
  </div>
</template>
