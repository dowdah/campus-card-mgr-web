import {createRouter, createWebHistory} from 'vue-router';
import Home from '../views/Home.vue';
import Cards from '../views/Cards.vue';
import PwdReset from '../views/PwdReset.vue';
import store from '../store';
import Transactions from "../views/Transactions.vue";
import TransactionSimulation from "../views/TransactionSimulation.vue";

const routes = [
    {path: '/', name: 'Home', component: Home},
    {path: '/cards', name: 'Cards', component: Cards, meta: {requiresAuth: true}},
    {path: '/transactions', name: 'Transactions', component: Transactions, meta: {requiresAuth: true}},
    {path: '/simulation', name: 'TransactionSimulation', component: TransactionSimulation, meta: {requiresAuth: true}},
    {path: '/reset-pwd', name: 'PwdReset', component: PwdReset, meta: {blockWhenAuthenticated: true}}
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL), routes
});

router.beforeEach(async (to, from, next) => {
    await store.dispatch('init');
    console.log(`Navigating to: ${to.name}`);
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!store.getters.isAuthenticated) {
            console.log('Not authenticated, redirecting to Home');
            next({name: 'Home'});
        } else {
            console.log('Authenticated, proceeding to route');
            next();
        }
    } else if (to.matched.some(record => record.meta.blockWhenAuthenticated)) {
        if (store.getters.isAuthenticated) {
            console.log('Already authenticated, redirecting to Home');
            next({name: 'Home'});
        } else {
            console.log('Not authenticated, proceeding to route');
            next();
        }
    } else {
        next();
    }
});

export default router;
