import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: null
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
    clearUser(state) {
      state.user = null;
    }
  },
  actions: {
    async login({ commit }, credentials) {
      const response = await axios.post('/api/v1/login', credentials);
      localStorage.setItem('token', response.data.token);
      commit('setUser', response.data.user);
    },
    async logout({ commit }) {
      localStorage.removeItem('token');
      commit('clearUser');
    }
  },
  getters: {
    isAuthenticated: state => !!state.user
  }
});