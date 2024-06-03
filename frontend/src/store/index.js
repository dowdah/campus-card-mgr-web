import { createStore } from 'vuex';
import axios from 'axios';

const store = createStore({
  state: {
    user: null
  },
  mutations: {
    setUser(state, user) {
      const roleTranslations = {
        'SchoolStaff': '学校管理员',
        'SiteOperator': '网站运营者',
        'User': '普通用户',
      };
      user.role = roleTranslations[user.role] || user.role;
      state.user = user;
    },
    clearUser(state) {
      state.user = null;
    }
  },
  actions: {
    async login({ commit }, credentials) {
      console.log('Login action called with credentials:', credentials);
      try {
        const response = await axios.post('/api/v1/login', credentials);
        console.log('Login response:', response.data);
        localStorage.setItem('token', response.data.token);
        axios.defaults.headers.common['Authorization'] = 'Basic ' + btoa(response.data.token + ':');
        commit('setUser', response.data.user);
        commit('setInitialized', true); // 设置初始化状态
      } catch (error) {
        console.error('Login action failed', error);
        throw error;
      }
    },
    async logout({ commit }) {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      commit('clearUser');
      commit('setInitialized', false); // 重置初始化状态
    },
    async init({ commit, state }) {
      const token = localStorage.getItem('token');
      console.log('Init action called with token:', token)
      if (token) {
        axios.defaults.headers.common['Authorization'] = 'Basic ' + btoa(token + ':');
        try {
          const response = await axios.get('/api/v1/me');
          commit('setUser', response.data.user);
          console.log('User set:', response.data.user);
        } catch (error) {
          console.error('Invalid token', error);
          localStorage.removeItem('token');
          commit('clearUser');
        }
      }
    }
  },
  getters: {
    isAuthenticated: state => !!state.user
  }
});

export default store;