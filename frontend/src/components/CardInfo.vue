<template>
  <div>
    <div>
      <p>卡号: {{ card.id }}</p>
      <p>余额: {{ card.balance }}</p>
      <p>状态: {{ card.status }}</p>
    </div>
    <button @click="$emit('toggleCardDetails', card.id)">
      {{ showDetails ? '隐藏详情' : '显示详情' }}
    </button>
    <div v-if="showDetails">
      <div v-if="fetchedTransactions">
        <p>共 {{ responseData.total }} 条交易</p><p>当前页: {{ currentPage }}</p>
        <div>
          <label for="itemsPerPage">每页显示:</label>
          <select v-model="itemsPerPage">
            <option value="2">2</option>
            <option value="5">5</option>
            <option value="10">10</option>
          </select>
        </div>
        <p>共 {{ responseData.pages }} 页</p>
      <div v-for="transaction in responseData.card.transactions" :key="transaction.id">
        <p>交易ID: {{ transaction.id }}</p>
        <p>金额: {{ transaction.amount }}</p>
        <p>创建时间: {{ transaction.created_at }}</p>
        <p>当前余额: {{ transaction.current_balance }}</p>
        <p v-if="transaction.is_canceled">交易已取消</p>
      </div>
      <div>
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

<script>
import axios from 'axios';
import { BASE_API_URL } from '@/config/constants';
export default {
  name: 'CardInfo',
  emits: ['toggleCardDetails'],
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