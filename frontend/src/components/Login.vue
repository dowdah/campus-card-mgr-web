<template>
  <div>
    <LoadingSpinner :isLoading="loading"></LoadingSpinner>
    <div class="login-container">
      <h2>登陆</h2>
      <form @submit.prevent="loginHandler" class="login-form">
        <div class="form-group">
          <label for="login_choice">登录方式</label>
          <select v-model="login_choice" required>
            <option value="student_id">学号</option>
            <option value="email">邮箱</option>
          </select>
        </div>
        <div class="form-group" v-if="login_choice === 'student_id'">
          <label for="student_id">学号</label>
          <input type="text" v-model="student_id" required />
        </div>
        <div class="form-group" v-if="login_choice === 'email'">
          <label for="email">邮箱</label>
          <input type="email" v-model="email" required />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" v-model="password" required />
        </div>
        <button type="submit" class="login-button">确认</button>
      </form>
      <div v-if="failed_login" class="error-message"><span class="error-icon">❎</span>{{ failed_response_data.msg }}
      <template v-if="failed_response_data.code==401">
        <RouterLink to="/reset-pwd">忘记密码？</RouterLink>
        </template>
      </div>
    </div>
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
  width: 100%;
}

label {
  margin-bottom: 0.5rem;
  color: #555;
}

select, input, .login-button {
  width: 100%;
  box-sizing: border-box;
}

input, select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input:focus, select:focus {
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
import LoadingSpinner from "./LoadingSpinner.vue";

export default {
  name: 'Login',
  data() {
    return {
      login_choice: 'student_id',
      student_id: '',
      email: '',
      password: '',
      failed_login: false,
      failed_response_data: {},
      loading: false
    };
  },
  components: {
    LoadingSpinner
  },
  computed: {
    credentials() {
      if(this.login_choice === 'student_id'){
        return { student_id: this.student_id, password: this.password };
      } else {
        return { email: this.email, password: this.password };
      }
    }
  },
  methods: {
    ...mapActions(['login']),
    async loginHandler() {
      console.log('Login form submitted');
      try {
        this.loading = true;
        await this.login(this.credentials);
      } catch (error) {
        this.loading = false;
        this.failed_login = true;
        this.failed_response_data = error.response.data;
      }
    }
  }
};
</script>