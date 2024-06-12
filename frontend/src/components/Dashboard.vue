<template>
  <div>
    <div class="dashboard">
      <template v-if="user">
        <div class="user-info">
          <h2>用户信息</h2>
          <div class="userinfo-row">
            <div class="info-label">姓名</div>
            <div class="info-value">{{ user.name }}</div>
          </div>
          <div class="userinfo-row">
            <div class="info-label">学号</div>
            <div class="info-value">{{ user.student_id }}</div>
          </div>
          <div class="userinfo-row">
            <div class="info-label">邮箱</div>
            <div class="info-value">{{ user.email }}</div>
          </div>
          <div class="userinfo-row">
            <div class="info-label">身份</div>
            <div class="info-value">{{ user.role }}</div>
          </div>
        </div>
        <div class="card-info">
          <h2>拥有的一卡通</h2>
          <div class="info-table">
            <div class="info-row header">
              <div class="info-cell">卡号</div>
              <div class="info-cell">余额</div>
              <div class="info-cell">状态</div>
              <div class="info-cell">创建时间</div>
              <div class="info-cell">过期时间</div>
            </div>
            <div v-for="(card, index) in user.cards" :key="index" class="info-row">
              <div class="info-cell">{{ card.id }}</div>
              <div class="info-cell">{{ card.balance }} ¥</div>
              <div class="info-cell">{{ card.status }}</div>
              <div class="info-cell">{{ card.created_at }}</div>
              <div class="info-cell">{{ card.expires_at }}</div>
            </div>
          </div>
          <h2>最近的交易</h2>
          <div class="info-table">
            <div class="info-row header">
              <div class="info-cell">时间</div>
              <div class="info-cell">卡号</div>
              <div class="info-cell">交易金额</div>
              <div class="info-cell">原金额</div>
              <div class="info-cell">新金额</div>
              <div class="info-cell">交易状态</div>
            </div>
            <div v-for="(transaction, index) in user.latest_transactions" :key="index" class="info-row">
              <div class="info-cell">{{ transaction.created_at }}</div>
              <div class="info-cell">{{ transaction.card_id }}</div>
              <div class="info-cell">{{ transaction.amount }} ¥</div>
              <div class="info-cell">{{ transaction.original_balance }} ¥</div>
              <div class="info-cell">{{ transaction.current_balance }} ¥</div>
              <div class="info-cell">{{ transaction.is_canceled ? "已取消" : "正常" }}</div>
            </div>
          </div>
        </div>
        <button @click="logoutHandler" class="logout-button" :disabled="isLoading">登出</button>
      </template>
    </div>
  </div>
</template>


<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  align-items: stretch;
  max-width: 800px;
  margin: 0 auto;
}

.user-info, .card-info {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 10px;
  color: #333333;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.userinfo-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #e9ecef;
}

.info-label {
  font-weight: bold;
  color: #333333;
  text-align: left;
}

.info-value {
  color: #555555;
  text-align: right;
}

.info-table {
  display: table;
  width: 100%;
  border-collapse: collapse;
}

.info-row {
  display: table-row;
}

.info-cell {
  display: table-cell;
  padding: 10px;
  border: 1px solid #e9ecef;
  text-align: center;
}

.header {
  background-color: #f1f3f5;
  font-weight: bold;
}

.logout-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  align-self: stretch;
}

.login-button:not(:disabled):hover {
  background-color: #0056b3;
}

.login-button:disabled {
  background-color: #ccc;
  color: #666;
  cursor: default;
}
</style>
<script>
import {mapActions, mapState} from 'vuex';

export default {
  name: 'Dashboard',
  computed: {
    ...mapState(['isLoading', 'user']),
  },
  methods: {
    ...mapActions(['logout', 'setLoading']),
    logoutHandler() {
      this.logout().then(() => {
        this.$router.push({name: 'Home'});
      });
    }
  }
};
</script>
