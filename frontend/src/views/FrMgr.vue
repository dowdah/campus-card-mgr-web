<template>
  <modal-window :show-modal="deleteFrData.showConfirmWindow" title="删除卡片" confirm-btn-text="删除"
                close-btn-text="取消"
                @confirm="deleteFr(deleteFrData.fr.id)" @close="clearDeleteFrData">
    <template v-slot:default>
      确定要删除该财务报表(生成者姓名: {{ deleteFrData.fr.user.name }}，报表ID: {{
        deleteFrData.fr.id
      }})吗？请注意你无法撤销删除操作！
    </template>
  </modal-window>
  <AlertWindow :show-alert="deleteFrData.responseData !== null"
               :title="deleteFrData.failed ? '删除失败' : '删除成功'"
               @confirm="clearDeleteFrResponse();">
  </AlertWindow>
  <AlertWindow :show-alert="newFrTask.taskStatus !== null"
               :title="newFrTask.taskStatus === 'SUCCESS' ? '创建成功' : '创建失败'"
               @confirm="clearNewFrTask">
    {{ newFrTask.taskStatus === 'SUCCESS' ? '财务报表创建成功！' : '财务报表创建失败！' }}
  </AlertWindow>
  <div class="fr-container">
    <h2 class="title">财务报表查询与管理</h2>
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
        <label for="totalIncomeGt">总收入大于</label>
        <input type="number" id="totalIncomeGt" v-model.lazy="queryInputs.floats.totalIncomeGt" min="0" step="0.01"
               :max="queryInputs.floats.totalIncomeGt" class="form-control"
               @blur="updateValue('floats.totalIncomeGt', $event)">
      </div>
      <div class="form-group">
        <label for="totalIncomeLt">总收入小于</label>
        <input type="number" id="totalIncomeLt" v-model.lazy="queryInputs.floats.totalIncomeLt"
               :min="queryInputs.floats.totalIncomeLt" step="0.01"
               class="form-control" @blur="updateValue('floats.totalIncomeLt', $event)">
      </div>
      <div class="form-group">
        <label for="totalExpensesGt">总支出大于</label>
        <input type="number" id="totalExpensesGt" v-model.lazy="queryInputs.floats.totalExpensesGt" min="0" step="0.01"
               :max="queryInputs.floats.totalExpensesGt" class="form-control"
               @blur="updateValue('floats.totalExpensesGt', $event)">
      </div>
      <div class="form-group">
        <label for="totalExpensesLt">总支出小于</label>
        <input type="number" id="totalExpensesLt" v-model.lazy="queryInputs.floats.totalExpensesLt"
               :min="queryInputs.floats.totalExpensesLt" step="0.01"
               class="form-control" @blur="updateValue('floats.totalExpensesLt', $event)">
      </div>
      <div class="form-group">
        <label for="id">财务报表ID</label>
        <input type="text" id="id" v-model.lazy="queryInputs.ints.id" class="form-control"
               @blur="updateValue('ints.id', $event)">
      </div>
      <div class="form-group">
        <label for="comments">财务报表备注</label>
        <input type="text" id="comments" v-model.lazy="queryInputs.strings.comments" class="form-control"
               @blur="updateValue('strings.comments', $event)">
      </div>
      <div class="form-group">
        <label for="isXlsxExpired">是否过期</label>
        <select id="isXlsxExpired" v-model="queryInputs.booleans.isXlsxExpired" class="form-control">
          <option value="">未选择</option>
          <option value="true">是</option>
          <option value="false">否</option>
        </select>
      </div>
      <div class="form-group">
        <label for="name">生成者姓名</label>
        <input type="text" id="name" v-model.lazy="queryInputs.user.name" class="form-control"
               @blur="updateValue('user.name', $event)">
      </div>
      <div class="form-group">
        <label for="id">生成者ID</label>
        <input type="text" id="id" v-model.lazy="queryInputs.user.id" class="form-control"
               @blur="updateValue('user.id', $event)">
      </div>
      <div class="form-group">
        <label for="email">生成者邮箱</label>
        <input type="text" id="email" v-model.lazy="queryInputs.user.email" class="form-control"
               @blur="updateValue('user.email', $event)">
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
      <button @click="newFr" class="btn btn-primary" v-if="hasPermission('GENERATE_REPORTS')"
              :disabled="newFrTask.taskId !== null">
        <template v-if="newFrTask.taskId === null">
          生成报告
        </template>
        <template v-else>
          生成中...
        </template>
      </button>
      <button v-if="!immediateQuery" @click="queryHandler" :disabled="isLoading" class="btn btn-primary">查询
      </button>
    </div>
    <div v-if="requestFailed" class="alert alert-danger">
      <p>查询失败: {{ responseData.msg }}</p>
    </div>
    <template v-else-if="fetchedFrs">
      <div class="results-summary">
        <p>财务报表数量: {{ responseData.total }}</p>
        <p>页:（{{ currentPage }}/{{ responseData.pages }})</p>
      </div>
      <div style="width: 100%;overflow-x: auto">
        <div class="fr-table">
          <table class="table">
            <thead>
            <tr>
              <th>生成者ID</th>
              <th>生成者姓名</th>
              <th>生成者邮箱</th>
              <th>财务报表ID</th>
              <th>生成时间</th>
              <th>总收入</th>
              <th>总支出</th>
              <th>净增长</th>
              <th>是否过期</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="fr in responseData.reports" :key="fr.id">
              <td>{{ fr.user.id }}</td>
              <td>{{ fr.user.name }}</td>
              <td>{{ fr.user.email }}</td>
              <td>{{ fr.id }}</td>
              <td>{{ fr.created_at }}</td>
              <td>{{ fr.total_income }}</td>
              <td>{{ fr.total_expenses }}</td>
              <td>{{ fr.net_growth }}</td>
              <td>{{ fr.is_xlsx_expired ? '是' : '否' }}</td>
              <td>{{ fr.comments === '' ? '无' : fr.comments }}</td>
              <td>
                <button @click="downloadFr(fr.id)" class="btn btn-primary"
                        v-if="hasPermission('EXPORT_REPORTS')">下载
                </button>
                <button @click="showDeleteModal(fr)" class="btn btn-primary btn-danger"
                        v-if="hasPermission('DEL_REPORTS')">
                  删除
                </button>
                <template
                    v-if="!(hasPermission('DEL_REPORTS') || hasPermission('EXPORT_REPORTS'))">
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

