<template>
  <Dashboard v-if="isAuthenticated"></Dashboard>
  <Login v-else></Login>
</template>

<script>
import Dashboard from '../components/Dashboard.vue';
import Login from '../components/Login.vue';
import {mapGetters} from 'vuex';

export default {
  name: 'Home',
  components: {Dashboard, Login},
  computed: {
    ...mapGetters(['isAuthenticated'])
  }
};
</script>
