<script lang="ts" setup>
import {updateVideoData} from '@/stores/videos/update_video';
import {computed, onMounted, ref} from 'vue';
import {parsePhoneNumberFromString} from 'libphonenumber-js';
import {ElMessage} from "element-plus";
import useClipboard from 'vue-clipboard3'

// 确保 videoData 是响应式的
const videoData = updateVideoData();
const influencerTable = ref<any[]>([]); // 初始化为一个空数组
const toClipboard = useClipboard();

// 异步初始化
onMounted(async () => {
  try {
    await videoData.initializeInfluencer();
    influencerTable.value = videoData.influencerTable; // 更新响应式数据
    console.log('influencerTable', influencerTable.value);
  } catch (error) {
    console.error('初始化失败', error);
  }
});

// 定义列数据类型
interface Column {
  prop: string;
  label: string;
  width: string;
  sortable?: boolean;
  filters?: any[];
  filterMethod?: (value: any, row: any, column: Column) => boolean;
  filteredValue?: any[];
  isLink?: boolean;
  merge?: boolean;
  isTag?: boolean;
}

// 定义固定列
const fixedColumns: Column[] = [
  { prop: 'id', label: 'ID', width: '80px', sortable: true, merge: true },
  { prop: '红人头像地址', label: '红人头像地址', width: 'auto', merge: true, isLink: true },
  { prop: '红人名称', label: '红人名称', width: '150px', isLink: true, merge: true },
  { prop: '平台', label: '平台', width: '100px', merge: true },
  { prop: '粉丝数量', label: '粉丝数量', width: 'auto', merge: true },
  { prop: '平均播放量', label: '平均播放量', width: 'auto', merge: true },
  { prop: '平均点赞数量', label: '平均点赞数', width: 'auto', merge: true },
  { prop: '平均评论数量', label: '平均评论数', width: 'auto', merge: true },
  { prop: '平均参与率', label: '平均参与率', width: 'auto', merge: true },
  { prop: '地区', label: '地区', width: '100px', merge: true, isLink: true },
  { prop: '地址', label: '地址', width: 'auto', merge: true },
  { prop: '联系方式', label: '联系方式', width: '200px', merge: true },
  { prop: '标签', label: '标签', width: '200px', merge: true, isTag: true },
  { prop: '评级', label: '评级', width: '80px', merge: true },
];
const isValidURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// 处理标签列，将逗号分隔的标签转换为数组
const processTags = (tags: string): string[] => {
  return tags ? tags.split(',').map(tag => tag.trim()) : [];
}

// 分割多个链接
const splitLinks = (links: string) => {
  return links ? links.split(',').map(link => link.trim()) : [];
};

const isDiscordLink = (url: string) => {
  return url.includes("discord.com");
};

const isEmailLink = (url: string) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(url);
};

const validatePhoneNumber = (phone: string) => {
  const parsedNumber = parsePhoneNumberFromString(phone);
  return parsedNumber.isValid();
}
// 使用 computed 确保列数据响应式
const columns = computed(() => [...fixedColumns]);
console.log(columns)

const open = (info: string) => {
  // 使用 Clipboard API 将信息复制到剪贴板
  toClipboard.toClipboard(info);
  ElMessage({
    message: "联系方式复制成功: " + info,
    offset: 20,
    grouping: true,
    type: 'success',
  });
}

</script>

