<script setup>
import {computed, h, ref} from "vue";
import {useNotice} from "@/stores/notice.js";
import {ElNotification} from "element-plus";
import {Close, StarFilled} from "@element-plus/icons-vue";

const addInput = ref();
const addUrl = ref();
const notice = useNotice();
const isClick = ref(false);
const drawer = ref(false);
const handleClose = (val) => {
  console.log("正在关闭")

  if (isClick.value === true) {
    notice.setIsUpdateInfluencerData(true);
  }
  isClick.value = false

}

const excludedSubstrings = [
  '/reel/', '/video/', '/watch/',
  '/video?', '/watch?', '/reel?',
  '/p/', '/p?', '/shorts/', '/shorts?', '/status/', "https://youtu.be/"
];
// 预编译排除的正则表达式
const exclusionRegex = computed(() => {
  const escapedSubstrings = excludedSubstrings.map(substr =>
      substr.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  );
  return new RegExp(escapedSubstrings.join('|'), 'i'); // 'i' 忽略大小写
});

/**
 * 验证字符串是否为有效的 URL
 * @param {string} str - 待验证的字符串
 * @returns {boolean} - 如果是有效的 URL，则返回 true，否则返回 false
 */
const isValidURL = (str) => {
  try {
    new URL(str);
    return true;
  } catch (_) {
    return false;
  }
};

const closeElMessage = () => {

}

const openMessage = (title, message) => {
  ElNotification.error({
    title: title,
    message: h('i', {style: 'color: teal'}, message),
  })
}
/**
 * 解析并过滤文本中的 URL
 * @param {string} text - 输入的多行文本
 */
const handleParseText = (text) => {
  const list = text
      .split('\n')                   // 按换行符分割成数组
      .map(line => line.trim())      // 移除每行的首尾空白字符
      .filter(line => line !== '');  // 排除空字符串
  const cur_url = [];
  const uniqueSet = new Set(list);       // 转换为 Set 以去除重复项
  const uniqueList = Array.from(uniqueSet); // 再转换回数组

  for (let i = 0; i < uniqueList.length; i++) {
    const url = uniqueList[i];
    if (!isValidURL(url)) {
      openMessage("这不是Url", "注意检查 - " + url);
      continue;
    }
    if (exclusionRegex.value.test(url)) {
      openMessage("这不是红人Url", "注意检查 - " + url);
      continue;
    }
    cur_url.push(url);
  }
  addUrl.value = cur_url;
  addInput.value = cur_url.join('\n');
}
</script>

<template>
  <div>
    <div class="addVideoDiv">
      <el-affix target=".addVideoDiv" :offset="20">
        <el-button type="warning" @click="drawer = true">新增红人</el-button>
      </el-affix>
    </div>
    <el-drawer v-model="drawer" title="新增任务" :with-header="false" size="40%" @close="handleClose"
               :append-to-body="true"
               :destroy-on-close="true">
      <el-form>
        <el-alert type="info" show-icon :closable="false">
          <p>
            输入红人的视频链接，如果相同会只保留一个;<br>
            如果不是 <span class="highlight">红人视频或Url格式</span>，则直接剔除
          </p>
        </el-alert>
        <el-form-item label="输入链接" prop="url">
          <el-input v-model="addInput" type="textarea" autosize placeholder="请输入红人链接，多条请换行" clearable
                    @change="handleParseText"/>
        </el-form-item>
      </el-form>
    </el-drawer>
  </div>

</template>

<style scoped>
::v-deep(.el-input__inner) {
  border: none; /* 移除边框 */
  box-shadow: none; /* 移除阴影，如果有的话 */
}

.highlight {
  font-weight: bold;
  color: red;
}

</style>