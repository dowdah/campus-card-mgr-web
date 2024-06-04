<template>
  <div class="dashboard">
    <template v-if="user">
    <div class="user-info">
      <h2>用户信息</h2>
      <div class="info-row">
        <div class="info-label">姓名</div>
        <div class="info-value">{{ user.name }}</div>
      </div>
      <div class="info-row">
        <div class="info-label">邮箱</div>
        <div class="info-value">{{ user.email }}</div>
      </div>
      <div class="info-row">
        <div class="info-label">身份</div>
        <div class="info-value">{{ user.role }}</div>
      </div>
    </div>
        <div class="card-info">
      <h2>拥有的一卡通</h2>
      <div class="card-table">
        <div class="card-row header">
          <div class="card-cell">卡号</div>
          <div class="card-cell">余额</div>
        </div>
        <div v-for="(card, index) in user.cards" :key="index" class="card-row">
          <div class="card-cell">{{ card.id }}</div>
          <div class="card-cell">{{ card.balance }} ¥</div>
        </div>
      </div>
                <h2>最近的交易</h2>
      <div class="card-table">
        <div class="card-row header">
          <div class="card-cell">时间</div>
          <div class="card-cell">交易金额</div>
          <div class="card-cell">交易状态</div>
        </div>
        <div v-for="(transaction, index) in user.latest_transactions" :key="index" class="card-row">
          <div class="card-cell">{{ transaction.created_at }}</div>
          <div class="card-cell">{{ transaction.amount }} ¥</div>
          <div class="card-cell">{{ transaction.canceled ? "已取消":"正常" }}</div>
        </div>
      </div>
    </div>
    <button @click="logoutHandler" class="logout-button">登出</button>
    </template>
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
  max-width: 400px;
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

.info-row {
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

.card-table {
  display: table;
  width: 100%;
  border-collapse: collapse;
}

.card-row {
  display: table-row;
}

.card-cell {
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

.logout-button:hover {
  background-color: #0056b3;
}
</style>
<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'Dashboard',
  computed: {
    ...mapGetters(['isAuthenticated']),
    user() {
      return this.$store.state.user;
    }
  },
  methods: {
    ...mapActions(['logout']),
    logoutHandler() {
      this.logout().then(() => {
        this.$router.push({ name: 'Home' });
      });
    }
  }
};
</script>