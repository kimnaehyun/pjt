<template>
  <NavBar />
  <RouterView />
</template>

<script setup>
import { RouterView, RouterLink } from "vue-router";
import NavBar from "./components/NavBar.vue";
</script>
<style scoped></style>
