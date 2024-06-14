import {createRouter, createWebHistory} from 'vue-router';
import Home from '../views/Home.vue';
import Cards from '../views/Cards.vue';
import PwdReset from '../views/PwdReset.vue';
import store from '../store';
import Transactions from "../views/Transactions.vue";
import TransactionSimulation from "../views/TransactionSimulation.vue";
import UserMgr from "../views/UserMgr.vue";

const routes = [
    {path: '/', name: '主页', component: Home},
    {path: '/cards', name: '我的一卡通', component: Cards, meta: {requiresAuth: true}},
    {path: '/transactions', name: '交易记录', component: Transactions, meta: {requiresAuth: true}},
    {path: '/simulation', name: '模拟交易', component: TransactionSimulation, meta: {requiresAuth: true}},
    {path: '/reset-pwd', name: '忘记密码', component: PwdReset, meta: {blockWhenAuthenticated: true}},
    {
        path: '/user-mgr',
        name: '用户管理',
        component: UserMgr,
        meta: {
            requiresAuth: true,
            requiresPermission: [
                'VIEW_USER_INFO'
            ]
        }
    }
];

const router = createRouter({history: createWebHistory(), routes});

router.beforeEach(async (to, from, next) => {
    await store.dispatch('init');
    console.log(`Navigating to: ${to.name}`);
    if (to.matched.some(record => record.meta.requiresAuth) && !store.getters.isAuthenticated) {
        console.log('Not authenticated, redirecting to Home');
        next({name: '主页'});
    }
    if (to.matched.some(record => record.meta.blockWhenAuthenticated) && store.getters.isAuthenticated) {
        console.log('Already authenticated, redirecting to Home');
        next({name: '主页'});
    }
    if (to.matched.some(record => record.meta.requiresPermission !== undefined)) {
        for (let permission of to.meta.requiresPermission) {
            if (!store.getters.hasPermission(permission)) {
                console.log(`Current user can't ${permission}, redirecting to Home`);
                next({name: '主页'});
                return;
            }
        }
    }
    console.log('Router guard passed, proceeding to next route');
    next();
});

export default router;
