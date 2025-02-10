<template>
  <div :class="{ 'invalid-label': wrapperClass }">
    <label v-if="label" :for="inputId">{{ label }}</label>
    <el-autocomplete :id="inputId" v-model="internalValue" :fetch-suggestions="querySearch" :placeholder="placeholder"
      clearable @select="handleSelect" :required="required" />
  </div>
</template>
<script setup>
import {computed} from 'vue';

// 接收父组件传递的 props
const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  placeholder: {
    type: String,
    default: '请输入',
  },
  dataList: {
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  wrapperClass: {
    type: Boolean,
    default: true,
  }
});

// 定义 emits，用于向父组件传递事件
const emits = defineEmits(['update:modelValue', 'select']);

// 生成唯一的输入框 ID（可选）
const inputId = `autocomplete-input-${Math.random().toString(36).substr(2, 9)}`;


// 使用 computed 属性实现双向绑定
const internalValue = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emits('update:modelValue', value);
  },
});


// 将 dataList 转换为包含 value 属性的对象数组
const dataListWithObjects = computed(() => {
  return props.dataList.map((item) => {
    if (typeof item === 'object' && item !== null) {
      return item;
    } else {
      return { value: item };
    }
  });
});

// 提供建议列表的函数
const querySearch = (queryString, callback) => {
  const list = dataListWithObjects.value;

  if (!Array.isArray(list) || list.length === 0) {
    callback([]);
    return;
  }

  let results = [];
  if (queryString) {
    const lowerQuery = queryString.toString().toLowerCase();
    results = list.filter((element) =>
      element.value.toString().toLowerCase().includes(lowerQuery)
    );
  } else {
    results = list;
  }

  callback(results);
};

// 处理选择建议项的函数
const handleSelect =async (item) => {
  emits('select', { "name": props.label, "value": item });
};
</script>
<style scoped>
::v-deep(.el-input__inner)  {
  border: none;
  /* 移除边框 */
  box-shadow: none;
  /* 移除阴影，如果有的话 */
}
</style>