import {createStore} from 'vuex';
import {BASE_API_URL} from '@/config/constants';
import axios from 'axios';

const store = createStore({
    state: {
        user: null,
        isLoading: false
    },
    mutations: {
        setUser(state, user) {
            const roleTranslations = {
                'SchoolStaff': '学校管理员',
                'SiteOperator': '网站运营者',
                'User': '普通用户'
            };
            user.role = roleTranslations[user.role] || user.role;
            state.user = user;
        },
        clearUser(state) {
            state.user = null;
        },
        setLoading(state, isLoading) {
            state.isLoading = isLoading;
        }
    },
    actions: {
        async login({commit}, credentials) {
            console.log('Login action called with credentials:', credentials);
            commit('setLoading', true);
            try {
                const response = await axios.post(`${BASE_API_URL}/auth/login`, credentials);
                if (response.data.success) {
                    console.log('Login response:', response.data);
                    localStorage.setItem('token', response.data.token);
                    axios.defaults.headers.common['Authorization'] = 'Basic ' + btoa(response.data.token + ':');
                    commit('setUser', response.data.user);
                } else {
                    alert('登录失败：' + response.data.msg)
                }
            } catch (error) {
                console.error('Login error:', error);
                throw error;
            } finally {
                commit('setLoading', false);
            }
        },
        async logout({commit}) {
            commit('setLoading', true);
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
            commit('clearUser');
            commit('setLoading', false);
        },
        async init({commit, state}) {
            // 当加载时间超过 500ms 时，显式加载。
            let setLoadingCalled = false;
            const timer = setTimeout(() => {
                setLoadingCalled = true;
                commit('setLoading', true);
            }, 500);
            const token = localStorage.getItem('token');
            console.log('Init action called with token:', token)
            if (token) {
                axios.defaults.headers.common['Authorization'] = 'Basic ' + btoa(token + ':');
                try {
                    const response = await axios.get(`${BASE_API_URL}/auth/me`);
                    commit('setUser', response.data.user);
                    if (response.data.token) {
                        // 如果后端返回了新的token，更新本地存储的token，并设置axios的默认请求头
                        // 后端是否返回新token，取决于 auth.py 中 ALLOW_TOKEN_REFRESH 的设置
                        localStorage.setItem('token', response.data.token);
                        axios.defaults.headers.common['Authorization'] = 'Basic ' + btoa(response.data.token + ':');
                        console.log('Token refreshed:', response.data.token);
                    }
                    console.log('User set:', response.data.user);
                } catch (error) {
                    console.error('Invalid token', error);
                    localStorage.removeItem('token');
                    commit('clearUser');
                }
            }
            // 如果加载时间未超过 500ms，取消计时器。若计时器已触发，取消加载状态。
            if (!setLoadingCalled) {
                clearTimeout(timer);
            } else {
                commit('setLoading', false);
            }
        },
        async resetPassword({commit}, payload) {
            commit('setLoading', true);
            const {reset_choice, identifier, password, token} = payload;
            let data = {password};
            if (reset_choice === 'email') {
                data.email = identifier;
            } else if (reset_choice === 'student_id') {
                data.student_id = identifier;
            }
            try {
                console.log('Reset password data:', data);
                console.log('Reset password token:', token);
                const response = await axios.post(`${BASE_API_URL}/auth/reset-password/${token}`, data);
                console.log('Reset password response:', response.data);
                commit('setUser', response.data.user);
                localStorage.setItem('token', response.data.token);
                axios.defaults.headers.common['Authorization'] = 'Basic ' + btoa(response.data.token + ':');
            } catch (error) {
                console.error('Reset password error:', error);
                throw error;
            } finally {
                commit('setLoading', false);
            }
        },
        setLoading({commit}, isLoading) {
            commit('setLoading', isLoading);
        }
    },
    getters: {
        isAuthenticated: state => !!state.user
    }
});

export default store;