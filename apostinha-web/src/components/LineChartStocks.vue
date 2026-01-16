<template>
  <q-card class="q-pa-md row items-center" style="height: 300px; width: 345px;">
    <Line :data="chartData" :options="chartOptions" style="height: 100%" />
  </q-card>
</template>

<script setup lang="ts">
import { Line } from 'vue-chartjs'
import zoomPlugin from "chartjs-plugin-zoom";

import { Chart as ChartJS, Title, Tooltip, Legend, CategoryScale, LinearScale, type ChartOptions, type ChartData, LineElement, PointElement, TimeScale } from 'chart.js'
import { type DataI, useMainStore } from 'src/stores/main.store';
import { computed, type ComputedRef } from 'vue';
import { date } from 'quasar'

const { formatDate } = date

ChartJS.register(Title, Tooltip, Legend, LineElement,
  LinearScale,
  PointElement,
  TimeScale, CategoryScale, LinearScale, zoomPlugin)

const mainStore = useMainStore()

const dates = computed(() => mainStore.portfolio?.data.dates.map(date => formatDate(date, 'DD/MM')) as string[])

const portfolios = computed(() => Object.keys(mainStore.portfolio?.data.portfolios ?? {}) as (keyof DataI['portfolios'])[])

const assetPrices = computed(() => Object.assign({}, ...portfolios.value.map(portfolioName => mainStore.portfolio?.data.portfolios[portfolioName].assetPrices)))

const assetNames = computed(() => Object.keys(assetPrices.value))

const COLORS = [
  '#FFDD00', // BBAS3 (Banco do Brasil - yellow)
  '#6AC7FF', // VALE3 (Vale - turquoise/cyan)
  '#FF9C00', // EQTL3 (Equatorial - bright orange)
  '#E30613', // MDIA3 (M.Dias Branco - bright red)
  '#FF6AB5', // NTCO3 (Natura &Co - vibrant pinkish-orange)
  '#7CCF51', // FLRY3 (Fleury - fresh green)
  '#EC7000', // ITUB4 (Itaú Unibanco - Itaú orange)
  '#FFFFFF', // LREN4 (Lojas Renner - pure white, distinctive in dark mode)
  '#00A88F', // SUZB4 (Suzano - teal green)
  '#A56EFF', // IBOV (Ibovespa Index - distinct purple, easily distinguishable)
];

const getAccReturnStocks = (ticker: string) => {
  const prices = assetPrices.value[ticker] as number[]
  if (prices.length === 0) return [];

  const initialPrice = prices[0] as number

  return prices.map((price) => (price - initialPrice) / initialPrice);
}

const chartData: ComputedRef<ChartData<'line'>> = computed(() => (
  {
    labels: dates.value,
    datasets: assetNames.value.slice(0, -1).map((assetName, idx) => ({
      label: assetName,
      borderColor: COLORS[idx],
      data: getAccReturnStocks(assetName),
      pointRadius: 0,
      borderWidth: 1.5
    }))

  }
))

const chartOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    tooltip: {
      enabled: true,
      mode: 'index',
      intersect: false,
      callbacks: {
        label: (item) => `${item.dataset.label}: ${(Number(item.raw) * 100).toFixed(1)}%`
      }
    },
    zoom: {
      pan: {
        enabled: true,
        mode: "x", // Allow panning in the X-axis (left & right)
      },
      zoom: {
        wheel: {
          enabled: true, // Zoom using the scroll wheel
        },
        pinch: {
          enabled: true, // Zoom using pinch gestures on mobile
        },
        mode: "x", // Only zoom the X-axis
      },
    },
  },
  interaction: {
    mode: 'index',
    intersect: false
  },
  scales: {
    y: {
      ticks: { callback: (value) => `${(Number(value) * 100).toFixed(0)}%` },
    }
  }
}

</script>