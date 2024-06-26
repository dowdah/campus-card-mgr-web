<template>
  <modal-window :show-modal="deleteUserData.showConfirmWindow" title="删除用户" confirm-btn-text="删除"
                close-btn-text="取消"
                @confirm="deleteUser(deleteUserData.user.id)" @close="clearDeleteUserData">
    <template v-slot:default>
      确定要删除该用户(姓名: {{ deleteUserData.user.name }}，学号: {{
        deleteUserData.user.student_id
      }})吗？请注意你无法撤销删除操作！
    </template>
  </modal-window>
  <AlertWindow :show-alert="deleteUserData.responseData !== null"
               :title="deleteUserData.failed ? '删除失败' : '删除成功'"
               @confirm="clearDeleteUserResponse">
    {{ deleteUserData.responseData.msg }}
  </AlertWindow>
  <transition name="user-editor">
    <UserEditor v-if="modifyUserData.showModifyWindow" :user="modifyUserData.user"
                @cancel="clearModifyUserData" @save="modifyUser"/>
  </transition>
  <AlertWindow :show-alert="modifyUserData.responseData !== null"
               :title="modifyUserData.failed ? '修改失败' : '修改成功'"
               @confirm="clearModifyUserResponse">
    {{ modifyUserData.responseData.msg }}
  </AlertWindow>
  <transition name="new-card-editor">
    <NewCardEditor v-if="newCardData.showNewCardWindow" :user="newCardData.user"
                   @cancel="clearNewCardData" @save="newCard"/>
  </transition>
  <AlertWindow :show-alert="newCardData.responseData !== null"
               :title="newCardData.failed ? '创建失败' : '创建成功'"
               @confirm="clearNewCardResponse">
    {{ newCardData.responseData.msg }}
  </AlertWindow>
  <transition name="new-user-editor">
    <NewUserEditor v-if="newUserData.showNewUserWindow" @cancel="newUserData.showNewUserWindow = false"
                   @submit="newUser"/>
  </transition>
  <AlertWindow :show-alert="newUserData.responseData !== null"
               :title="newUserData.failed ? '创建失败' : '创建成功'"
               @confirm="clearNewUserResponse">
    {{ newUserData.responseData.msg }}
  </AlertWindow>
  <div class="users-container">
    <h2 class="title">用户查询与管理</h2>
    <p class="hint">如果遇到性能问题，取消勾选“立即查询”</p>
    <div class="filters-group">
      <div class="form-group">
        <label for="startDate">开始日期</label>
        <input type="date" id="startDate" v-model="startDate" min="1970-01-01" :max="aDayBeforeEndDate"
               class="form-control no-input">
      </div>
      <div class="form-group">
        <label for="endDate">结束日期</label>
        <input type="date" id="endDate" v-model="endDate" min="1970-01-02" :max="getToday()"
               class="form-control no-input">
      </div>
      <div class="form-group">
        <label for="roleSelection">角色</label>
        <select id="roleSelection" v-model="roleSelection" class="form-control">
          <option value="all">未选择</option>
          <option v-for="(role, index) in role_names" :key="index" :value="role">{{ role }}</option>
        </select>
      </div>
      <div class="form-group">
        <label for="name">姓名</label>
        <input type="text" id="name" v-model.lazy="lazyInputs.name" class="form-control"
               @blur="updateValue('name', $event)">
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input type="text" id="email" v-model.lazy="lazyInputs.email" class="form-control"
               @blur="updateValue('email', $event)">
      </div>
      <div class="form-group">
        <label for="student_id">学号</label>
        <input type="text" id="student_id" v-model.lazy="lazyInputs.student_id" class="form-control"
               @blur="updateValue('student_id', $event)">
      </div>
      <div class="form-group">
        <label for="comments">备注</label>
        <input type="text" id="comments" v-model.lazy="lazyInputs.comments" class="form-control"
               @blur="updateValue('comments', $event)">
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
      <button @click="resetQuery" class="btn btn-primary" style="display: none">重置查询条件</button>
      <button @click="newUserData.showNewUserWindow = true" class="btn btn-primary" v-if="hasPermission('ADD_USER')">
        创建新用户
      </button>
      <button v-if="!immediateQuery" @click="queryHandler" :disabled="isLoading" class="btn btn-primary">查询
      </button>
    </div>
    <div v-if="requestFailed" class="alert alert-danger">
      <p>查询失败: {{ responseData.msg }}</p>
    </div>
    <template v-else-if="fetchedUsers">
      <div class="results-summary">
        <p>用户数量: {{ responseData.total }}</p>
        <p>页:（{{ currentPage }}/{{ responseData.pages }})</p>
      </div>
      <div style="width: 100%;overflow-x: auto">
        <div class="users-table">
          <table class="table">
            <thead>
            <tr>
              <th>ID</th>
              <th>学号</th>
              <th>创建时间</th>
              <th>邮箱</th>
              <th>邮箱已确认</th>
              <th>姓名</th>
              <th>角色</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="user in responseData.users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.student_id }}</td>
              <td>{{ user.created_at }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.confirmed ? '是' : '否' }}</td>
              <td>{{ user.name }}</td>
              <td>{{ user.role.name }}</td>
              <td>{{ user.comments === '' ? '无' : user.comments }}</td>
              <td>
                <button @click="showUserEditor(user)" class="btn btn-primary" v-if="hasPermission('MODIFY_USER_INFO')">
                  修改
                </button>
                <button @click="showNewCardEditor(user)" class="btn btn-primary" v-if="hasPermission('ADD_CARD')">
                  创建卡
                </button>
                <button @click="showDeleteModal(user)" class="btn btn-danger" v-if="hasPermission('DEL_USER')">
                  删除
                </button>
                <template
                    v-if="!(hasPermission('DEL_USER') || hasPermission('MODIFY_USER_INFO') || hasPermission('ADD_CARD'))">
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
.user-editor-enter-active,
.user-editor-leave-active {
  transition: opacity 100ms ease;
}

