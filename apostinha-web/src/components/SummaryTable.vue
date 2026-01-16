<template>
    <q-card>
        <q-card-section>
            <div class="row full-width justify-between items-center">
                <div class="row items-center">
                    <q-avatar v-if="index == 0" size="24px" text-color="black" font-size="24px">🥇
                    </q-avatar>
                    <q-avatar v-else-if="index == 1" size="24px" text-color="black" font-size="24px">🥈
                    </q-avatar>
                    <q-avatar v-else size="24px" text-color="black" font-size="24px">💩
                    </q-avatar>
                    <div class="text-h6 q-ml-sm">{{ portfolio }}</div>
                    <q-badge class="q-ml-sm" color="orange" v-if="vencedor">Vencedor {{ mainStore.selectedYear
                        }}</q-badge>
                </div>
                <div class="text-h6" :class="getColor(thisPortfolio?.portfolioReturn?.at(-1))">{{
                    ((thisPortfolio?.portfolioReturn?.at(-1) ?? 0) * 100).toFixed(2) }}%</div>
            </div>
        </q-card-section>
        <q-separator dark />
        <q-card-section>
            <q-skeleton v-if="mainStore.loading" height="300px" width="300px" square />
            <q-markup-table v-else dense>
                <thead>
                    <tr>
                        <th class="text-center">Ticker</th>
                        <th class="text-center">Px Inicial</th>
                        <th class="text-center">Px Final</th>
                        <th class="text-center">L1D</th>
                        <th class="text-center">ITD</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="ticker in tickers" :key="ticker">
                        <td class="text-center">{{ ticker }}</td>
                        <td class="text-center">R$ {{ (thisPortfolio?.assetPrices[ticker]?.at(0) ?? 0).toFixed(2) }}
                        </td>
                        <td class="text-center">R$ {{ (thisPortfolio?.assetPrices[ticker]?.at(-1) ?? 0).toFixed(2) }}
                        </td>
                        <td class="text-center" :class="getColor(get1DReturn(ticker))">{{
                            ((get1DReturn(ticker)) * 100).toFixed(2) }}%</td>
                        <td class="text-center" :class="getColor(thisPortfolio?.assets[ticker]?.at(-1))">{{
                            ((thisPortfolio?.assets[ticker]?.at(-1) ?? 0) * 100).toFixed(2) }}%</td>
                    </tr>
                    <tr>
                        <td class="text-center" colspan="3">Portfolio</td>
                        <td class="text-center" :class="getColor(getPortfolio1D())">{{
                            ((getPortfolio1D()) * 100).toFixed(2) }}%</td>
                        <td class="text-center" :class="getColor(thisPortfolio?.portfolioReturn?.at(-1))">{{
                            ((thisPortfolio?.portfolioReturn?.at(-1) ?? 0) * 100).toFixed(2) }}%
                        </td>
                    </tr>
                </tbody>

            </q-markup-table>
        </q-card-section>
        <q-card-section>
            <div v-if="!mainStore.loading" class="full-width text-right text-caption">
                Last updated: {{
                    formattedString }}</div>
        </q-card-section>
    </q-card>
</template>

<script setup lang="ts">
import { type DataI, useMainStore } from 'src/stores/main.store';
import { computed } from 'vue';
import { date } from 'quasar'

const props = defineProps<{ portfolio: keyof DataI['portfolios'], index: number }>()

const mainStore = useMainStore()

const updatedAt = computed(() => date.addToDate(new Date(mainStore.portfolio?.updatedAt ?? 0), { hours: -3 }),)

const formattedString = computed(() => date.formatDate(updatedAt.value, 'DD/MM/YYYY HH:mm'))

const thisPortfolio = computed(() => mainStore.portfolio?.data.portfolios[props.portfolio])

const tickers = computed(() => Object.keys(thisPortfolio.value?.assets ?? {}))

console.log(new Date().toISOString())

const vencedor = computed(() => {
    return props.index == 0 && new Date() > mainStore.getEndTime
})

const getColor = (value?: number) => {
    return value && value > 0 ? 'text-green-4' : 'text-red-4'
}

const get1DReturn = (ticker: string) => {
    const series = thisPortfolio.value?.assets[ticker]
    if (!series) return 0
    const lastItem = series.at(-1) as number
    const beforeLastItem = series.at(-2) as number
    return ((1 + lastItem) / (1 + beforeLastItem)) - 1
}

const getPortfolio1D = () => {
    const series = thisPortfolio.value?.portfolioReturn
    if (!series) return 0
    const lastItem = series.at(-1) as number
    const beforeLastItem = series.at(-2) as number
    return ((1 + lastItem) / (1 + beforeLastItem)) - 1
}

</script>