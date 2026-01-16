<template>
    <div class="row items-center q-gutter-md">
        <q-select v-model="selectedYear" :options="yearOptions" outlined dense emit-value map-options
            @update:model-value="handleYearChange" style="min-width: 120px" />
    </div>
</template>

<script setup lang="ts">
import { useMainStore } from 'src/stores/main.store'
import { computed } from 'vue'

const mainStore = useMainStore()

const selectedYear = computed({
    get: () => mainStore.selectedYear,
    set: (value) => {
        mainStore.selectedYear = value
    }
})

const yearOptions = [
    { label: '2025', value: 2025 },
    { label: '2026', value: 2026 }
]

const handleYearChange = async () => {
    // The MainLayout will be watching this change via computed watcher
    // and will refetch the data automatically
}
</script>