.user-editor-enter-from,
.user-editor-leave-to {
  opacity: 0;
}

.new-card-editor-enter-active,
.new-card-editor-leave-active {
  transition: opacity 100ms ease;
}

.new-card-editor-enter-from,
.new-card-editor-leave-to {
  opacity: 0;
}

.new-user-editor-enter-active,
.new-user-editor-leave-active {
  transition: opacity 100ms ease;
}

.new-user-editor-enter-from,
.new-user-editor-leave-to {
  opacity: 0;
}

input[type="date"].no-input {
  pointer-events: none;
}

input[type="date"].no-input::-webkit-calendar-picker-indicator {
  pointer-events: auto;
}

.users-container {
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

.users-table {
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

.table td button {
  margin: 0 5px;
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
import {BASE_API_URL, ROLE_NAMES} from '@/config/constants';
import ModalWindow from "../components/ModalWindow.vue";
import AlertWindow from "../components/AlertWindow.vue";
import UserEditor from "../components/UserEditor.vue";
import NewCardEditor from "../components/NewCardEditor.vue";
import NewUserEditor from "../components/NewUserEditor.vue";

export default {
  name: 'UserMgr',
  components: {UserEditor, AlertWindow, ModalWindow, NewCardEditor, NewUserEditor},
  data() {
    return {
      responseData: {},
      currentPage: 1,
      perPage: 10,
      requestFailed: false,
      fetchedUsers: false,
      startDate: null,
      endDate: this.getToday(),
      roleSelection: 'all',
      immediateQuery: true,
      role_names: ROLE_NAMES,
      lazyInputs: {
        name: '',
        email: '',
        student_id: '',
        comments: ''
      },
      deleteUserData: {
        user: null,
        responseData: null,
        failed: false,
        showConfirmWindow: false
      },
      modifyUserData: {
        user: null,
        responseData: null,
        failed: false,
        showModifyWindow: false
      },
      newCardData: {
        user: null,
        responseData: null,
        failed: false,
        showNewCardWindow: false
      },
      newUserData: {
        responseData: null,
        failed: false,
        showNewUserWindow: false
      }
    }
  },
  computed: {
    ...mapState(['isLoading', 'user']),
    ...mapGetters(['hasPermission']),
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
      };
      if (this.roleSelection !== 'all') {
        data['role_name'] = this.roleSelection;
      }
      for (let key in this.lazyInputs) {
        if (this.lazyInputs[key] !== '') {
          data[key] = this.lazyInputs[key];
        }
      }
      return data;
    },
    resetQuery() {
      this.startDate = null;
      this.endDate = this.getToday();
      this.roleSelection = 'all';
      this.lazyInputs = {
        name: '',
        email: '',
        student_id: '',
        comments: ''
      };
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
    async fetchUsers(page, perPage) {
      this.setLoading(true);
      try {
        const response = await axios.post(`${BASE_API_URL}/user/query?page=${page}&per_page=${perPage}`,
            this.requestData);
        this.fetchedUsers = true;
        this.requestFailed = false;
        this.responseData = response.data;
      } catch (error) {
        this.requestFailed = true;
        this.fetchedUsers = false;
        this.responseData = error.response.data;
      } finally {
        this.setLoading(false);
      }
    },
    queryHandler() {
      this.currentPage = 1;
      this.fetchUsers(this.currentPage, this.perPage);
    },
    updateValue(field, event) {
      this.lazyInputs[field] = event.target.value;
    },
    async deleteUser(userId) {
      this.clearDeleteUserData();
      this.setLoading(true);
      try {
        const response = await axios.delete(`${BASE_API_URL}/user/operate/${userId}`);
        this.deleteUserData.responseData = response.data;
        this.deleteUserData.failed = false;
        await this.fetchUsers(this.currentPage, this.perPage);
      } catch (error) {
        this.deleteUserData.responseData = error.response.data;
        this.deleteUserData.failed = true;
      } finally {
        this.setLoading(false);
      }
    },
    showDeleteModal(user) {
      this.deleteUserData.user = user;
      this.deleteUserData.showConfirmWindow = true;
    },
    clearDeleteUserData() {
      this.deleteUserData.showConfirmWindow = false;
      this.deleteUserData.user = null;
    },
    clearDeleteUserResponse() {
      this.deleteUserData.responseData = null;
      this.deleteUserData.failed = false;
    },
    showUserEditor(user) {
      this.modifyUserData.user = user;
      this.modifyUserData.showModifyWindow = true;
    },
    clearModifyUserData() {
      this.modifyUserData.showModifyWindow = false;
      this.modifyUserData.user = null;
    },
    clearModifyUserResponse() {
      this.modifyUserData.responseData = null;
      this.modifyUserData.failed = false;
    },
    async modifyUser(user, userId) {
      this.clearModifyUserData();
      this.setLoading(true);
      try {
        const response = await axios.put(`${BASE_API_URL}/user/operate/${userId}`, user);
        this.modifyUserData.responseData = response.data;
        this.modifyUserData.failed = false;
        await this.fetchUsers(this.currentPage, this.perPage);
      } catch (error) {
        this.modifyUserData.responseData = error.response.data;
        this.modifyUserData.failed = true;
      } finally {
        this.setLoading(false);
      }
    },
    showNewCardEditor(user) {
      this.newCardData.user = user;
      this.newCardData.showNewCardWindow = true;
    },
    clearNewCardData() {
      this.newCardData.showNewCardWindow = false;
      this.newCardData.user = null;
    },
    clearNewCardResponse() {
      this.newCardData.responseData = null;
      this.newCardData.failed = false;
    },
    async newCard(card, userId) {
      this.clearNewCardData();
      this.setLoading(true);
      try {
        const response = await axios.post(`${BASE_API_URL}/card/create/${userId}`, card);
        this.newCardData.responseData = response.data;
        this.newCardData.failed = false;
      } catch (error) {
        this.newCardData.responseData = error.response.data;
        this.newCardData.failed = true;
      } finally {
        this.setLoading(false);
      }
    },
    clearNewUserResponse() {
      this.newUserData.responseData = null;
      this.newUserData.failed = false;
    },
    async newUser(userData) {
      this.newUserData.showNewUserWindow = false;
      this.setLoading(true);
      try {
        const response = await axios.post(`${BASE_API_URL}/user/new`, userData);
        this.newUserData.responseData = response.data;
        this.newUserData.failed = false;
        await this.fetchUsers(this.currentPage, this.perPage);
      } catch (error) {
        this.newUserData.responseData = error.response.data;
        this.newUserData.failed = true;
      } finally {
        this.setLoading(false);
      }
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
        this.fetchUsers(newVal, this.perPage);
      }
    },
    perPage: {
      handler: function (newVal, oldVal) {
        this.currentPage = 1;
        this.fetchUsers(this.currentPage, newVal);
      }
    },
    requestData: {
      handler: function (newVal, oldVal) {
        this.currentPage = 1;
        if (this.immediateQuery) {
          this.fetchUsers(this.currentPage, this.perPage);
        }
      },
      deep: true
    }
  },
  created() {
    if (this.immediateQuery) {
      this.fetchUsers(this.currentPage, this.perPage)
    }
  }
}
</script>
