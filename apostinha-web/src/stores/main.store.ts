import { defineStore, acceptHMRUpdate } from 'pinia';
import { ref } from 'vue';

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

  return { portfolio, loading }
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMainStore, import.meta.hot));
}
