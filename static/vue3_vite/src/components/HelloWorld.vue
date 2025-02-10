<script setup>
import {onBeforeUnmount, onMounted, ref} from 'vue'
import TableV2_influencer from "@/components/tables_element/tableV2_influencer.vue";
import {ArrowLeft} from "@element-plus/icons-vue";
import AddInfluencer from "@/components/influencer/addInfluencer.vue";
const onBack = () => {
  window.open('http://172.16.11.236:37799/webroot/decision#/directory?activeTab=d3b7c734-4360-4833-b0b4-62d5e7cece08', '_blank');
}
const goToVideos = () => {
  window.open('http://172.16.11.245:5173/videos', '_blank');
}
const windowHeight = ref(window.innerHeight);

const updateHeight = () => {
  windowHeight.value = window.innerHeight;
};

onMounted(() => {
  window.addEventListener('resize', updateHeight);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateHeight);
});
</script>

<template>
  <div class="body_influencer" :style="{ height: windowHeight + 'px' }">
    <div class="header">
      <el-page-header :icon="ArrowLeft" title="返回看板" @back="onBack">
        <template #content>
          <div class="flex items-center">
            <el-avatar :size="38" class="mr-3" src="/logo.png" />
            <span class="text-large font-600 mr-3"> 红人数据管理 </span>
            <el-check-tag :checked="true" type="danger" @click="goToVideos">
              前往视频数据管理
            </el-check-tag>
          </div>
        </template>
        <template #extra>
          <el-row :gutter="20">
            <el-col>
              <add-influencer />
            </el-col>
          </el-row>
        </template>
      </el-page-header>
    </div>
    <el-divider />
    <div class="container">
      <section id="videoSection" class="videoSection_form-container">
        <table-v2_influencer />
      </section>
    </div>
  </div>
</template>

<style scoped>
body{
  overflow:auto;
}

::v-deep(.el-statistic)  {
  --el-statistic-content-font-size: 28px;
}
::v-deep(.el-page-header__header) {
  padding-top: 1%;
}

::v-deep(.el-page-header__left) {
  margin-left: 5%;
}

::v-deep(.el-page-header__content)  {
  font-size: 32px;
}

::v-deep(.el-page-header__extra)  {
  margin-right: 5%;
}
</style>
