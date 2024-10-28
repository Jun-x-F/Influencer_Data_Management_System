<template>
    <!DOCTYPE html>
    <html lang="zh">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>视频数据管理</title>
        <!-- <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}?v={{ version }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <!-- SweetAlert2 CSS -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css">
    </head>

    <body>
        <div class="header">
            <el-page-header :icon="ArrowLeft" title="返回看板" @back="onBack">
                <template #content>
                    <div class="flex items-center">
                        <el-avatar :size="38" class="mr-3"
                            src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
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
                        <el-col>
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
                        </el-col>

                        <el-col>
                            <add_videos />
                        </el-col>
                    </el-row>


                </template>
            </el-page-header>
        </div>
        <el-divider />
        <div class="container">
            <!-- <h1>视频数据管理</h1> -->

            <section id="videoSection" class="form-container">
                <!-- <div class="affix-container">
                    <el-affix target=".affix-container" :offset="80">
                        <el-button type="primary" class="el_btn">视频数据管理</el-button>
                    </el-affix>
                </div> -->
                <!-- 新增数据按钮 -->


                <updateVideos />


                <!-- 视频数据表格 -->
                <cascaderTable />

                <!-- 新增数据表单 -->

                <div id="addVideoDataForm" class="modal">
                    <div class="modal-content">
                        <span class="close" id="closeAddVideoForm">&times;</span>
                        <form id="addVideoData" autocomplete="off">
                            <div class="form-row">
                                <div>
                                    <label for="addbrand">品牌:</label>
                                    <input list="addBrandOptions" id="addbrand" name="品牌" required>
                                    <datalist id="addBrandOptions">
                                        <!-- 动态加载的品牌选项将插入到这里 -->
                                    </datalist>
                                </div>
                                <div>
                                    <label for="addprojectName">项目:</label>
                                    <input list="addProjectOptions" id="addprojectName" name="项目" required>
                                    <datalist id="addProjectOptions">
                                        <!-- 动态加载的项目选项将插入到这里 -->
                                    </datalist>
                                </div>
                                <div>
                                    <label for="addmanager">负责人:</label>
                                    <input list="addManagerOptions" id="addmanager" name="负责人" required>
                                    <datalist id="addManagerOptions">
                                        <!-- 动态加载的负责人选项将插入到这里 -->
                                    </datalist>
                                </div>
                                <div>
                                    <label for="addInfluencerName">红人名称:</label>
                                    <input list="addInfluencerNameOptions" id="addInfluencerName"
                                        class="addInfluencerName" placeholder="选择或输入红人名称">
                                    <datalist id="addInfluencerNameOptions">
                                        <!-- 选项将在JavaScript中动态生成 -->
                                    </datalist>
                                </div>
                            </div>

                            <div class="form-row">
                                <div>
                                    <label for="addcost">花费:</label>
                                    <input type="number" id="addcost" class="addcost" placeholder="请输入花费">
                                </div>
                                <div>
                                    <label for="addcurrency">币种:</label>
                                    <select id="addcurrency" class="addcurrency">
                                        <option value="">选择币种</option>
                                        <option value="USD">USD - 美元</option>
                                        <option value="EUR">EUR - 欧元</option>
                                        <option value="CNY">CNY - 人民币</option>
                                        <option value="JPY">JPY - 日元</option>
                                        <option value="GBP">GBP - 英镑</option>
                                        <option value="AUD">AUD - 澳元</option>
                                        <option value="CAD">CAD - 加元</option>
                                    </select>
                                </div>
                                <div>
                                    <label for="addproduct">产品:</label>
                                    <input list="addProductOptions" id="addproduct" name="产品" placeholder="请输入或选择产品">
                                    <datalist id="addProductOptions">
                                        <!-- 动态加载的产品选项将插入到这里 -->
                                    </datalist>
                                </div>
                            </div>

                            <div class="form-row">
                                <div>
                                    <label for="addProgress">合作进度:</label>
                                    <input list="addProgressOptions" id="addProgress" class="addProgress"
                                        placeholder="请输入合作进度">
                                    <datalist id="addProgressOptions">
                                        <option value="进行中"></option>
                                        <option value="合作完成"></option>
                                        <option value="合作失败"></option>
                                    </datalist>
                                </div>
                                <div>
                                    <label for="addestimatedViews">预估观看量:</label>
                                    <input type="number" id="addestimatedViews" name="预估观看量">
                                </div>
                                <div>
                                    <label for="addestimatedLaunchDate">预估上线时间:</label>
                                    <input type="date" id="addestimatedLaunchDate" name="预估上线时间">
                                </div>
                            </div>
                            <div>
                                <label for="addLinks">视频链接:</label>
                                <textarea id="addLinks" class="addLinks" placeholder="请输入视频链接"></textarea>
                                <!-- 错误提示 -->
                                <span id="addLinksMessage" class="error-tooltip"></span>
                            </div>
                            <button type="submit" id="addLinksBtn" class="btn-primary">提交</button>
                            <button type="button" id="addresetMetricsForm" class="btn-secondary">重置</button>
                            <button type="button" id="cancelAddVideoData" class="btn-secondary">取消</button>
                            <div id="formErrorMessage" style="color:red;"></div> <!-- 错误提示容器 -->
                        </form>
                    </div>
                </div>

            </section>
            <!-- 指标定义板块 -->
            <section id="metricsDefinitionSection" class="form-container">
                <div class="form-column">
                    <h2>指标定义板块</h2>
                    <form id="metricsDefinitionForm" autocomplete="off">
                        <div class="form-row">
                            <div>
                                <label for="metricsBrand">品牌:</label>
                                <input list="metricsBrandOptions" id="metricsBrand" name="brand" placeholder="请输入或选择品牌"
                                    required>
                                <datalist id="metricsBrandOptions">
                                    <!-- 动态加载的品牌选项将插入到这里 -->
                                </datalist>
                            </div>
                            <div>
                                <label for="metricsProject">项目:</label>
                                <input list="metricsProjectOptions" id="metricsProject" name="project"
                                    placeholder="请输入或选择项目">
                                <datalist id="metricsProjectOptions">
                                    <!-- 动态加载的项目选项将插入到这里 -->
                                </datalist>
                            </div>
                        </div>
                        <div class="form-row">
                            <div>
                                <label for="metricsManager">负责人:</label>
                                <input list="metricsManagerOptions" id="metricsManager" name="manager"
                                    placeholder="请输入或选择负责人">
                                <datalist id="metricsManagerOptions">
                                    <!-- 动态加载的负责人选项将插入到这里 -->
                                </datalist>
                            </div>
                            <div>
                                <label for="metricsProduct">产品:</label>
                                <input list="metricsProductOptions" id="metricsProduct" name="product"
                                    placeholder="请输入或选择产品">
                                <datalist id="metricsProductOptions">
                                    <!-- 动态加载的产品选项将插入到这里 -->
                                </datalist>
                            </div>
                        </div>
                        <div class="form-row">
                            <div>
                                <label for="metricsId">唯一ID（仅用于删除数据）:</label>
                                <input list="metricsIdOptions" id="metricsId" name="id" placeholder="请输入或选择唯一ID">
                                <datalist id="metricsIdOptions">
                                    <!-- 动态加载的唯一ID选项将插入到这里 -->
                                </datalist>
                            </div>
                        </div>

                        <div style="position: relative; width: 100%;">
                            <div style="display: inline-block;">
                                <button type="submit" class="btn-primary">提交指标</button>
                                <button type="button" id="resetMetricsForm" class="btn-secondary">重置</button>
                            </div>
                            <div style="position: absolute; right: 0; top: 0;">
                                <button type="button" id="deleteMetricsData" class="btn-danger">删除</button>
                            </div>
                        </div>
                    </form>
                    <div id="responseMessageMetrics" class="response-message"></div>
                </div>


                <!-- 指标定义数据表 -->
                <div class="form-column">
                    <div id="metricsTableContainer">
                        <table id="metricsTable" border="1">
                            <thead>
                                <tr>
                                    <th class="group1">唯一id</th>
                                    <th class="group1">品牌</th>
                                    <th class="group1">项目</th>
                                    <th class="group1">产品</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- 数据将通过JavaScript动态生成 -->
                            </tbody>
                        </table>
                    </div>
                </div>

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
import { ref, onMounted } from 'vue';
import { initVideoData } from '@/stores/init';
// 导入功能模块组件
import updateVideos from '@/components/videos/update_videos.vue';
import cascaderTable from '@/components/tables_element/cascaderTable.vue';
import add_videos from '@/components/videos/add_videos.vue';
import { ArrowLeft } from '@element-plus/icons-vue'
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