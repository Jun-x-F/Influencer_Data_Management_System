import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createPinia } from 'pinia';
import router from './router';
// 引入 Element Plus
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css'; // 引入 Element Plus 的样式


const app = createApp(App);
// 全局注册 Vue Multiselect 组件
app.use(ElementPlus);
app.use(createPinia());
app.use(router);
app.mount('#app');