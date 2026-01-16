<template>
  <q-page padding>
    <div class="text-h3 q-pa-md">Apostinha</div>

    <CountdownCard />

    <div class="row  q-gutter-md q-pa-md">

      <SummaryTable v-for="(portfolio, index) in portfolios" :key="portfolio" :portfolio="portfolio" :index="index" />
      <LineChart />
      <LineChartStocks />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import SummaryTable from 'src/components/SummaryTable.vue';
import LineChart from "components/LineChart.vue"
import LineChartStocks from "components/LineChartStocks.vue"
import CountdownCard from 'src/components/CountdownCard.vue';
import { type DataI, useMainStore } from 'src/stores/main.store';
import { computed } from 'vue';

const mainStore = useMainStore()

const portfolioNames = ['Ari', 'Vai', 'Jai'] as const

const indices = [...portfolioNames.keys()];

const portfoliosReturns = computed(() => portfolioNames.map(name => mainStore.portfolio?.data.portfolios[name].portfolioReturn.at(-1) as number))

const sortedIndexes = computed(() => indices.toSorted((a, b) => Number(portfoliosReturns.value[b]) - Number(portfoliosReturns.value[a])))

const portfolios = computed(() => sortedIndexes.value.map(index => portfolioNames[index] as keyof DataI['portfolios']))

</script>
