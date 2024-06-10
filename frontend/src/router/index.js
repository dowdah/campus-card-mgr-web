import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../components/Login.vue';
import Dashboard from '../components/Dashboard.vue';
import PwdReset from '../views/PwdReset.vue';
import store from '../store';

const routes = [
  { path: '/', name: 'Home', component: Home },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  { path: '/reset-pwd', name: 'PwdReset', component: PwdReset, meta: { blockWhenAuthenticated: true }}
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach(async (to, from, next) => {
  await store.dispatch('init');
  console.log(`Navigating to: ${to.name}`);
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters.isAuthenticated) {
      console.log('Not authenticated, redirecting to Login');
      next({ name: 'Login' });
    } else {
      console.log('Authenticated, proceeding to route');
      next();
    }
  } else if (to.matched.some(record => record.meta.blockWhenAuthenticated)) {
    if (store.getters.isAuthenticated) {
      console.log('Already authenticated, redirecting to Dashboard');
      next({ name: 'Home' });
    } else {
      console.log('Not authenticated, proceeding to route');
      next();
    }
  }
  else {
    next();
  }
});

export default router;