<template>
  <div class="table-wrapper">
    <el-table :data="influencerTable" fixed border :default-sort="{ prop: 'id', order: 'descending' }"
      max-height="720px">
      <el-table-column v-for="column in columns" :key="column.prop" :prop="column.prop" :label="column.label"
        :width="column.width" :sortable="column.sortable" :filters="column.filters" :filter-method="column.filterMethod"
        :filtered-value="column.filteredValue">
        <!-- Custom Cell Content -->
        <!-- Custom Cell Content for Image -->
        <template v-if="column.isLink" #default="scope">
          <el-image v-if="column.prop === '红人头像地址'" :src="scope.row[column.prop]" fit="cover" loading="lazy">
            {{ column.prop }}
          </el-image>
          <a v-else-if="column.prop === '红人名称' && isValidURL(scope.row['红人主页地址'])" :href="scope.row['红人主页地址']"
            target="_blank" rel="noopener noreferrer">
            {{ scope.row[column.prop] }}
          </a>
          <!-- <span>{{ scope.row[column.prop] }}</span> -->
        </template>
        <!-- Custom Cell Content for Tags -->
        <template v-else-if="column.prop === '标签' && column.isTag" #default="scope">
          <el-row>
            <div v-if="scope.row[column.prop]">
              <el-col :span="30">
                <el-tag v-for="(tag, index) in processTags(scope.row[column.prop])" :key="index" :closable="false"
                  class="contact_tag">
                  {{ tag }}
                </el-tag>
              </el-col>
            </div>
          </el-row>
        </template>
        <template v-else-if="column.prop === '地址'" #default="scope">
          <el-row>
            <el-col :span="30" v-if="scope.row['地址']">
              <el-tooltip :content="scope.row['地址']" placement="bottom" effect="dark">
                <a href="#" @click="open(scope.row['地址'])">
                  <el-image src="./src/assets/map_logo.png" class="contact_logo"></el-image>
                </a>
              </el-tooltip>
            </el-col>
          </el-row>
        </template>
        <template v-else-if="column.prop === '联系方式'" #default="scope">
          <el-row>
            <div v-for="(link, index) in splitLinks(scope.row['联系方式'])" :key="index">
              <el-col :span="30">
                <el-tooltip :content="link" placement="bottom" effect="dark">
                  <a href="#" @click="open(link)">
                    <el-image v-if="isDiscordLink(link)" src="./src/assets/discord_logo.png" class="contact_logo">
                    </el-image>
                    <el-image v-else-if="isEmailLink(link)" src="./src/assets/email.png" class="contact_logo" />
                    <el-image v-else-if="validatePhoneNumber(link)" src="./src/assets/chat_logo.png"
                      class="contact_logo" />
                  </a>
                  <!--          <a v-else></a>-->
                </el-tooltip>
              </el-col>
            </div>

          </el-row>
          <!--        <el-image v-for="column.prop=== 联系f" :key="index" :closable="false">-->
        </template>
        <!-- Default Cell Content -->
        <template v-else #default="scope">
          {{ scope.row[column.prop] }}
        </template>

      </el-table-column>
      <el-table-column fixed="right" label="Operations" min-width="120">
        <template #default="scope">
          <el-row>
            <el-col :span="12">
              <el-tooltip content="更新" placement="top">
                <el-button type="primary" key="更新" size="small">更新</el-button>
              </el-tooltip>
            </el-col>
            <el-col :span="12">
              <el-tooltip content="删除" placement="top">
                <el-button type="danger" key="删除" size="small" >删除</el-button>
              </el-tooltip>
            </el-col>
          </el-row>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.table-wrapper {
  width: 100%;
  margin: 0 auto;
  border-radius: 5px;
}

.contact_logo {
  margin: 5px;
  width: 40px;
  height: 40px;
  cursor: pointer;
  transition: transform 0.2s;
}

.contact_tag {
  transition: all 0.3s ease;
  margin: 5px;
  width: 60px;
  height: 40px;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  /* 初始的轻微阴影 */
}

.contact_tag:hover {
  transform: scale(1.1);
  /* 放大效果 */
  box-shadow: 0 8px 16px rgba(229, 57, 53, 0.4);
  /* 发光阴影效果 */
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
  /* 发光文字效果 */
}

/* 在光标悬停时给tag增加点外发光的动画 */
@keyframes glowing {
  0% {
    box-shadow: 0 0 2px rgba(0, 255, 255, 0.4);
  }

  50% {
    box-shadow: 0 0 2px rgba(0, 255, 255, 0.4);
  }

  100% {
    box-shadow: 0 0 1px rgba(0, 255, 255, 0.4);
  }
}

.contact_tag:hover {
  animation: glowing 1.5s infinite;
}

.contact_logo:hover {
  transform: scale(1.1);
}
</style>
