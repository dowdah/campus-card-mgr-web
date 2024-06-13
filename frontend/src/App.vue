<template>
  <div id="app">
    <Navbar/>
    <h3>{{ title }}</h3>
    <Unconfirmed v-if="unconfirmed"/>
    <router-view v-if="!unconfirmed"></router-view>
    <LoadingSpinner/>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import {mapGetters, mapActions, mapState} from 'vuex';
import Unconfirmed from "@/views/Unconfirmed.vue";
import LoadingSpinner from '@/components/LoadingSpinner.vue';

export default {
  name: 'App',
  data() {
    return {
      title: process.env.VUE_APP_TITLE
    };
  },
  components: {
    Unconfirmed,
    Navbar,
    LoadingSpinner
  },
  computed: {
    ...mapGetters(['isAuthenticated']),
    user() {
      return this.$store.state.user;
    },
    unconfirmed() {
      if (this.isAuthenticated) {
        return !this.user.confirmed;
      } else {
        return false;
      }
    }
  },
  methods: {
    ...mapActions(['logout']),
    logoutHandler() {
      this.logout().then(() => {
        this.$router.push({name: 'Home'});
      });
    }
  },
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
