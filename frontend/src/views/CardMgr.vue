<template>
  <modal-window :show-modal="deleteCardData.showConfirmWindow" title="删除卡片" confirm-btn-text="删除"
                close-btn-text="取消"
                @confirm="deleteCard(deleteCardData.card.id)" @close="clearDeleteCardData">
    <template v-slot:default>
      确定要删除该卡(持卡者姓名: {{ deleteCardData.card.user.name }}，卡号: {{
        deleteCardData.card.id
      }})吗？请注意你无法撤销删除操作！
    </template>
  </modal-window>
  <AlertWindow :show-alert="deleteCardData.responseData !== null"
               :title="deleteCardData.failed ? '删除失败' : '删除成功'"
               @confirm="clearDeleteCardResponse">
    {{ deleteCardData.responseData.msg }}
  </AlertWindow>
  <CardEditor v-if="modifyCardData.showModifyWindow" :card="modifyCardData.card"
              @cancel="clearModifyCardData" @save="modifyCard">
  </CardEditor>
  <AlertWindow :show-alert="modifyCardData.responseData !== null"
               :title="modifyCardData.failed ? '修改失败' : '修改成功'"
               @confirm="clearModifyCardResponse">
    {{ modifyCardData.responseData.msg }}
  </AlertWindow>
  <CardRenewWindow v-if="renewCardData.showRenewWindow" :card="renewCardData.card"
                   @close="clearRenewCardData" @confirm="renewCard">
  </CardRenewWindow>
  <AlertWindow :show-alert="renewCardData.responseData !== null"
               :title="renewCardData.failed ? '延期失败' : '延期成功'"
               @confirm="clearRenewCardResponse">
    {{ renewCardData.responseData.msg }}
  </AlertWindow>
  <div class="cards-container">
    <h2 class="title">一卡通查询与管理</h2>
    <p class="hint">如果遇到性能问题，取消勾选“立即查询”</p>
    <div class="filters-group">
      <div class="form-group">
        <label for="startCreatedDate">创建时间起始</label>
        <input type="date" id="startCreatedDate" v-model="queryInputs.strings.startCreatedDate"
               min="1970-01-01" :max="aDayBeforeEndCreatedDate" class="form-control">
      </div>
      <div class="form-group">
        <label for="endCreatedDate">创建时间结束</label>
        <input type="date" id="endCreatedDate" v-model="queryInputs.strings.endCreatedDate"
               min="1970-01-02" class="form-control">
      </div>
      <div class="form-group">
        <label for="startExpiresDate">过期时间起始</label>
        <input type="date" id="startExpiresDate" v-model="queryInputs.strings.startExpiresDate"
               min="1970-01-01" :max="aDayBeforeEndExpiresDate" class="form-control">
      </div>
      <div class="form-group">
        <label for="endExpiresDate">过期时间结束</label>
        <input type="date" id="endExpiresDate" v-model="queryInputs.strings.endExpiresDate"
               min="1970-01-02" class="form-control">
      </div>
      <div class="form-group">
        <label for="balanceGt">余额大于</label>
        <input type="number" id="balanceGt" v-model.lazy="queryInputs.floats.balanceGt" min="0" step="0.01"
               :max="queryInputs.floats.balanceLt" class="form-control"
               @blur="updateValue('floats.balanceGt', $event)">
      </div>
      <div class="form-group">
        <label for="balanceLt">余额小于</label>
        <input type="number" id="balanceLt" v-model.lazy="queryInputs.floats.balanceLt"
               :min="queryInputs.floats.balanceGt" step="0.01"
               class="form-control" @blur="updateValue('floats.balanceLt', $event)">
      </div>
      <div class="form-group">
        <label for="id">卡号</label>
        <input type="text" id="id" v-model.lazy="queryInputs.ints.id" class="form-control"
               @blur="updateValue('ints.id', $event)">
      </div>
      <div class="form-group">
        <label for="isBanned">是否禁用</label>
        <select id="isBanned" v-model="queryInputs.booleans.isBanned" class="form-control">
          <option value="">未选择</option>
          <option value="true">是</option>
          <option value="false">否</option>
        </select>
      </div>
      <div class="form-group">
        <label for="isExpired">是否过期</label>
        <select id="isExpired" v-model="queryInputs.booleans.isExpired" class="form-control">
          <option value="">未选择</option>
          <option value="true">是</option>
          <option value="false">否</option>
        </select>
      </div>
      <div class="form-group">
        <label for="isLost">是否挂失</label>
        <select id="isLost" v-model="queryInputs.booleans.isLost" class="form-control">
          <option value="">未选择</option>
          <option value="true">是</option>
          <option value="false">否</option>
        </select>
      </div>
      <div class="form-group">
        <label for="name">持卡者姓名</label>
        <input type="text" id="name" v-model.lazy="queryInputs.user.name" class="form-control"
               @blur="updateValue('user.name', $event)">
      </div>
      <div class="form-group">
        <label for="id">持卡者ID</label>
        <input type="text" id="id" v-model.lazy="queryInputs.user.id" class="form-control"
               @blur="updateValue('user.id', $event)">
      </div>
      <div class="form-group">
        <label for="student_id">持卡者学号</label>
        <input type="text" id="student_id" v-model.lazy="queryInputs.user.studentId" class="form-control"
               @blur="updateValue('user.studentId', $event)">
      </div>
      <div class="form-group">
        <label for="email">持卡者邮箱</label>
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
      <button v-if="!immediateQuery" @click="queryHandler" :disabled="isLoading" class="btn btn-primary btn-query">查询
      </button>
    </div>
    <div v-if="requestFailed" class="alert alert-danger">
      <p>查询失败: {{ responseData.msg }}</p>
    </div>
    <template v-else-if="fetchedCards">
      <div class="results-summary">
        <p>卡片数量: {{ responseData.total }}</p>
        <p>页:（{{ currentPage }}/{{ responseData.pages }})</p>
      </div>
      <div style="width: 100%;overflow-x: auto">
        <div class="cards-table">
          <table class="table">
            <thead>
            <tr>
              <th>持卡者ID</th>
              <th>持卡者学号</th>
              <th>持卡者姓名</th>
              <th>持卡者邮箱</th>
              <th>卡号</th>
              <th>创建时间</th>
              <th>过期时间</th>
              <th>余额</th>
              <th>是否过期</th>
              <th>是否挂失</th>
              <th>是否禁用</th>
              <th>操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="card in responseData.cards" :key="card.id">
              <td>{{ card.user.id }}</td>
              <td>{{ card.user.student_id }}</td>
              <td>{{ card.user.name }}</td>
              <td>{{ card.user.email }}</td>
              <td>{{ card.id }}</td>
              <td>{{ card.created_at }}</td>
              <td>{{ card.expires_at }}</td>
              <td>{{ card.balance }}</td>
              <td>{{ card.is_expired ? '是' : '否' }}</td>
              <td>{{ card.is_lost ? '是' : '否' }}</td>
              <td>{{ card.is_banned ? '是' : '否' }}</td>
              <td>
                <button @click="showCardEditor(card)" class="btn btn-primary"
                        v-if="hasPermission('CHANGE_CARD_STATUS') || hasPermission('CHANGE_CARD_BALANCE')">
                  修改
                </button>
                <button @click="showRenewWindow(card)" class="btn btn-primary" v-if="hasPermission('RENEW_CARD')">
                  延期
                </button>
                <button @click="showDeleteModal(card)" class="btn btn-danger" v-if="hasPermission('DEL_CARD')">
                  删除
                </button>
                <template
                    v-if="!(hasPermission('DEL_CARD') || hasPermission('CHANGE_CARD_STATUS') || hasPermission('CHANGE_CARD_BALANCE'))">
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

