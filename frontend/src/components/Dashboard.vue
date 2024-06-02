<template>
  <div>
    <h2>Dashboard</h2>
    <p v-if="user">Welcome, {{ user.username }}</p>
    <button @click="logoutHandler">Logout</button>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  computed: {
    ...mapGetters(['isAuthenticated']),
    user() {
      return this.$store.state.user;
    }
  },
  methods: {
    ...mapActions(['logout']),
    logoutHandler() {
      this.logout().then(() => {
        this.$router.push({ name: 'Home' });
      });
    }
  }
};
</script>