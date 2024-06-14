<template>
  <div class="confirm-container">
    <h2>验证你的邮箱！</h2>
    <form @submit.prevent="confirmEmail" class="confirm-form">
      <div class="form-group">
        <label for="student_id">学号</label>
        <input type="text" v-model="student_id" disabled/>
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input type="email" v-model="email" disabled/>
      </div>
      <div class="form-group">
        <label for="verification_code">验证码</label>
        <input type="text" v-model="token" required/>
      </div>
      <button @click="sendEmail" class="email-button" v-if="!emailSent" type="button" :disabled="isLoading">发送验证码
      </button>
      <button type="submit" class="submit-button" v-else :disabled="isLoading">提交</button>
      <button class="logout-button" @click="logoutHandler" type="button" :disabled="isLoading">登出</button>
    </form>
    <div v-if="emailSent" class="success-message"><span class="success-icon">✉️</span>验证码邮件已发送，请查收。</div>
    <div v-if="emailConfirmed" class="success-message"><span class="success-icon">✅</span>邮箱已确认。{{ countdown }}
      秒后页面跳转。
    </div>
    <div v-if="requestFailed" class="error-message"><span class="error-icon">❎</span>{{ responseData.msg }}</div>
  </div>
</template>

<style scoped>
.confirm-container {
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

.confirm-form {
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

.submit-button, .email-button {
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover, .email-button:hover {
  background-color: #0056b3;
}

.logout-button {
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  background-color: #ff4d4f;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #ff1a1a;
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

.error-icon, .success-icon {
  margin-right: 0.5rem;
}
</style>

<script>
import {mapGetters, mapActions, mapState} from 'vuex';
import {BASE_API_URL} from '@/config/constants';
import axios from 'axios';

export default {
  name: 'Unconfirmed',
  data() {
    return {
      student_id: this.$store.state.user.student_id,
      email: this.$store.state.user.email,
      token: '',
      emailSent: false,
      emailConfirmed: false,
      requestFailed: false,
      responseData: {},
      countdown: 3
    };
  },
  computed: {
    ...mapGetters(['isAuthenticated']),
    ...mapState(['isLoading'])
  },
  methods: {
    ...mapActions(['logout', 'setLoading']),
    logoutHandler() {
      this.logout().then(() => {
        this.$router.push({name: '主页'});
      });
    },
    sendEmail() {
      this.setLoading(true)
      axios.get(`${BASE_API_URL}/auth/send-confirmation`)
          .then(() => {
            this.emailSent = true;
          })
          .catch(err => {
            this.requestFailed = true;
            this.responseData = err.response.data;
          })
          .finally(() => {
            this.setLoading(false);
          });
    },
    confirmEmail() {
      this.setLoading(true)
      axios.get(`${BASE_API_URL}/auth/confirm/${this.token}`)
          .then(() => {
            this.emailConfirmed = true;
            this.requestFailed = false;
            const interval = setInterval(() => {
              this.countdown--;
              if (this.countdown === 0) {
                clearInterval(interval);
                window.location.reload();
              }
            }, 1000);
          })
          .catch(err => {
            this.requestFailed = true;
            this.responseData = err.response.data;
          })
          .finally(() => {
            this.setLoading(false);
          });
    }
  }
}
</script>
