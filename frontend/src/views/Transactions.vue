<template>
  <h4>我的交易</h4>
  <div>
    <label for="startDate">选择开始日期:</label>
    <input type="date" id="startDate" v-model="startDate" :max="aDayBeforeEndDate" class="no-input">
    <p>选择的日期是: {{ startDate }}</p>
  </div>
  <div>
    <label for="endDate">选择结束日期:</label>
    <input type="date" id="endDate" v-model="endDate" :max="getToday()" class="no-input">
    <p>选择的日期是: {{ endDate }}</p>
  </div>
  <div>
    <label for="cardId">选择卡号:</label>
    <select id="cardId" v-model="selectedCardId">
      <option value="">未选择</option>
      <option v-for="cardId in cardIds" :key="cardId" :value="cardId">{{ cardId }}</option>
    </select>
  </div>
  <div>
    <label for="transactionStatus">选择交易状态:</label>
    <select id="transactionStatus" v-model="transactionStatus">
      <option value="all">全部</option>
      <option value="normal">正常</option>
      <option value="canceled">已取消</option>
    </select>
  </div>
  <div>
    <label for="perPage">每页显示:</label>
    <select id="perPage" v-model="perPage">
      <option value="5">5</option>
      <option value="10">10</option>
      <option value="15">15</option>
    </select>
  <div>
    <label for="immidiateQuery">更改条件立即查询:</label>
    <input type="checkbox" id="immidiateQuery" v-model="immediateQuery">
    <button @click="queryHandler" :disabled="isLoading">查询</button>
  </div>
    <div v-if="requestFailed">
      <p>查询失败: {{ responseData.msg }}</p>
    </div>
    <div v-else-if="fetchedTransactions">
      <div>
        <p>交易数量: {{ responseData.total }}</p>
      </div>
      <p>页:（{{ currentPage }}/{{ responseData.pages }})</p>
      <div>
        <button @click="prevPage" :disabled="!responseData.has_prev">上一页</button>
        <button @click="nextPage" :disabled="!responseData.has_next">下一页</button>
      </div>
      <div>
        <table>
          <tr>
            <th>交易ID</th>
            <th>金额</th>
            <th>时间</th>
            <th>卡号</th>
            <th>交易前余额</th>
            <th>交易后余额</th>
            <th>状态</th>
          </tr>
          <tr v-for="transaction in responseData.transactions" :key="transaction.id">
            <td>{{ transaction.id }}</td>
            <td>{{ transaction.amount }}</td>
            <td>{{ transaction.created_at }}</td>
            <td>{{ transaction.card_id }}</td>
            <td>{{ transaction.original_balance }} ¥</td>
            <td>{{ transaction.current_balance }} ¥</td>
            <td v-if="transaction.is_canceled">交易已取消</td>
            <td v-else>正常</td>
          </tr>
        </table>
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
      immediateQuery: false
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
  }
}
</script>
