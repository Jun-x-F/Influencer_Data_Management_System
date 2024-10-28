<template>
  <div :class="{ 'invalid-label': wrapperClass }"
    :style="{ '--cascader-tags-margin-top': dynamicMarginTop, '--cascader-tags-with': tagsWith }">
    <label v-if="label">{{ label }}</label>
    <el-cascader class="wide-cascader" v-model="internalValue" :placeholder="placeholder" :options="options"
      :props="cascaderProps" :clearable="clearable" :filterable="filterable" :show-all-levels="showAllLevels"
      :collapse-tags="collapseTags" :collapse-tags-tooltip="collapseTagsTooltip" :required="required" />
  </div>
</template>

<script lang="ts" setup>
import {computed} from 'vue';

// 定义组件的 props，并接收返回的 props 对象
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  options: {
    type: Array,
    required: true,
  },
  placeholder: {
    type: String,
    default: '请选择',
  },
  label: {
    type: String,
    default: '',
  },
  wrapperClass: {
    type: Boolean,
    default: true,
  },
  cascaderProps: {
    type: Object,
    default: () => ({}),
  },
  clearable: {
    type: Boolean,
    default: true,
  },
  filterable: {
    type: Boolean,
    default: true,
  },
  showAllLevels: {
    type: Boolean,
    default: false,
  },
  collapseTags: {
    type: Boolean,
    default: true,
  },
  collapseTagsTooltip: {
    type: Boolean,
    default: true,
  },
  required: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false
  },
  dynamicMarginTop: { // 新增一个 prop 来控制 margin-top
    type: String,
    default: '0',
  },
  tagsWith: {
    type: String
  }
});

console.log(props.wrapperClass);

// 定义 emits，用于向父组件传递事件
const emit = defineEmits(['update:modelValue', 'select']);

// 使用 computed 属性实现双向绑定
const internalValue = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit('update:modelValue', value);
    emit('select', { "name": props.label, "value": value });
  },
});
</script>

<style scoped>
/* 添加通用样式 */
::v-deep .wide-cascader {
  width: var(--cascader-tags-with, 600px);

  height: 43px;
}

::v-deep .el-input--suffix {
  float: left;
  height: 43px;
}

::v-deep .el-cascader__tags {
  /* margin-top: -10%; */
  float: left;
  width: 90%;
  height: 100%;
  margin-top: 0;
  top: unset;
  transform: unset;
}

::v-deep .el-cascader__search-input {
  margin-top: 0;
  width: 80%;
  height: 100%;
  position: absolute;
  border: none;
  /* 移除边框 */
  box-shadow: none;
}

::v-deep .el-input__inner {
  border: none;
  /* 移除边框 */
  box-shadow: none;
  /* 移除阴影，如果有的话 */
}

::v-deep .el-cascader__tags .el-tag {
  /* margin-right: -30%;
  margin-left: 37%;
  margin-top: -11.8%; */
  margin: 0;
  margin-left: 20%;
  margin-right: -10%;
  margin-top: var(--cascader-tags-margin-top, 0);
  border: none;
  /* 移除边框 */
  color: #504f4f;
}
</style>