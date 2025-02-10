<script setup>
import { computed, h, ref, watch } from "vue";
import { ElNotification, ElMessage } from "element-plus";
import { Close, StarFilled, Delete, Upload, InfoFilled } from "@element-plus/icons-vue";
import { useInfluencerStore } from '@/store/useInfluencerStore';

const influencerStore = useInfluencerStore();
// 定义 props
const props = defineProps({
  drawer: {
    type: Boolean,
    required: true
  }
})

// 定义 emits
const emit = defineEmits(['update:drawer', 'close'])

// 同步 drawer 状态
watch(() => props.drawer, (newVal) => {
  drawerVisible.value = newVal
})

const drawerVisible = ref(false)
const addInput = ref('')
const addUrl = ref([])
const isClick = ref(false)
const isSubmitting = ref(false)

// 监听内部 drawer 状态变化
watch(drawerVisible, (newVal) => {
  emit('update:drawer', newVal)
})

const handleClose = (val) => {
  emit('close')
}

// 允许的域名列表
const allowedDomains = [
  'instagram.com',
  'youtube.com',
  'x.com',
  'twitter.com', // 包含 twitter.com 因为有些旧链接可能还在使用
  'tiktok.com'
];

// 按平台定义允许的路径模式
const platformPaths = {
  instagram: ['/reel/', '/p/', '/reels/', '/@', '/'],  // 添加 '/' 支持个人主页
  youtube: ['/watch', '/shorts/', '/@', '/videos', '/channel/', 'youtu.be/'],
  twitter: ['/status/'],
  tiktok: [] // TikTok 只需验证域名
};

// 预编译正则表达式
const domainRegex = computed(() => {
  const escapedDomains = allowedDomains.map(domain =>
    domain.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  );
  return new RegExp(`^https?:\/\/(.*\.)?(${escapedDomains.join('|')})`, 'i');
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

/**
 * 验证 URL 是否来自允许的社交平台且包含指定路径
 * @param {string} url - 待验证的 URL
 * @returns {boolean} - 如果符合要求返回 true，否则返回 false
 */
const isValidSocialMediaURL = (url) => {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    const pathname = urlObj.pathname;

    // 检查域名是否匹配允许的社交平台
    if (!domainRegex.value.test(url)) return false;

    // TikTok 特殊处理：只需验证域名
    if (hostname.includes('tiktok.com')) {
      return true;
    }

    if (hostname.includes('twitter.com') || hostname.includes('x.com')) {
      return true;
    }

    // Instagram 特殊处理：允许个人主页
    if (hostname.includes('instagram.com')) {
      // 如果是个人主页（路径格式为 /@username 或 /username）
      if (pathname.length > 1 && !pathname.includes('.')) {
        return true;
      }
      return platformPaths.instagram.some(path => url.includes(path));
    }

    if (hostname.includes('youtube.com') || hostname.includes('youtu.be')) {
      return platformPaths.youtube.some(path => url.includes(path));
    }

    return false;
  } catch (_) {
    return false;
  }
};

const closeElMessage = () => {

}

const openMessage = (title, message) => {
  ElNotification.error({
    title: title,
    message: h('i', { style: 'color: teal' }, message),
  })
}
/**
 * 解析并过滤文本中的 URL
 * @param {string} text - 输入的多行文本
 */
const handleParseText = (text) => {
  try {
    if (!text) {
      addUrl.value = [];
      addInput.value = '';
      return;
    }

    // 首先尝试分割可能连在一起的URL
    const splitUrls = text
      .replace(/https?:\/\//g, '\nhttps://')  // 在每个 http(s):// 前添加换行
      .split('\n')
      .map(line => line.trim())
      .filter(line => line !== '');

    const list = splitUrls.map(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
        return `https://${trimmed}`;
      }
      return trimmed;
    });

    const cur_url = [];
    const uniqueSet = new Set(list);
    const uniqueList = Array.from(uniqueSet);

    for (let i = 0; i < uniqueList.length; i++) {
      const url = uniqueList[i];
      if (!isValidURL(url)) {
        openMessage("这不是有效的Url", "请确保包含 http:// 或 https:// - " + url);
        continue;
      }
      if (!isValidSocialMediaURL(url)) {
        openMessage(
          "无效的社交媒体链接",
          "请确保链接来自 Instagram、YouTube、Twitter/X 或 TikTok，并且是视频/帖子链接 - " + url
        );
        continue;
      }
      cur_url.push(url);
    }

    addUrl.value = cur_url;
    addInput.value = cur_url.join('\n');
  } catch (error) {
    console.error('Error parsing text:', error);
    openMessage(
      "解析错误",
      "处理输入时发生错误，请检查输入格式是否正确"
    );
  }
}

// 清空输入
const handleClear = () => {
  addInput.value = ''
  addUrl.value = []
  ElMessage({
    message: '已清空输入内容',
    type: 'info'
  })
}

