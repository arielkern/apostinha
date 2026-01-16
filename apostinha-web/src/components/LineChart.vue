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

const getAccReturn = (portfolioName: keyof DataI['portfolios']) => {
  return mainStore.portfolio?.data.portfolios[portfolioName].portfolioReturn as number[]
}

const chartData: ComputedRef<ChartData<'line'>> = computed(() => (
  {
    labels: dates.value,
    datasets: [
      {
        label: 'Ari',
        borderColor: "#fcfc30", // Yellow
        data: getAccReturn('Ari'),
        pointRadius: 0,
        borderWidth: 1.5,
      },
      {
        label: 'Jai',
        borderColor: "#007AFF", // Blue
        data: getAccReturn('Jai'),
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 1.5,
      },
      {
        label: 'Vai',
        borderColor: '#a500b9', // Cashin Purple
        data: getAccReturn('Vai'),
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 1.5,
      },
      {
        label: 'IBOV',
        borderColor: "white", // White
        data: getAccReturn('IBOV'),
        tension: 0.3,
        borderDash: [2, 3],
        pointRadius: 0,
        borderWidth: 1.7,
      },
    ]
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