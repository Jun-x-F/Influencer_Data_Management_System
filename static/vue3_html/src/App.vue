<template>
  <div id="app" style="width: 100vw; height: 100vh;">
    <!-- 根据路由进行跳转 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import {onMounted} from 'vue'
import {getUserId} from './config/config'

onMounted(() => {
  // 组件挂载时生成或获取用户ID
  getUserId()
})
</script>
