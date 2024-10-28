<template>
     <div class="btn-reset">
        <el-button type="info" plain @click="handleReset">重置</el-button>
     </div>
</template>
<script setup lang="ts">
import {defineEmits} from 'vue';

// 定义组件可以触发的事件
const emit = defineEmits(['reset']);

// 处理重置按钮的点击事件
function handleReset() {
  // 触发 'reset' 事件，通知父组件
  emit('reset');
}
</script>
<style scoped>

</style>