<template>
  <nav>
    <ul>
      <li v-for="route in filteredRoutes" :key="route.name">
        <router-link :to="route.path">{{ route.name }}</router-link>
      </li>
    </ul>
  </nav>
</template>

<script>
import {mapGetters, mapState, mapActions} from 'vuex';
import {useRouter} from 'vue-router';

export default {
  name: 'Navbar',
  data() {
    return {
      routes: [],
      filteredRoutes: []
    };
  },
  methods: {
    ...mapActions(['fetchPermissions']),
    filterRoutes() {
      this.filteredRoutes = this.routes.filter(route => {
        // 检查 requiresAuth
        if (route.meta) {
          if (route.meta.requiresAuth && !this.isAuthenticated) {
            console.log(`Exclude ${route.name} because it requires authentication.`)
            return false;
          }
          // 检查 blockWhenAuthenticated
          if (route.meta.blockWhenAuthenticated && this.isAuthenticated) {
            console.log(`Exclude ${route.name} because it blocks when authenticated.`)
            return false;
          }
          // 检查 requiresPermission
          if (route.meta.requiresPermission) {
            for (let permission of route.meta.requiresPermission) {
              if (!this.hasPermission(permission)) {
                console.log(`Exclude ${route.name} because it requires permission ${permission}.`)
                return false;
              }
            }
          }
        }
        return true;
      });
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'hasPermission']),
    ...mapState(['isInitialized', 'permissions'])
  },
  created() {
    const router = useRouter();
    this.routes = router.options.routes;
  },
  watch: {
    isInitialized: {
      immediate: true,
      handler(newVal, oldVal) {
        // 等待初始化后再过滤路由
        if (newVal) {
          this.filterRoutes();
        }
      }
    },
    isAuthenticated(newVal, oldVal) {
      // 在已经初始化，然后改变登录状态的情况下重新过滤路由
      if (this.isInitialized && this.permissions !== null) {
        this.filterRoutes();
      }
    },
    permissions(newVal, oldVal) {
      // 在刷新页面，首次登录后，等待权限初始化后再过滤路由
      if (newVal !== null && this.isAuthenticated) {
        this.filterRoutes();
      }
    }
  },
};
</script>

<style scoped>
nav {
  background-color: #1f1f1f;
  color: white;
  top: 0;
  left: 0;
  padding: 0.5em 1em;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  width: 100%;
  z-index: 1000;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
  justify-content: flex-start;
}

li {
  margin-right: 2em;
}

a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

a:hover {
  color: #6661ff;
  text-decoration: none;
}

a.router-link-exact-active {
  border-bottom: 2px solid #007bff;
}
</style>