// 提交处理
const handleSubmit = async () => {
  if (!addUrl.value.length) {
    ElMessage({
      message: '请先输入有效的链接',
      type: 'warning'
    })
    return
  }

  try {
    isSubmitting.value = true
    // TODO: 这里添加你的提交逻辑
    // redisApi/get/
    await influencerStore.addInfluencerList(addUrl.value)

    ElMessage({
      message: '提交成功',
      type: 'success'
    })
    handleClear()
    drawerVisible.value = false
  } catch (error) {
    ElMessage({
      message: '提交失败：' + error.message,
      type: 'error'
    })
  } finally {
    isSubmitting.value = false
  }
}

// 移除单个URL
const removeUrl = (index) => {
  addUrl.value.splice(index, 1)
  addInput.value = addUrl.value.join('\n')
}
</script>

<template>
  <div>
    <el-drawer v-model="drawerVisible" title="新增任务" :with-header="true" size="40%" @close="handleClose"
      :append-to-body="true" :destroy-on-close="true" class="custom-drawer">
      <!-- 自定义头部 -->
      <template #header>
        <div class="drawer-header">
          <h3>新增任务</h3>
        </div>
      </template>

      <el-form class="drawer-content">
        <el-alert type="info" show-icon :closable="false" class="info-alert">
          <template #icon>
            <el-icon>
              <InfoFilled />
            </el-icon>
          </template>
          <p>
            输入红人的视频链接，如果相同会只保留一个;<br>
            如果不是 <span class="highlight">红人视频或Url格式</span>，则直接剔除
          </p>
        </el-alert>

        <el-form-item label="输入链接" prop="url" class="input-area">
          <template #label>
            <span class="form-label">输入链接</span>
          </template>
          <el-input v-model="addInput" type="textarea" autosize placeholder="请输入红人链接，多条请换行" clearable
            @change="handleParseText" class="custom-input" />
        </el-form-item>

        <!-- URL 预览区域 -->
        <div v-if="addUrl.length" class="url-preview">
          <h4>已解析的链接 ({{ addUrl.length }})</h4>
          <el-scrollbar height="150px">
            <div v-for="(url, index) in addUrl" :key="index" class="url-item">
              <el-tag size="small" closable @close="removeUrl(index)">
                {{ url }}
              </el-tag>
            </div>
          </el-scrollbar>
        </div>
      </el-form>

      <!-- 底部按钮 -->
      <div class="drawer-footer">
        <el-button @click="handleClear" :disabled="!addInput">
          <el-icon>
            <Delete />
          </el-icon>
          清空
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="isSubmitting" :disabled="!addUrl.length">
          <el-icon>
            <Upload />
          </el-icon>
          提交
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.custom-drawer {
  :deep(.el-drawer__header) {
    margin-bottom: 0;
    padding: 16px 20px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  :deep(.el-drawer__body) {
    padding: 20px;
    padding-bottom: 70px;
  }
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  h3 {
    margin: 0;
    font-size: 18px;
    color: var(--el-text-color-primary);
  }
}

.close-btn {
  padding: 8px;
  border: none;

  &:hover {
    background-color: var(--el-color-primary-light-9);
  }
}

.drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-alert {
  margin-bottom: 20px;
  border-radius: 8px;

  :deep(.el-alert__content) {
    padding: 8px 0;
  }
}

.input-area {
  /* flex-grow: 1; */

  :deep(.el-form-item__label) {
    font-weight: 500;
    height: 32px;
    line-height: 32px;
    padding: 0;
    margin-bottom: 8px;
  }

  :deep(.el-form-item__content) {
    display: flex;
    flex-direction: column;
    align-items: none;
  }
}

.form-label {
  display: inline-block;
  vertical-align: middle;
}

.custom-input {
  :deep(.el-textarea__inner) {
    border-radius: 8px;
    min-height: 100px !important;
    resize: vertical;
    margin-top: 0;

    &:focus {
      box-shadow: 0 0 0 2px var(--el-color-primary-light-8);
    }
  }
}

.url-preview {
  background-color: var(--el-fill-color-lighter);
  border-radius: 8px;
  padding: 12px;

  h4 {
    margin: 0 0 12px 0;
    color: var(--el-text-color-secondary);
    font-size: 14px;
  }
}

.url-item {
  margin-bottom: 8px;

  .el-tag {
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  backdrop-filter: blur(8px);
}

/* 暗黑模式适配 */
html.dark {
  .custom-drawer {
    :deep(.el-drawer__header) {
      border-bottom-color: var(--el-border-color-darker);
    }
  }

  .url-preview {
    background-color: var(--el-bg-color-overlay);
  }

  .drawer-footer {
    background: var(--el-bg-color-overlay);
    border-top-color: var(--el-border-color-darker);
  }
}

/* 动画效果 */
.url-item {
  transition: all 0.3s ease;

  &:hover {
    transform: translateX(4px);
  }
}

.el-button {
  transition: all 0.3s ease;

  &:not(:disabled):hover {
    transform: translateY(-2px);
  }
}
</style>