<template>
    <div :class="{ 'invalid-label': wrapperClass }">
        <label v-if="label">{{ label }}</label>
    <el-input
      v-model="internalValue"
      :placeholder="placeholder"
      :type="type"
      clearable
    />
    </div>
  </template>
  <script lang="ts" setup>
  import {computed, defineEmits, defineProps} from 'vue';

  // 定义组件的 props
  const props = defineProps({
    modelValue: {
      type: [String, Number],
      default: '',
    },
    label:{
        type: String,
        default: '',
    },
    type:{
        type: String,
        default: 'text',
    },
    placeholder: {
      type: String,
      default: '请输入',
    },
    wrapperClass:{
        type: Boolean,
        default: true,
    }
  });
  
  // 定义 emits，用于向父组件传递事件
  const emit = defineEmits(['update:modelValue', 'input', 'change', 'blur', 'focus']);
  
  // 使用 computed 属性实现双向绑定
  const internalValue = computed({
    get() {
      return props.modelValue;
    },
    set(value) {
      emit('update:modelValue', value);
      emit('input', value);
    },
  });

  
  </script>
  <style scoped>
 ::v-deep(.el-input__inner) {
  border: none; /* 移除边框 */
  box-shadow: none; /* 移除阴影，如果有的话 */
}

  </style>
  
  