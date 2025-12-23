<template>
    <div>
        {{ search }}
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const search = route.params.search
</script>

<style lang="scss" scoped>

</style>