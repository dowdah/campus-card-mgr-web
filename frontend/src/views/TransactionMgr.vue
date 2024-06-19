<template>
  <modal-window :show-modal="cancelTransactionData.showConfirmWindow" title="撤销交易" confirm-btn-text="确定"
                close-btn-text="取消"
                @confirm="cancelTransaction(cancelTransactionData.transaction.id)" @close="clearCancelTransactionData">
    <template v-slot:default>
      确定要撤销该交易(交易者姓名: {{ cancelTransactionData.transaction.user.name }}，交易ID: {{
        cancelTransactionData.transaction.id
      }})吗？请注意你无法回退该操作！
    </template>
  </modal-window>
  <AlertWindow :show-alert="cancelTransactionData.responseData !== null"
               :title="cancelTransactionData.failed ? '撤销失败' : '撤销成功'"
               @confirm="clearCancelTransactionResponse">
    {{ cancelTransactionData.responseData.msg }}
  </AlertWindow>
  <div class="transaction-container">
    <h2 class="title">交易查询与管理</h2>
    <p class="hint">如果遇到性能问题，取消勾选“立即查询”</p>
    <div class="filters-group">
      <div class="form-group">
        <label for="startDate">开始日期</label>
        <input type="date" id="startDate" v-model="queryInputs.strings.startDate" min="1970-01-01"
               :max="aDayBeforeEndDate"
               class="form-control no-input">
      </div>
      <div class="form-group">
        <label for="endDate">结束日期</label>
        <input type="date" id="endDate" v-model="queryInputs.strings.endDate" min="1970-01-02" :max="getToday()"
               class="form-control no-input">
      </div>
      <div class="form-group">
        <label for="amountGt">交易额大于</label>
        <input type="number" id="amountGt" v-model.lazy="queryInputs.floats.amountGt" min="0" step="0.01"
               :max="queryInputs.floats.amountLt" class="form-control"
               @blur="updateValue('floats.amountGt', $event)">
      </div>
      <div class="form-group">
        <label for="amountLt">交易额小于</label>
        <input type="number" id="amountLt" v-model.lazy="queryInputs.floats.amountLt"
               :min="queryInputs.floats.amountGt" step="0.01"
               class="form-control" @blur="updateValue('floats.amountLt', $event)">
      </div>
      <div class="form-group">
        <label for="id">交易ID</label>
        <input type="text" id="id" v-model.lazy="queryInputs.ints.id" class="form-control"
               @blur="updateValue('ints.id', $event)">
      </div>
      <div class="form-group">
        <label for="comments">交易备注</label>
        <input type="text" id="comments" v-model.lazy="queryInputs.strings.comments" class="form-control"
               @blur="updateValue('strings.comments', $event)">
      </div>
      <div class="form-group">
        <label for="isCanceled">是否撤销</label>
        <select id="isCanceled" v-model="queryInputs.booleans.isCanceled" class="form-control">
          <option value="">未选择</option>
          <option value="true">是</option>
          <option value="false">否</option>
        </select>
      </div>
      <div class="form-group">
        <label for="name">交易者姓名</label>
        <input type="text" id="name" v-model.lazy="queryInputs.user.name" class="form-control"
               @blur="updateValue('user.name', $event)">
      </div>
      <div class="form-group">
        <label for="id">交易者ID</label>
        <input type="text" id="id" v-model.lazy="queryInputs.user.id" class="form-control"
               @blur="updateValue('user.id', $event)">
      </div>
      <div class="form-group">
        <label for="studentId">交易者学号</label>
        <input type="text" id="studentId" v-model.lazy="queryInputs.user.studentId" class="form-control"
               @blur="updateValue('user.studentId', $event)">
      </div>
      <div class="form-group">
        <label for="email">交易者邮箱</label>
        <input type="text" id="email" v-model.lazy="queryInputs.user.email" class="form-control"
               @blur="updateValue('user.email', $event)">
      </div>
      <div class="form-group">
        <label for="card_id">交易卡号</label>
        <input type="text" id="card_id" v-model.lazy="queryInputs.card.id" class="form-control"
               @blur="updateValue('card.id', $event)">
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
    <div class="btn-group">
      <button @click="resetQueryInputs" class="btn btn-primary">重置查询条件</button>
      <button v-if="!immediateQuery" @click="queryHandler" :disabled="isLoading" class="btn btn-primary">查询
      </button>
    </div>
    <div v-if="requestFailed" class="alert alert-danger">
      <p>查询失败: {{ responseData.msg }}</p>
    </div>
    <template v-else-if="fetchedTransactions">
      <div class="results-summary">
        <p>交易数量: {{ responseData.total }}</p>
        <p>页:（{{ currentPage }}/{{ responseData.pages }})</p>
      </div>
      <div style="width: 100%;overflow-x: auto">
        <div class="transaction-table">
          <table class="table">
            <thead>
            <tr>
              <th>交易者ID</th>
              <th>交易者学号</th>
              <th>交易者姓名</th>
              <th>交易者邮箱</th>
              <th>卡号</th>
              <th>交易ID</th>
              <th>金额</th>
              <th>时间</th>
              <th>交易前余额</th>
              <th>交易后余额</th>
              <th>状态</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="transaction in responseData.transactions" :key="transaction.id">
              <td>{{ transaction.user.id }}</td>
              <td>{{ transaction.user.student_id }}</td>
              <td>{{ transaction.user.name }}</td>
              <td>{{ transaction.user.email }}</td>
              <td>{{ transaction.card_id }}</td>
              <td>{{ transaction.id }}</td>
              <td>{{ transaction.amount }}</td>
              <td>{{ transaction.created_at }}</td>
              <td>{{ transaction.original_balance }}</td>
              <td>{{ transaction.current_balance }}</td>
              <td>{{ transaction.status }}</td>
              <td>{{ transaction.comments === '' ? '无' : transaction.comments }}</td>
              <td>
                <button @click="showCancelModal(transaction)" class="btn btn-primary"
                        v-if="hasPermission('CANCEL_TRANSACTION')" :disabled="transaction.is_canceled">
                  撤销
                </button>
                <template
                    v-if="!(hasPermission('CANCEL_TRANSACTION'))">
                  无权限
                </template>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="pagination">
        <button @click="prevPage" :disabled="!responseData.has_prev" class="btn btn-secondary">上一页</button>
        <button @click="nextPage" :disabled="!responseData.has_next" class="btn btn-secondary">下一页</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
