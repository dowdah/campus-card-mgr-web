<template>
  <div id="app">
    <Navbar />
    <h3>{{ title }}</h3>
    <router-view></router-view>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
export default {
  name: 'App',
  data() {
    return {
      title: process.env.VUE_APP_TITLE
    };
  },
  components: {
    Navbar
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
