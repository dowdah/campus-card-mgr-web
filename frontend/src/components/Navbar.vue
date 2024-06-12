<template>
  <nav>
    <ul>
      <li><router-link to="/">主页</router-link></li>
      <template v-if="!isAuthenticated">
      <li><router-link to="/reset-pwd">忘记密码</router-link></li>
      </template>
      <template v-if="isAuthenticated">
      <li><router-link to="/cards">我的一卡通</router-link></li>
      </template>
    </ul>
  </nav>
</template>

<script>
import { mapGetters } from 'vuex';
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
  top:0;
  left:0;
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