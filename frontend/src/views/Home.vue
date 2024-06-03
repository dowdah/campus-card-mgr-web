<template>
<Dashboard v-if="isAuthenticated"></Dashboard>
  <Login v-else></Login>
</template>
<style scoped>
.dashboard-box {
  display: flex;
  width: fit-content;
  padding: 0 10px; /* 为内部组件分配额外的空间 */
  margin: 0 auto;
}
</style>
<script>
import Dashboard from '../components/Dashboard.vue';
import Login from '../components/Login.vue';
import { mapGetters, mapActions } from 'vuex';
export default {
  name: 'Home',
  components: {Dashboard, Login},
  computed: {
    ...mapGetters(['isAuthenticated'])
  }
};
</script>