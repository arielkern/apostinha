<template>
    <div class="q-pa-md">
        <q-card class="q-pa-md">
            <q-card-section>
                <div class="text-h6">Faltam</div>
                <div class="text-subtitle1">
                    {{ days }} dias {{ hours }} h {{ minutes }} m {{ seconds }} s
                </div>
            </q-card-section>
        </q-card>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';

const END_TIME = new Date('2025-12-12 18:00:00')

const now = ref(new Date());

let timer: ReturnType<typeof setInterval>;

onMounted(() => {
    timer = setInterval(() => now.value = new Date(), 1000);
});

onUnmounted(() => {
    clearInterval(timer);
});

const timeDifference = computed(() => Math.max(0, END_TIME.getTime() - now.value.getTime()));

const days = computed(() => Math.floor(timeDifference.value / (1000 * 60 * 60 * 24)));
const hours = computed(() => Math.floor((timeDifference.value / (1000 * 60 * 60)) % 24));
const minutes = computed(() => Math.floor((timeDifference.value / (1000 * 60)) % 60));
const seconds = computed(() => Math.floor((timeDifference.value / 1000) % 60));

</script>