.cards-container {
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

.cards-table {
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
import CardEditor from "../components/CardEditor.vue";
import CardRenewWindow from "../components/CardRenewWindow.vue";

export default {
  name: 'CardMgr',
  components: {CardEditor, AlertWindow, ModalWindow, CardRenewWindow},
  data() {
    return {
      responseData: {},
      currentPage: 1,
      perPage: 10,
      requestFailed: false,
      fetchedCards: false,
      immediateQuery: true,
      queryInputs: {
        ints: {
          id: ''
        },
        strings: {
          startCreatedDate: null,
          endCreatedDate: this.getToday(),
          startExpiresDate: null,
          endExpiresDate: "2099-12-31"
        },
        floats: {
          balanceGt: '',
          balanceLt: ''
        },
        booleans: {
          isBanned: '',
          isExpired: '',
          isLost: ''
        },
        user: {
          studentId: '',
          id: '',
          email: '',
          name: ''
        }
      },
      deleteCardData: {
        card: null,
        responseData: null,
        failed: false,
        showConfirmWindow: false
      },
      modifyCardData: {
        card: null,
        responseData: null,
        failed: false,
        showModifyWindow: false
      },
      renewCardData: {
        card: null,
        responseData: null,
        failed: false,
        showRenewWindow: false
      }
    }
  },
  computed: {
    ...mapState(['isLoading', 'user']),
    ...mapGetters(['hasPermission']),
    aDayBeforeEndCreatedDate() {
      const date = new Date(this.queryInputs.strings.endCreatedDate);
      date.setDate(date.getDate() - 1);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    aDayBeforeEndExpiresDate() {
      const date = new Date(this.queryInputs.strings.endExpiresDate);
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
    async fetchCards(page, perPage) {
      this.setLoading(true);
      try {
        const response = await axios.post(`${BASE_API_URL}/card/query?page=${page}&per_page=${perPage}`,
            this.requestData);
        this.fetchedCards = true;
        this.requestFailed = false;
        this.responseData = response.data;
      } catch (error) {
        this.requestFailed = true;
        this.fetchedCards = false;
        this.responseData = error.response.data;
      } finally {
        this.setLoading(false);
      }
    },
    queryHandler() {
      this.currentPage = 1;
      this.fetchCards(this.currentPage, this.perPage);
    },
    updateValue(field, event) {
      if (field.includes(".")) {
        const [obj, key] = field.split(".");
        this.queryInputs[obj][key] = event.target.value;
      } else {
        this.queryInputs[field] = event.target.value;
      }
    },
    async deleteCard(cardId) {
      this.clearDeleteCardData();
      this.setLoading(true);
      try {
        const response = await axios.delete(`${BASE_API_URL}/card/rm/${cardId}`);
        this.deleteCardData.responseData = response.data;
        this.deleteCardData.failed = false;
        await this.fetchCards(this.currentPage, this.perPage);
      } catch (error) {
        this.deleteCardData.responseData = error.response.data;
        this.deleteCardData.failed = true;
      } finally {
        this.setLoading(false);
      }
    },
    showDeleteModal(card) {
      this.deleteCardData.card = card;
      this.deleteCardData.showConfirmWindow = true;
    },
    clearDeleteCardData() {
      this.deleteCardData.showConfirmWindow = false;
      this.deleteCardData.card = null;
    },
    clearDeleteCardResponse() {
      this.deleteCardData.responseData = null;
      this.deleteCardData.failed = false;
    },
    showCardEditor(card) {
      this.modifyCardData.card = card;
      this.modifyCardData.showModifyWindow = true;
    },
    clearModifyCardData() {
      this.modifyCardData.showModifyWindow = false;
      this.modifyCardData.card = null;
    },
    clearModifyCardResponse() {
      this.modifyCardData.responseData = null;
      this.modifyCardData.failed = false;
    },
    async modifyCard(card, cardId) {
      this.clearModifyCardData();
      this.setLoading(true);
      try {
        const response = await axios.put(`${BASE_API_URL}/card/set/${cardId}`, card);
        this.modifyCardData.responseData = response.data;
        this.modifyCardData.failed = false;
        await this.fetchCards(this.currentPage, this.perPage);
      } catch (error) {
        this.modifyCardData.responseData = error.response.data;
        this.modifyCardData.failed = true;
      } finally {
        this.setLoading(false);
      }
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
          startCreatedDate: null,
          endCreatedDate: this.getToday(),
          startExpiresDate: null,
          endExpiresDate: "2099-12-31"
        },
        floats: {
          balanceGt: '',
          balanceLt: ''
        },
        booleans: {
          isBanned: '',
          isExpired: '',
          isLost: ''
        },
        user: {
          studentId: '',
          id: '',
          email: '',
          name: ''
        }
      }
    },
    showRenewWindow(card) {
      this.renewCardData.card = card;
      this.renewCardData.showRenewWindow = true;
    },
    clearRenewCardData() {
      this.renewCardData.card = null;
      this.renewCardData.showRenewWindow = false;
    },
    clearRenewCardResponse() {
      this.renewCardData.responseData = null;
      this.renewCardData.failed = false;
    },
    async renewCard(card, cardId) {
      this.clearRenewCardData();
      this.setLoading(true);
      try {
        const response = await axios.put(`${BASE_API_URL}/card/renew/${cardId}`, card);
        this.renewCardData.responseData = response.data;
        this.renewCardData.failed = false;
        await this.fetchCards(this.currentPage, this.perPage);
      } catch (error) {
        this.renewCardData.responseData = error.response.data;
        this.renewCardData.failed = true;
      } finally {
        this.setLoading(false);
      }
    }
  },
  watch: {
    'queryInputs.strings.endCreatedDate': function (newVal, oldVal) {
      if (newVal && newVal <= this.queryInputs.strings.startCreatedDate) {
        this.queryInputs.strings.startCreatedDate = this.aDayBeforeEndCreatedDate;
      }
    },
    'queryInputs.strings.endExpiresDate': function (newVal, oldVal) {
      if (newVal && newVal <= this.queryInputs.strings.startExpiresDate) {
        this.queryInputs.strings.startExpiresDate = this.aDayBeforeEndExpiresDate;
      }
    },
    currentPage: {
      handler: function (newVal, oldVal) {
        this.fetchCards(newVal, this.perPage);
      }
    },
    perPage: {
      handler: function (newVal, oldVal) {
        this.currentPage = 1;
        this.fetchCards(this.currentPage, newVal);
      }
    },
    requestData: {
      handler: function (newVal, oldVal) {
        this.currentPage = 1;
        if (this.immediateQuery) {
          this.fetchCards(this.currentPage, this.perPage);
        }
      },
      deep: true
    }
  },
  created() {
    if (this.immediateQuery) {
      this.fetchCards(this.currentPage, this.perPage)
    }
  }
}
</script>
