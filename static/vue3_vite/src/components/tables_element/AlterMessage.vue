<!-- ConfirmDialog.vue -->
<template>
  <!-- 自定义对话框 -->
  <el-dialog v-model="dialogVisible" :show-close="false" :width="width" :before-close="handleBeforeClose"
    :destroy-on-close="true">
    <!-- 自定义头部 -->
    <template #header="{ close, titleId, titleClass }">
      <div class="my-header">
        <h4 :id="titleId" :class="titleClass">{{ title }}</h4>
        <el-button type="danger" @click="close">
          <CircleCloseFilled />
          Close
        </el-button>
      </div>
    </template>

    <!-- 对话框内容 -->
    <div v-loading="loading">{{ errorMessage }}</div>
  </el-dialog>
</template>

<script lang="ts" setup>
import {computed, defineEmits, defineProps} from 'vue';
import {CircleCloseFilled} from '@element-plus/icons-vue';

// 定义组件的 props
const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  header_info: {
    type: String,
    default: '警告',
  },
  title: {
    type: String,
    default: 'Confirmation',
  },
  errorMessage: {
    type: String,
    default: 'Are you sure you want to proceed?',
  },
  width: {
    type: String,
    default: '500px',
  },
  loading: {
    type: Boolean,
    default: false,
  }
});

// 定义组件的 emits
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);

// 定义一个计算属性，用于同步 modelValue 和内部可见性状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

// 打开对话框的方法
const openDialog = () => {
  dialogVisible.value = true;
};

// 确认操作的处理方法
const confirmDialog = () => {
  emit('confirm');
  dialogVisible.value = false;
};

// 取消操作的处理方法
const closeDialog = () => {
  emit('cancel');
  dialogVisible.value = false;
};

// 处理对话框关闭前的逻辑
const handleBeforeClose = (done: () => void) => {
  emit('cancel');
  done();
};
</script>

<style scoped>
.my-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.dialog-footer {
  text-align: right;
}

.el-dialog__wrapper {
  transition: opacity 0.3s ease;
}
</style>