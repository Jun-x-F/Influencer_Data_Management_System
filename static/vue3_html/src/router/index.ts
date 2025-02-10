// src/router/index.js
import {createRouter, createWebHistory} from 'vue-router';
import MainLayout from '@/components/layout/MainLayout.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MainLayout
  },
  {
    path: '/index',
    name: 'Index',
    component: MainLayout
    // 如果需要懒加载，可以使用以下方式：
    // component: () => import('@/views/VideoIndex.vue')
  }
  // 你可以在这里添加更多的路由
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0, left: 0 };
  },
});

export default router;
