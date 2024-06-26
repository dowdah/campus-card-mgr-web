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
            <div class="info-value">{{ user.role.name }}</div>
          </div>
        </div>
        <div class="card-info">
          <h2 class="sub-heading">
            <router-link to="/cards">拥有的一卡通</router-link>
          </h2>
          <div class="info-table">
            <div class="info-row header">
              <div class="info-cell">卡号</div>
              <div class="info-cell">余额</div>
              <div class="info-cell">状态</div>
              <div class="info-cell">创建时间</div>
              <div class="info-cell">过期时间</div>
            </div>
            <div v-for="(card, index) in cards" :key="index" class="info-row">
              <div class="info-cell">{{ card.id }}</div>
              <div class="info-cell">{{ card.balance }} ¥</div>
              <div class="info-cell">{{ card.status }}</div>
              <div class="info-cell">{{ card.created_at }}</div>
              <div class="info-cell">{{ card.expires_at }}</div>
            </div>
          </div>
          <h2 class="sub-heading">
            <router-link to="/transactions">最近的交易</router-link>
          </h2>
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
              <div class="info-cell">{{ transaction.status }}</div>
            </div>
          </div>
        </div>
        <div class="permissions-info" v-if="user.role.name !== '普通用户'">
          <h2>你拥有的权限</h2>
          <p class="hint">此栏仅管理员可见，方便确认自己的权能</p>
          <div class="permission-table">
            <div v-for="(permission_number, permission_name, index) in permissions" :key="permission_number"
                 class="permission-row">
              <input type="checkbox" :id="permission_number" :disabled="true" :checked="hasPermission(permission_name)">
              <label :for="permission_number">{{ permission_name }}</label>
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

.user-info, .card-info, .permissions-info {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hint {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

h2 {
  margin-bottom: 10px;
  color: #333333;
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

.logout-button:not(:disabled):hover {
  background-color: #0056b3;
}

.logout-button:disabled {
  background-color: #ccc;
  color: #666;
  cursor: default;
}

.sub-heading a {
  color: #333333;
}

.permission-table {
  display: flex;
  flex-direction: row;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
}

.permission-row {
  display: flex;
  align-items: center;
  background-color: #f1f3f5;
  padding: 5px;
  border-radius: 4px;
}

.permission-row:hover {
  background-color: #e9ecef;
}



.permission-row input {
  margin-right: 10px;
}

.permission-row label {
  color: #333333;
}


</style>
<script>
import {mapActions, mapState, mapGetters} from 'vuex';

export default {
  name: 'Dashboard',
  computed: {
    ...mapState(['isLoading', 'user', 'permissions']),
    ...mapGetters(['cards', 'hasPermission'])
  },
  methods: {
    ...mapActions(['logout', 'setLoading']),
    logoutHandler() {
      this.logout().then(() => {
        this.$router.push({name: '主页'});
      });
    }
  }
};
</script>
