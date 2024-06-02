<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="loginHandler">
      <div>
        <label for="username">Username:</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      username: '',
      password: ''
    };
  },
  methods: {
    ...mapActions(['login']),
    async loginHandler() {
      console.log('Login form submitted');
      try {
        await this.login({ username: this.username, password: this.password });
        console.log('Login successful, navigating to Dashboard');
        console.log('Router instance:', this.$router);

        // 确保状态更新后再进行路由跳转
        this.$router.push({ name: 'Dashboard' }).then(() => {
          console.log('Navigated to Dashboard');
        }).catch((error) => {
          console.error('Navigation error:', error);
        });
      } catch (error) {
        console.error('Login failed', error);
      }
    }
  }
};
</script>