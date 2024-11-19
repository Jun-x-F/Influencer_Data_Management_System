<template>
    <!DOCTYPE html>
    <html lang="zh">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>视频数据管理</title>
    </head>

    <body>
        <div class="header">
            <el-page-header :icon="ArrowLeft" title="返回看板" @back="onBack">
                <template #content>
                    <div class="flex items-center">
                        <el-avatar :size="38" class="mr-3" src="/logo.png" />
                        <span class="text-large font-600 mr-3"> 视频数据管理 </span>
                        <el-check-tag :checked="true" type="danger" @click="goToInfluencers">
                            前往红人数据管理
                        </el-check-tag>
                        <!-- <a href="http://172.16.11.245:5000/influencers" class="text-sm mr-2"
                            style="color: var(--el-text-color-regular)"> 前往红人数据管理 </a>
                        <el-tag>Default</el-tag> -->
                    </div>
                </template>
                <template #extra>
                    <el-row :gutter="20">
                        <!-- <el-col :span="12">
                            <div class="statistic-card">
                                <el-statistic :value="98500">
                                    <template #title>
                                        <div style="display: inline-flex; align-items: center">
                                            我的任务 - 所有待执行数
                                            <el-tooltip effect="dark" content="关于任务执行的顺序以及现有的待执行数" placement="top">
                                                <el-icon style="margin-left: 4px" :size="12">
                                                    <Warning />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
</el-statistic>
</div>
</el-col> -->
                        <el-col :span="12">
                            <addMertics />
                        </el-col>
                        <el-col :span="6">
                            <add_videos />
                        </el-col>
                    </el-row>


                </template>
            </el-page-header>
        </div>
        <el-divider />
        <div class="container">
            <!-- <h1>视频数据管理</h1> -->

            <section id="videoSection" class="videoSection_form-container">
                <!-- <div class="affix-container">
                    <el-affix target=".affix-container" :offset="80">
                        <el-button type="primary" class="el_btn">视频数据管理</el-button>
                    </el-affix>
                </div> -->
                <!-- 新增数据按钮 -->


                <updateVideos />


                <!-- 视频数据表格 -->
                <cascaderTable />

            </section>
        </div>


        <!-- <script src="{{ url_for('static', filename='js/innodb_tools.js') }}?v={{ version }}"></script>
<script src="{{ url_for('static', filename='js/videos.js') }}?v={{ version }}"></script>
<script src="{{ url_for('static', filename='js/intervalId_func.js') }}?v={{ version }}"></script>
<script src="{{ url_for('static', filename='js/tools.js') }}?v={{ version }}"></script>
<script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/uuid/8.3.2/uuid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script> -->

    </body>

    </html>

</template>
<script setup>
import {ref} from 'vue';
import {initVideoData} from '@/stores/init';
// 导入功能模块组件
import updateVideos from '@/components/videos/update_videos.vue';
import cascaderTable from '@/components/tables_element/cascaderTable.vue';
import add_videos from '@/components/videos/add_videos.vue';
import addMertics from '@/components/videos/addMertics.vue';
import {ArrowLeft} from '@element-plus/icons-vue'

const changeId = ref();
const changeProduct = ref();
const updateTableData = ref();
const videoData = initVideoData();
const noticeUpdateAddUpdateData = ref();
const handleRest = (item) => {
    changeId.value = null;
    changeProduct.value = null;
    updateTableData.value = true;
}

const handleItemSelect = (item) => {
    changeId.value = item.value
}

const handleItemSelectProduct = (item) => {
    const obj = new Set();
    item.forEach(element => {
        obj.add(element[2]);
    });
    if (obj.size > 0) {
        changeProduct.value = obj;
    }

}

const handelUpdated = (item) => {
    updateTableData.value = false;
    noticeUpdateAddUpdateData.value = false;
}

const handleAddUpdateData = (item) => {
    // 通知更新update数据和表格数据
    noticeUpdateAddUpdateData.value = item;
}

// // 初始化数据
// onMounted(() => {
//     videoData.initialize();
// });

const goToInfluencers = () => {
    window.open('http://172.16.11.245:5000/influencers', '_blank');
}

const onBack = () => {
    window.open('http://172.16.11.236:37799/webroot/decision#/directory?activeTab=d3b7c734-4360-4833-b0b4-62d5e7cece08', '_blank');
}

</script>
<style scoped>
body{
  overflow:auto;
}

.affix-container {
    text-align: center;
    border-radius: 4px;
    /* margin-bottom: -1%; */
    /* height: 10%; */
    /* background: var(--el-color-primary-light-9); */
}

.statistic-card {
    height: 20px;
}

::v-deep .el-statistic {
    --el-statistic-content-font-size: 28px;
}

.el_btn {
    width: 20%;
    height: 40px;
    font-size: larger;

    /* boxShadow: --el-box-shadow-dark */
}

::v-deep .el-page-header__header {
    padding-top: 1%;
}

::v-deep .el-page-header__left {
    margin-left: 5%;
}

::v-deep .el-page-header__content {
    font-size: 32px;
}

::v-deep .el-page-header__extra {
    margin-right: 5%;
}
</style>