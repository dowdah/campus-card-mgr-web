<template>
  <div class="login-container">
    <h2>登录</h2>
    <form @submit.prevent="loginHandler" class="login-form">
      <div class="form-group">
        <label for="student_id">学号</label>
        <input type="text" v-model="student_id" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit" class="login-button">确定</button>
    </form>
    <div v-if="failed_login" class="error-message"><span class="error-icon">❎</span>{{ failed_response_data.msg }}</div>
  </div>
</template>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

label {
  margin-bottom: 0.5rem;
  color: #555;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input:focus {
  border-color: #007bff;
  outline: none;
}

.login-button {
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #0056b3;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  border: 1px solid #ff4d4f;
  background-color: #fff1f0;
  color: #ff4d4f;
  border-radius: 4px;
  text-align: left;
  font-size: 0.875rem;
}

.error-icon {
  margin-right: 0.5rem;
}
</style>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'Login',
  data() {
    return {
      student_id: '',
      password: '',
      failed_login: false,
      failed_response_data: null
    };
  },
  methods: {
    ...mapActions(['login']),
    async loginHandler() {
      console.log('Login form submitted');
      try {
        await this.login({ student_id: this.student_id, password: this.password });
        console.log('Login successful, navigating to Dashboard');
        console.log('Router instance:', this.$router);

        // 确保状态更新后再进行路由跳转
        // this.$router.push({ name: 'Dashboard' }).then(() => {
        //   console.log('Navigated to Dashboard');
        // }).catch((error) => {
        //   console.error('Navigation error:', error);
        // });
      } catch (error) {
        this.failed_login = true;
        this.failed_response_data = error.response.data;
      }
    }
  }
};
</script>