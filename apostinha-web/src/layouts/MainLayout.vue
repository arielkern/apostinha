<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import { type JsonI, useMainStore } from 'stores/main.store'

const mainStore = useMainStore()

let intervalId: ReturnType<typeof setInterval> | null = null
let inFlight = false

const fetchPortfolios = async (showLoading = false) => {
  if (inFlight) return
  inFlight = true

  if (showLoading) mainStore.loading = true
  try {
    const fileName = mainStore.selectedYear === 2025 ? 'portfolios_2025.json' : 'portfolios_2026.json'
    const response = await fetch(`/${fileName}`, { cache: 'no-store' })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const respJson = (await response.json()) as JsonI
    mainStore.portfolio = respJson
  } catch (err) {
    console.error('Failed to refresh portfolio data', err)
  } finally {
    if (showLoading) mainStore.loading = false
    inFlight = false
  }
}

// Watch for year changes and refetch data
watch(() => mainStore.selectedYear, async () => {
  await fetchPortfolios(true)
})

onMounted(async () => {
  await fetchPortfolios(true) // initial load with spinner
  intervalId = setInterval(() => {
    void fetchPortfolios(false) // silent refresh
  }, 15000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
})
</script>