.fr-container {
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

.fr-table {
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

export default {
  name: 'FrMgr',
  components: {AlertWindow, ModalWindow},
  data() {
    return {
      responseData: {},
      currentPage: 1,
      perPage: 10,
      requestFailed: false,
      fetchedFrs: false,
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
          totalIncomeGt: '',
          totalIncomeLt: '',
          totalExpensesGt: '',
          totalExpensesLt: '',
          netGrowthGt: '',
          netGrowthLt: ''
        },
        booleans: {
          isXlsxExpired: ''
        },
        user: {
          id: '',
          email: '',
          name: ''
        }
      },
      deleteFrData: {
        fr: null,
        responseData: null,
        failed: false,
        showConfirmWindow: false
      },
      newFrTask: {
        taskStatus: null,
        taskId: null,
        intervalId: null
      }
    }
  },
  computed: {
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
    async fetchFrs(page, perPage) {
      this.setLoading(true);
      try {
        const response = await axios.post(`${BASE_API_URL}/fr/query?page=${page}&per_page=${perPage}`,
            this.requestData);
        this.fetchedFrs = true;
        this.requestFailed = false;
        this.responseData = response.data;
      } catch (error) {
        this.requestFailed = true;
        this.fetchedFrs = false;
        this.responseData = error.response.data;
      } finally {
        this.setLoading(false);
      }
    },
    queryHandler() {
      this.currentPage = 1;
      this.fetchFrs(this.currentPage, this.perPage);
    },
    updateValue(field, event) {
      if (field.includes(".")) {
        const [obj, key] = field.split(".");
        this.queryInputs[obj][key] = event.target.value;
      } else {
        this.queryInputs[field] = event.target.value;
      }
    },
    async deleteFr(frId) {
      this.clearDeleteFrData();
      this.setLoading(true);
      try {
        const response = await axios.delete(`${BASE_API_URL}/fr/rm/${frId}`);
        this.deleteFrData.responseData = response.data;
        this.deleteFrData.failed = false;
        await this.fetchFrs(this.currentPage, this.perPage);
      } catch (error) {
        this.deleteFrData.responseData = error.response.data;
        this.deleteFrData.failed = true;
      } finally {
        this.setLoading(false);
      }
    },
    showDeleteModal(fr) {
      this.deleteFrData.fr = fr;
      this.deleteFrData.showConfirmWindow = true;
    },
    clearDeleteFrData() {
      this.deleteFrData.showConfirmWindow = false;
      this.deleteFrData.fr = null;
    },
    clearDeleteFrResponse() {
      this.deleteFrData.responseData = null;
      this.deleteFrData.failed = false;
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
          totalIncomeGt: '',
          totalIncomeLt: '',
          totalExpensesGt: '',
          totalExpensesLt: '',
          netGrowthGt: '',
          netGrowthLt: ''
        },
        booleans: {
          isXlsxExpired: ''
        },
        user: {
          id: '',
          email: '',
          name: ''
        }
      }
    },
    async downloadFr(frId) {
      this.setLoading(true);
      try {
        const response = await axios.get(`${BASE_API_URL}/fr/get-dl-link/${frId}`);
        window.open(response.data.url);
      } catch (error) {
        return null;
      } finally {
        this.setLoading(false);
      }
    },
    async checkNewFrTaskStatus() {
      if (!this.newFrTask.taskId) {
        return;
      }
      try {
        const response = await axios.get(`${BASE_API_URL}/task/${this.newFrTask.taskId}`);
        if (response.data.task_status === 'SUCCESS') {
          clearInterval(this.newFrTask.intervalId);
          this.newFrTask.taskStatus = 'SUCCESS';
          this.newFrTask.taskId = null;
          await this.fetchFrs(this.currentPage, this.perPage);
        } else if (response.data.task_status === 'FAILURE') {
          clearInterval(this.newFrTask.intervalId);
          this.newFrTask.taskStatus = 'FAILURE';
          this.newFrTask.taskId = null;
        }
      } catch (error) {
        clearInterval(this.newFrTask.intervalId);
        this.newFrTask.taskStatus = 'FAILURE';
        this.newFrTask.taskId = null;
      }
    },
    async newFr() {
      this.setLoading(true);
      try {
        const response = await axios.get(`${BASE_API_URL}/fr/generate`);
        this.newFrTask.taskId = response.data.task_id;
        this.checkNewFrTaskStatus();
        // 为了确保在第一次调用 setInterval 之前就能立即获取任务状态，可以在设置定时器之前手动调用一次 this.checkNewFrTaskStatus()。
        // 这样可以避免等待2秒钟才开始第一次状态检查。
        this.intervalId = setInterval(async () => {
          await this.checkNewFrTaskStatus();
        }, 1000);
      } catch (error) {
        console.error('Error starting task:', error);
      } finally {
        this.setLoading(false)
      }
    },
    clearNewFrTask() {
      this.newFrTask.taskStatus = null;
      this.newFrTask.taskId = null;
      clearInterval(this.newFrTask.intervalId);
      this.newFrTask.intervalId = null;
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
        this.fetchFrs(newVal, this.perPage);
      }
    },
    perPage: {
      handler: function (newVal, oldVal) {
        this.currentPage = 1;
        this.fetchFrs(this.currentPage, newVal);
      }
    },
    requestData: {
      handler: function (newVal, oldVal) {
        this.currentPage = 1;
        if (this.immediateQuery) {
          this.fetchFrs(this.currentPage, this.perPage);
        }
      },
      deep: true
    }
  },
  created() {
    if (this.immediateQuery) {
      this.fetchFrs(this.currentPage, this.perPage)
    }
  }
}
</script>
