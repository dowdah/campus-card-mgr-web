<template>
  <div>
    <!-- 加载动画组件，通过:isLoading绑定loading状态 -->
    <LoadingSpinner :isLoading="loading" />
    <div class="login-container">
      <h2>登陆</h2>
      <!-- 登录表单，阻止默认提交行为 -->
      <form @submit.prevent="loginHandler" class="login-form">
        <!-- 登录方式选择 -->
        <div class="form-group">
          <label for="login_choice">登录方式</label>
          <select v-model="login_choice" required>
            <option value="student_id">学号</option>
            <option value="email">邮箱</option>
          </select>
        </div>
        <!-- 根据选择的登录方式显示对应输入框 -->
        <div class="form-group" v-if="login_choice === 'student_id'">
          <label for="student_id">学号</label>
          <input type="text" v-model="student_id" required />
        </div>
        <div class="form-group" v-if="login_choice === 'email'">
          <label for="email">邮箱</label>
          <input type="email" v-model="email" required />
        </div>
        <!-- 密码输入框 -->
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" v-model="password" required />
        </div>
        <!-- 提交按钮 -->
        <button type="submit" class="login-button" :disabled="loading">确认</button>
      </form>
      <!-- 登录失败信息显示 -->
      <div v-if="failed_login" class="error-message">
        <span class="error-icon">❎</span>{{ failed_response_data.msg }}
        <template v-if="failed_response_data.code === 401">
          <RouterLink to="/reset-pwd">忘记密码？</RouterLink>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  max-width: 400px;
  margin: auto;
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

.login-button:not(:disabled):hover {
  background-color: #0056b3;
}

.login-button:disabled {
  background-color: #ccc;
  color: #666;
  cursor: default;
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
  components: {
    LoadingSpinner
  },
  data() {
    return {
      login_choice: 'student_id', // 默认登录方式为学号
      student_id: '',
      email: '',
      password: '',
      failed_login: false, // 登录失败状态
      failed_response_data: {}, // 登录失败的响应数据
      loading: false // 加载状态
    };
  },
  computed: {
    credentials() {
      // 根据登录方式返回相应的凭证信息
      return this.login_choice === 'student_id'
        ? { student_id: this.student_id, password: this.password }
        : { email: this.email, password: this.password };
    }
  },
  methods: {
    ...mapActions(['login']),
    async loginHandler() {
      this.loading = true;
      try {
        await this.login(this.credentials);
        this.loading = false;
      } catch (error) {
        this.loading = false;
        this.failed_login = true;
        this.failed_response_data = error.response.data;
      }
    }
  }
};
</script>
