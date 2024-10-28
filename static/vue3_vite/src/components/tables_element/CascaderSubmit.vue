<template>
     <div class="btn-success">
        <el-button type="success" plain @click="updateData">提交视频</el-button>
     </div>
</template>
<script setup lang="ts">
// 定义组件可以触发的事件
const emit = defineEmits(['update']);
// 处理重置按钮的点击事件
function updateData() {
  // 触发 'reset' 事件，通知父组件
  emit('update');
}
</script>
<style scoped>
.btn-success{
   margin-right: 10px;
}
</style>