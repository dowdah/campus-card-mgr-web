<template>
  <nav>
    <ul>
      <li><router-link to="/">Home</router-link></li>
      <li v-if="!isAuthenticated"><router-link to="/login">Login</router-link></li>
      <li v-if="isAuthenticated"><router-link to="/dashboard">Dashboard</router-link></li>
    </ul>
  </nav>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
export default {
  name: 'Navbar',
  computed: {
    ...mapGetters(['isAuthenticated'])
  }
}
</script>

<style scoped>
nav {
  background-color: #1f1f1f;
  color: white;
  padding: 0.5em 1em;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  width: 100%;
  top: 0;
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
  color: #ff6f61;
  text-decoration: none;
}

a.router-link-exact-active {
  border-bottom: 2px solid #ff6f61;
}
</style>