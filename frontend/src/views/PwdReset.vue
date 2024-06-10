<template>
  <div class="reset-container">
    <h2>忘记密码</h2>
    <form @submit.prevent="request_email" class="reset-form" v-if="!email_sent">
      <div class="form-group">
        <label for="reset_choice">你还记得什么？</label>
        <select v-model="reset_choice" required>
          <option value="student_id">学号</option>
          <option value="email">邮箱</option>
          <option value="none">我什么也不记得</option>
        </select>
      </div>
      <div class="form-group" v-if="reset_choice === 'student_id'">
        <label for="student_id">学号</label>
        <input type="text" v-model="student_id" required />
      </div>
      <div class="form-group" v-if="reset_choice === 'email'">
        <label for="email">邮箱</label>
        <input type="email" v-model="email" required />
      </div>
      <div class="form-group" v-if="reset_choice === 'none'">
        <p class="mock-message"><span class="mock-icon">🤣👍</span>我们抱歉地通知您，您失去了您的账号，永远地。</p>
      </div>
      <button type="submit" class="email-button" v-if="reset_choice != 'none'">发送重置邮件</button>
    </form>
    <form v-else @submit.prevent="reset_pwd" class="reset-form">
    <div class="form-group" v-if="reset_choice === 'student_id'">
        <label for="student_id">学号</label>
        <input type="text" v-model="student_id" disabled />
      </div>
      <div class="form-group" v-if="reset_choice === 'email'">
        <label for="email">邮箱</label>
        <input type="email" v-model="email" disabled />
      </div>
      <div class="form-group">
        <label for="verification_code">验证码</label>
        <input type="text" v-model="token" required />
      </div>
      <div class="form-group">
        <label for="new_password">新密码</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit" class="email-button">重置密码</button>
    </form>
    <div v-if="email_sent" class="success-message"><span class="success-icon">✉️</span>重置邮件已发送，请查收。</div>
    <div v-if="pwd_reset" class="success-message"><span class="success-icon">✅</span>密码已重置。{{ countdown }} 秒后跳转到主页。</div>
    <div v-if="request_failed" class="error-message"><span class="error-icon">❎</span>{{ response_data.msg }}</div>
  </div>
</template>

<style scoped>
.reset-container {
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

.reset-form {
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

.email-button {
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.email-button:hover {
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

.mock-message {
  color: #ff4d4f;
  text-align: left;
  font-size: 1rem;
}

.success-message {
  margin-top: 1rem;
  padding: 0.75rem;
  border: 1px solid #52c41a;
  background-color: #f6ffed;
  color: #52c41a;
  border-radius: 4px;
  text-align: left;
  font-size: 0.875rem;
}

.error-icon, .mock-icon, .success-icon {
  margin-right: 0.5rem;
}
</style>

<script>
import { mapGetters, mapActions } from 'vuex';
import { BASE_API_URL } from '@/config/constants';
import axios from 'axios';
export default {
  name: 'PwdReset',
  data() {
    return {
      reset_choice: 'student_id',
      student_id: '',
      email: '',
      request_failed: false,
      response_data: {},
      email_sent: false,
      pwd_reset: false,
      token: '',
      password: '',
      countdown: 3
    };
  },
  computed: {
    ...mapGetters(['isAuthenticated']),
    request_email_url() {
      if (this.reset_choice === 'student_id') {
        return `${BASE_API_URL}/auth/reset-password?student_id=${this.student_id}`;
      } else if (this.reset_choice === 'email') {
        return `${BASE_API_URL}/auth/reset-password?email=${this.email}`;
      } else {
        return null;
      }
    },
    identifier() {
        return this.reset_choice === 'student_id' ? this.student_id : this.email;
      }
  },
  methods: {
    ...mapActions(['resetPassword']),
    async request_email() {
      try {
        const response = await axios.get(this.request_email_url);
        this.response_data = response.data;
        this.email_sent = true;
        this.request_failed = false;
      } catch (error) {
        this.request_failed = true;
        this.response_data = error.response.data;
      }
    },
    async reset_pwd() {
      try {
          await this.resetPassword({
      reset_choice: this.reset_choice,
      identifier: this.identifier,
      password: this.password,
      token: this.token
    });
          this.request_failed = false;
          this.pwd_reset = true;
    const countdownInterval = setInterval(() => {
      this.countdown--;
      if (this.countdown === 0) {
        clearInterval(countdownInterval);
        this.$router.push('/');
      }
    }, 1000);
        }
        catch (error) {
          this.request_failed = true;
          this.response_data = error.response.data;
        }
    }
  }
};
</script>