<template>
  <div class="simulation">
    <h2>交易模拟(充值与消费)</h2>
    <div class="card-info">
      <h2>可用的一卡通</h2>
      <div class="info-table" v-if="availableCards.length > 0">
        <div class="info-row header">
          <div class="info-cell">卡号</div>
          <div class="info-cell">余额</div>
          <div class="info-cell">创建时间</div>
          <div class="info-cell">过期时间</div>
        </div>
        <div v-for="(card, index) in availableCards" :key="index" class="info-row">
          <div class="info-cell">{{ card.id }}</div>
          <div class="info-cell">{{ card.balance }} ¥</div>
          <div class="info-cell">{{ card.created_at }}</div>
          <div class="info-cell">{{ card.expires_at }}</div>
        </div>
      </div>
      <div v-else>
        <p>没有可用的一卡通，无法进行模拟交易。</p>
      </div>
    </div>
    <template v-if="availableCards.length > 0">
      <div class="transaction-maker">
        <label>交易类型</label>
        <label for="recharge">
          <input type="radio" id="recharge" name="transactionType" value="recharge" v-model="transactionType">
          充值
        </label>
        <label for="consume">
          <input type="radio" id="consume" name="transactionType" value="consume" v-model="transactionType">
          消费
        </label>
        <label for="amount">交易金额</label>
        <input v-if="transactionType==='consume'" type="number" id="amount" v-model="amount" min="0" step="0.01"
               @blur="formatAmount" :max="maxConsumeAmount">
        <input v-if="transactionType==='recharge'" type="number" id="amount" v-model="amount" min="0" step="0.01"
               @blur="formatAmount"> ¥
        <label for="card">选择一卡通</label>
        <select id="card" v-model="selectedCard">
          <option value="" disabled>请选择一卡通</option>
          <option v-for="(card, index) in availableCards" :key="index" :value="card.id">{{ card.id }}</option>
        </select>
        <button @click="simulateTransaction" class="transaction-btn" :disabled="!postDataReady">模拟交易</button>
      </div>
      <div v-if="requestFailed" class="alert alert-danger"><p>交易失败: {{ responseData.msg }}</p></div>
      <div v-else-if="responseData" class="alert alert-success">
        <p>交易成功</p>
      </div>
      <div class="latest-transactions">
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
            <div class="info-cell">{{ transaction.status }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.simulation {
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

.card-info, .transaction-maker, .latest-transactions {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 10px;
  color: #333333;
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

.alert {
  padding: 10px;
  border-radius: 4px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
}

.transaction-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  align-self: stretch;
}

.transaction-btn:not(:disabled):hover {
  background-color: #0056b3;
}

.transaction-btn:disabled {
  background-color: #ccc;
  color: #666;
  cursor: default;
}

.transaction-maker {
  display: flex;
  flex-direction: row;
  gap: 10px;
  align-items: center;
}

.transaction-maker label {
  font-weight: bold;
}
</style>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import {BASE_API_URL} from '@/config/constants';
import axios from 'axios';

export default {
  name: 'TransactionSimulation',
  data() {
    return {
      transactionType: 'recharge',
      amount: 0,
      selectedCard: '',
      requestFailed: false,
      responseData: null
    }
  },
  computed: {
    ...mapState(['user', 'isLoading']),
    ...mapGetters(['cards']),
    availableCards() {
      return this.cards.filter(card => card.is_active)
    },
    postData() {
      return {
        card_id: this.selectedCard ? parseInt(this.selectedCard) : null,
        amount: parseFloat(this.amount),
        method: this.transactionType
      }
    },
    postDataReady() {
      return this.selectedCard && this.amount > 0
    },
    maxConsumeAmount() {
      if (this.selectedCard !== '') {
        const card = this.availableCards.find(card => card.id === parseInt(this.selectedCard));
        return card.balance;
      } else {
        return 0;
      }
    }
  },
  methods: {
    ...mapActions(['setLoading', 'init']),
    formatAmount() {
      // 使用toFixed方法将金额格式化为两位小数
      if (this.amount !== null) {
        if (this.transactionType === 'consume' && parseFloat(this.amount) > parseFloat(this.maxConsumeAmount)) {
          this.amount = this.maxConsumeAmount;
        }
        if (this.amount < 0) {
          this.amount = 0;
        }
        this.amount = parseFloat(this.amount).toFixed(2);
      }
    },
    async simulateTransaction() {
      this.setLoading(true);
      try {
        const response = await axios.post(`${BASE_API_URL}/transaction/my/make`, this.postData);
        await this.init();
        this.requestFailed = false;
        this.responseData = response.data;
      } catch (error) {
        this.requestFailed = true;
        this.responseData = error.response.data;
      } finally {
        this.setLoading(false);
      }
    }
  },
  watch: {
    selectedCard(newVal, oldVal) {
      if (this.transactionType === 'consume' && parseFloat(this.amount) > parseFloat(this.maxConsumeAmount)) {
        this.amount = parseFloat(this.maxConsumeAmount).toFixed(2);
      }
    },
    transactionType(newVal, oldVal) {
      console.log(`Amount: ${this.amount}, Max consume amount: ${this.maxConsumeAmount}`);
      if (newVal === 'consume' && parseFloat(this.amount) > parseFloat(this.maxConsumeAmount)) {
        console.log('Amount exceeds max consume amount');
        this.amount = parseFloat(this.maxConsumeAmount).toFixed(2);
      }
    }
  }
}
</script>
