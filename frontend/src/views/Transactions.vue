<template>
  <div class="transactions-container">
    <h2 class="title">我的交易</h2>
    <p class="hint">如果遇到性能问题，取消勾选“立即查询”</p>
    <div class="filters-group">
      <div class="form-group">
        <label for="startDate">开始日期</label>
        <input type="date" id="startDate" v-model="startDate" :max="aDayBeforeEndDate" min="1970-01-01" class="form-control no-input">
      </div>
      <div class="form-group">
        <label for="endDate">结束日期</label>
        <input type="date" id="endDate" v-model="endDate" :max="getToday()" class="form-control no-input">
      </div>
      <div class="form-group">
        <label for="cardId">卡号</label>
        <select id="cardId" v-model="selectedCardId" class="form-control">
          <option value="">未选择</option>
          <option v-for="cardId in cardIds" :key="cardId" :value="cardId">{{ cardId }}</option>
        </select>
      </div>
      <div class="form-group">
        <label for="transactionStatus">交易状态</label>
        <select id="transactionStatus" v-model="transactionStatus" class="form-control">
          <option value="all">全部</option>
          <option value="normal">正常</option>
          <option value="canceled">已取消</option>
        </select>
      </div>
      <div class="form-group">
        <label for="perPage">每页显示</label>
        <select id="perPage" v-model="perPage" class="form-control">
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="15">15</option>
        </select>
      </div>
      <div class="form-group">
        <label for="immediateQuery">立即查询</label>
        <input type="checkbox" id="immediateQuery" v-model="immediateQuery" class="form-control">
      </div>
    </div>
    <button v-if="!immediateQuery" @click="queryHandler" :disabled="isLoading" class="btn btn-primary query-btn">查询</button>
    <div v-if="requestFailed" class="alert alert-danger">
      <p>查询失败: {{ responseData.msg }}</p>
    </div>
    <div v-else-if="fetchedTransactions">
      <div class="results-summary">
        <p>交易数量: {{ responseData.total }}</p>
        <p>页:（{{ currentPage }}/{{ responseData.pages }})</p>
      </div>
      <div class="transactions-table">
        <table class="table">
          <thead>
            <tr>
              <th>交易ID</th>
              <th>金额</th>
              <th>时间</th>
              <th>卡号</th>
              <th>交易前余额</th>
              <th>交易后余额</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in responseData.transactions" :key="transaction.id">
              <td>{{ transaction.id }}</td>
              <td>{{ transaction.amount }} ¥</td>
              <td>{{ transaction.created_at }}</td>
              <td>{{ transaction.card_id }}</td>
              <td>{{ transaction.original_balance }} ¥</td>
              <td>{{ transaction.current_balance }} ¥</td>
              <td>{{ transaction.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
            <div class="pagination">
        <button @click="prevPage" :disabled="!responseData.has_prev" class="btn btn-secondary">上一页</button>
        <button @click="nextPage" :disabled="!responseData.has_next" class="btn btn-secondary">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
input[type="date"].no-input {
  pointer-events: none;
}

input[type="date"].no-input::-webkit-calendar-picker-indicator {
  pointer-events: auto;
}

.transactions-container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.filters-group {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
  justify-content: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-control {
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
  width: 200px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #007BFF;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn:disabled {
  background-color: #ccc;
}

.btn:hover {
  background-color: #0056b3;
}

.btn:disabled:hover {
  background-color: #ccc;
}

.alert {
  padding: 10px;
  border-radius: 5px;
  background-color: #f8d7da;
  color: #721c24;
  margin-top: 20px;
}

.results-summary {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.transactions-table {
  margin-top: 20px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  cursor: default;
}

.table th,
.table td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: center;
}

.table th {
  background-color: #f1f1f1;
}

.table tbody tr:nth-child(even) {
  background-color: #ffffff;
}

.table tbody tr:hover {
  background-color: #f1f1f1;
}

.title {
  text-align: center;
  margin-bottom: 20px;
}

.query-btn {
  margin-top: 20px;
}

.hint {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}
</style>

<script>
import {mapActions, mapState} from 'vuex';
import axios from 'axios';
import {BASE_API_URL} from '@/config/constants';

export default {
  name: 'Transactions',
  data() {
    return {
      responseData: {},
      currentPage: 1,
      perPage: 10,
      requestFailed: false,
      fetchedTransactions: false,
      selectedCardId: '',
      startDate: null,
      endDate: this.getToday(),
      transactionStatus: 'all',
      immediateQuery: true
    }
  },
  computed: {
    ...mapState(['isLoading', 'user']),
    cardIds() {
      return this.user.cards.map(card => card.id).sort((a, b) => a - b);
    },
    aDayBeforeEndDate() {
      const date = new Date(this.endDate);
      date.setDate(date.getDate() - 1);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    requestData() {
      let data = {
        start_date: this.startDate ? this.startDate : null,
        end_date: this.endDate ? this.endDate : null,
        card_id: this.selectedCardId ? this.selectedCardId : null
      };
      if (this.transactionStatus !== 'all') {
        data['is_canceled'] = this.transactionStatus === 'canceled';
      }
      return data;
    }
  },
  methods: {
    ...mapActions(['setLoading']),
    getToday() {
      const today = new Date();
      const year = today.getFullYear();
      const month = today.getMonth() + 1;
      const day = today.getDate() + 1;
      return `${year}-${month < 10 ? '0' + month : month}-${day < 10 ? '0' + day : day}`;
    },
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
    async fetchTransactions(page, perPage) {
      this.setLoading(true);
      try {
        const response = await axios.post(`${BASE_API_URL}/transaction/my/query?page=${page}&per_page=${perPage}`,
            this.requestData);
        this.fetchedTransactions = true;
        this.requestFailed = false;
        this.responseData = response.data;
      } catch (error) {
        this.requestFailed = true;
        this.fetchedTransactions = false;
        this.responseData = error.response.data;
      } finally {
        this.setLoading(false);
      }
    },
    queryHandler() {
      this.currentPage = 1;
      this.fetchTransactions(this.currentPage, this.perPage);
    }
  },
  watch: {
    endDate: function (newVal, oldVal) {
      if (newVal <= this.startDate) {
        this.startDate = this.aDayBeforeEndDate
      }
    },
    currentPage: {
      handler: function (newVal, oldVal) {
        this.fetchTransactions(newVal, this.perPage);
      }
    },
    perPage: {
      handler: function (newVal, oldVal) {
        this.currentPage = 1;
        this.fetchTransactions(this.currentPage, newVal);
      }
    },
    requestData: {
      handler: function (newVal, oldVal) {
        if (this.immediateQuery) {
          this.fetchTransactions(this.currentPage, this.perPage);
        }
      },
      deep: true
    }
  },
  created() {
    if (this.immediateQuery){
      this.fetchTransactions(this.currentPage, this.perPage);
    }
  }
}
</script>
