<template>
  <div class="container">
    <div class="p-8 border border-black w-full">

        <ProfileInfo />
    </div>
    
  </div>
</template>

<script setup>
import ProfileHeader from './components/ProfileHeader.vue';
import ProfileInfo from './components/ProfileInfo.vue';


</script>
<style scoped>

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>
