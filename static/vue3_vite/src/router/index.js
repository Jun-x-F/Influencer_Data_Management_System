// src/router/index.js
import {createRouter, createWebHistory} from 'vue-router';
import Home from '@/components/HelloWorld.vue'; // 确保路径正确
import VideoIndex from '@/components/videos/video_index.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/videos',
    name: 'VideoIndex',
    component: VideoIndex
    // 如果需要懒加载，可以使用以下方式：
    // component: () => import('@/views/VideoIndex.vue')
  }
  // 你可以在这里添加更多的路由
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return { x: 0, y: 0 };
  },
});

export default router;