input[type="date"].no-input {
  pointer-events: none;
}

input[type="date"].no-input::-webkit-calendar-picker-indicator {
  pointer-events: auto;
}

.transaction-container {
  max-width: 1200px;
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

.btn-danger {
  background-color: #dc3545 !important;
}

.btn-danger:hover {
  background-color: #c82333 !important;
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

.transaction-table {
  margin-top: 20px;
  white-space: nowrap;
  width: max-content;
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

.table td button {
  margin: 0 5px;
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

.hint {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

.btn-group {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}
</style>

<script>
import {mapActions, mapState, mapGetters} from 'vuex';
import axios from 'axios';
import {BASE_API_URL} from '@/config/constants';
import ModalWindow from "../components/ModalWindow.vue";
import AlertWindow from "../components/AlertWindow.vue";
import cards from "./Cards.vue";

export default {
  name: 'TransactionMgr',
  components: {AlertWindow, ModalWindow},
  data() {
    return {
      responseData: {},
      currentPage: 1,
      perPage: 10,
      requestFailed: false,
      fetchedTransactions: false,
      immediateQuery: true,
      queryInputs: {
        ints: {
          id: ''
        },
        strings: {
          startDate: null,
          endDate: this.getToday(),
          comments: ''
        },
        floats: {
          amountGt: '',
          amountLt: ''
        },
        booleans: {
          isCanceled: ''
        },
        user: {
          studentId: '',
          id: '',
          email: '',
          name: ''
        },
        card: {
          id: ''
        }
      },
      cancelTransactionData: {
        transaction: null,
        responseData: null,
        failed: false,
        showConfirmWindow: false
      }
    }
  },
  computed: {
    cards() {
      return cards
    },
    ...mapState(['isLoading', 'user']),
    ...mapGetters(['hasPermission']),
    aDayBeforeEndDate() {
      const date = new Date(this.queryInputs.strings.endDate);
      date.setDate(date.getDate() - 1);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    requestData() {
      let data = {}
      for (let key in this.queryInputs.ints) {
        if (this.queryInputs.ints[key] !== '') {
          data[this.camelToSnake(key)] = parseInt(this.queryInputs.ints[key])
        }
      }
      for (let key in this.queryInputs.strings) {
        if (this.queryInputs.strings[key] !== null) {
          data[this.camelToSnake(key)] = this.queryInputs.strings[key]
        }
      }
      for (let key in this.queryInputs.booleans) {
        if (this.queryInputs.booleans[key] !== '') {
          data[this.camelToSnake(key)] = this.queryInputs.booleans[key] === 'true'
        }
      }
      for (let key in this.queryInputs.floats) {
        if (this.queryInputs.floats[key] !== '') {
          data[this.camelToSnake(key)] = parseFloat(this.queryInputs.floats[key])
        }
      }
      for (let key in this.queryInputs.user) {
        if (this.queryInputs.user[key] !== '') {
          data[`user_${this.camelToSnake(key)}`] = this.queryInputs.user[key]
        }
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
        const response = await axios.post(`${BASE_API_URL}/transaction/query?page=${page}&per_page=${perPage}`,
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
    },
    updateValue(field, event) {
      if (field.includes(".")) {
        const [obj, key] = field.split(".");
        this.queryInputs[obj][key] = event.target.value;
      } else {
        this.queryInputs[field] = event.target.value;
      }
    },
    async cancelTransaction(transactionId) {
      this.clearCancelTransactionData();
      this.setLoading(true);
      try {
        const response = await axios.get(`${BASE_API_URL}/transaction/cancel/${transactionId}`);
        this.cancelTransactionData.responseData = response.data;
        this.cancelTransactionData.failed = false;
        await this.fetchTransactions(this.currentPage, this.perPage);
      } catch (error) {
        this.cancelTransactionData.responseData = error.response.data;
        this.cancelTransactionData.failed = true;
      } finally {
        this.setLoading(false);
      }
    },
    showCancelModal(transaction) {
      this.cancelTransactionData.transaction = transaction;
      this.cancelTransactionData.showConfirmWindow = true;
    },
    clearCancelTransactionData() {
      this.cancelTransactionData.showConfirmWindow = false;
      this.cancelTransactionData.transaction = null;
    },
    clearCancelTransactionResponse() {
      this.cancelTransactionData.responseData = null;
      this.cancelTransactionData.failed = false;
    },
    camelToSnake(str) {
      return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
    },
    resetQueryInputs() {
      this.queryInputs = {
        ints: {
          id: ''
        },
        strings: {
          startDate: null,
          endDate: this.getToday(),
          comments: ''
        },
        floats: {
          amountGt: '',
          amountLt: ''
        },
        booleans: {
          isCanceled: ''
        },
        user: {
          studentId: '',
          id: '',
          email: '',
          name: ''
        },
        card: {
          id: ''
        }
      }

    }
  },
  watch: {
    'queryInputs.strings.endDate': function (newVal, oldVal) {
      if (newVal <= this.queryInputs.strings.startDate) {
        this.queryInputs.strings.startDate = this.aDayBeforeEndDate
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
        this.currentPage = 1;
        if (this.immediateQuery) {
          this.fetchTransactions(this.currentPage, this.perPage);
        }
      },
      deep: true
    }
  },
  created() {
    if (this.immediateQuery) {
      this.fetchTransactions(this.currentPage, this.perPage)
    }
  }
}
</script>
