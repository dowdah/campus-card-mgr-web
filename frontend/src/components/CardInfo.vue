<template>
  <div class="card-info">
    <div class="card-summary">
      <table>
        <tr>
          <td>卡号:</td>
          <td>{{ card.id }}</td>
        </tr>
        <tr>
          <td>余额:</td>
          <td>{{ card.balance }}</td>
        </tr>
        <tr>
          <td>状态:</td>
          <td>{{ card.status }}</td>
        </tr>
        <tr>
          <td>创建时间:</td>
          <td>{{ card.created_at }}</td>
        </tr>
        <tr v-if="fetchedTransactions">
          <td>交易数量:</td>
          <td>{{ responseData.total }}</td>
        </tr>
      </table>
    </div>
    <button @click="$emit('reportLost', card.id)" v-if="!card.is_lost" class="report-lost-button">挂失</button>
    <button @click="$emit('toggleCardDetails', card.id)">
      {{ showDetails ? '隐藏交易' : '显示交易' }}
    </button>
    <div v-if="showDetails" class="details">
      <div v-if="fetchedTransactions">
        <div class="transactions-summary">
          <div class="transaction-controls">
          <p>页:（{{ currentPage }}/{{ responseData.pages }})</p>
          <div class="page-size-selector">
            <label for="itemsPerPage">每页显示:</label>
            <select v-model="itemsPerPage">
              <option value="2">2</option>
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
          </div>
            </div>
        </div>
        <div class="transaction-list">
          <table>
            <tr>
              <th>交易ID</th>
              <th>金额</th>
              <th>创建时间</th>
              <th>交易前余额</th>
              <th>交易后余额</th>
              <th>状态</th>
            </tr>
            <tr v-for="transaction in responseData.card.transactions" :key="transaction.id" class="transaction">
              <td>{{ transaction.id }}</td>
              <td>{{ transaction.amount }}</td>
              <td>{{ transaction.created_at }}</td>
              <td>{{ transaction.original_balance }} ¥</td>
              <td>{{ transaction.current_balance }} ¥</td>
              <td v-if="transaction.is_canceled">交易已取消</td>
              <td v-else>正常</td>
            </tr>
          </table>
        </div>
        <div class="pagination-buttons">
          <button @click="prevPage" :disabled="!responseData.has_prev">上一页</button>
          <button @click="nextPage" :disabled="!responseData.has_next">下一页</button>
        </div>
      </div>
      <div v-else-if="fetchedFailed">
        <p>获取交易失败: {{ responseData.msg }}</p>
      </div>
      <div v-else>
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-info {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  font-family: 'Arial', sans-serif;
  border: 1px solid #ccc;
  padding: 20px;
  border-radius: 8px;
  max-width: 600px;
  margin: 2em auto;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  background-color: white;
}

.card-summary table {
  width: 100%;
}

.card-summary td {
  padding: 5px;
}

.card-summary td:first-child {
  font-weight: bold;
}

button {
  margin: 10px;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background-color: #007BFF;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3;
}

button:disabled {
  background-color: #ccc;
}

.details {
  animation: fadeIn 0.3s;
}

.transactions-summary, .transaction-list, .pagination-buttons {
  width: 100%;
  margin-top: 10px;
}

.page-size-selector {
display: flex;
  align-items: center;
}

.transaction {
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.transaction-list table {
  width: 100%;
}

.transaction-list th {
  padding: 10px;
  background-color: #f2f2f2;
  font-weight: bold;
  text-align: left;
}

.transaction-list td {
  padding: 10px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.transaction-controls {
  display: flex;
  justify-content: space-between;
}

.report-lost-button {
  margin: 10px;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background-color: #dc3545;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.report-lost-button:hover {
  background-color: #c82333;
}
</style>

<script>
import axios from 'axios';
import { BASE_API_URL } from '@/config/constants';
export default {
  name: 'CardInfo',
  emits: ['toggleCardDetails', 'reportLost'],
  props: {
    card: {
      type: Object,
      required: true
    },
    showDetails: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 2,
      responseData: {},
      fetchedTransactions: false,
      fetchedFailed: false
    };
  },
  methods: {
    nextPage() {
      if (this.responseData.has_next) {
        this.currentPage = this.responseData.next_num;
      }
    },
    prevPage() {
      if (this.responseData.has_prev) {
        this.currentPage = this.responseData.prev_num;
      }
    },
    async fetchTransactions(page, per_page) {
      try {
        const response = await axios.get(`${BASE_API_URL}/card/my/${this.card.id}?page=${page}&per_page=${per_page}`);
        this.fetchedTransactions = true;
        this.fetchedFailed = false;
        this.responseData = response.data;
      } catch (error) {
        this.fetchedFailed = true;
        this.fetchedTransactions = false;
        this.responseData = error.response.data;
      }
    }
  },
  watch: {
    currentPage: {
      handler: function(newVal, oldVal) {
        this.fetchTransactions(newVal, this.itemsPerPage);
      }
    },
    itemsPerPage: {
      handler: function(newVal, oldVal) {
        this.fetchTransactions(this.currentPage, newVal);
      }
    },
    showDetails: {
      handler: function(newVal, oldVal) {
        if (newVal && !this.fetchedTransactions) {
          this.fetchTransactions(this.currentPage, this.itemsPerPage);
        }
      }
    }
  }
};
</script>