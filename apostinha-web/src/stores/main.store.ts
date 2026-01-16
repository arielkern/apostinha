import { defineStore, acceptHMRUpdate } from 'pinia';
import { ref, computed } from 'vue';

interface PortfolioI {
  assets: Record<string, number[]>
  assetPrices: Record<string, number[]>
  portfolioReturn: number[]
}

export interface DataI {
  dates: string[]
  portfolios: Record<'Ari' | 'Jai' | 'Vai' | 'IBOV', PortfolioI>
}

export interface JsonI {
  updatedAt: string
  data: DataI
}

export const useMainStore = defineStore('main', () => {
  const portfolio = ref<JsonI>()
  const loading = ref(false)
  const selectedYear = ref<2025 | 2026>(2026)

  // Year configuration with end times
  const yearConfig = {
    2025: { endTime: '2025-12-12 21:00:00' },
    2026: { endTime: '2026-12-15 21:00:00' }
  }

  // Get end time for current selected year
  const getEndTime = computed(() => {
    return new Date(yearConfig[selectedYear.value].endTime)
  })

  return { portfolio, loading, selectedYear, getEndTime }
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMainStore, import.meta.hot));
}
