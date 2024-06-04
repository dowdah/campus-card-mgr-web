import { createApp } from 'vue';
import App from './App.vue';
import store from './store';
import router from './router';

const app = createApp(App);

// 使用 Vuex store 和 Vue Router
app.use(store);
app.use(router);
app.mount('#app');

// router.isReady().then(() => {
//   // 此举目的是保证路由守卫总是在 store 初始化之后执行，并且 store 不会被多次初始化
//   const isProtectedRoute = router.currentRoute.value.matched.some(record => record.meta.requiresAuth);
//
//   if (!isProtectedRoute) {
//     // 如果当前路由不是受保护路由，则执行 store init
//     store.dispatch('init').then(() => {
//       app.mount('#app');
//     });
//   } else {
//     // 如果当前路由是受保护路由，则直接挂载应用，由路由守卫执行 store init
//     app.mount('#app');
//   }
// });