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
        this.$router.push({name: '主页'});
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

::-webkit-scrollbar {
  height: 8px; /* 设置滚动条的高度 */
}

::-webkit-scrollbar-track {
  background: #f1f1f1; /* 滚动条轨道背景色 */
}

::-webkit-scrollbar-thumb {
  background: #888; /* 滚动条滑块背景色 */
  border-radius: 4px; /* 滚动条滑块圆角 */
}

::-webkit-scrollbar-thumb:hover {
  background: #555; /* 滚动条滑块悬停时背景色 */
}
</style>
