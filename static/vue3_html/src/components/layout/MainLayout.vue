<template>
    <el-container>
        <!-- 导航栏 -->
        <el-header>
            <el-menu :default-active="activeIndex" mode="horizontal" active-text-color="#ffd04b" class="nav-menu"
                @select="handleSelect">
                <!-- Logo区域 -->
                <div class="logo-container">
                    <div ref="chartContainer" class="echarts-logo"></div>
                    <span class="website-name">{{ menuItems.platformName }}</span>
                </div>

                <!-- 右侧菜单项 -->
                <div class="right-menu">
                    <el-menu-item index="1" class="menu-item">{{ menuItems.kolInfo }}</el-menu-item>
                    <el-menu-item index="2" class="menu-item">{{ menuItems.kolVideos }}</el-menu-item>

                    <!-- 任务统计 -->
                    <div class="statistics-container">
                        <el-button class="stat-button" :class="{ 'pending-active': activeStat === 'pending' }"
                            @click="showTaskList('created')">
                            <el-statistic :title="t('statistics.pending')" :value="pendingTasks" class="task-statistic">
                                <template #suffix>
                                    <el-icon>
                                        <Clock />
                                    </el-icon>
                                </template>
                            </el-statistic>
                        </el-button>
                        <el-button class="stat-button" :class="{ 'success-active': activeStat === 'finish' }"
                            @click="showTaskList('finish')">
                            <el-statistic :title="t('statistics.completed')" :value="completedTasks"
                                class="task-statistic success-statistic">
                                <template #suffix>
                                    <el-icon>
                                        <Check />
                                    </el-icon>
                                </template>
                            </el-statistic>
                        </el-button>
                        <el-button class="stat-button" :class="{ 'error-active': activeStat === 'error' }"
                            @click="showTaskList('error')">
                            <el-statistic :title="t('statistics.error')" :value="errorTasks"
                                class="task-statistic error-statistic">
                                <template #suffix>
                                    <el-icon>
                                        <Warning />
                                    </el-icon>
                                </template>
                            </el-statistic>
                        </el-button>
                        <el-button class="stat-button" :class="{ 'processing-active': activeStat === 'processing' }"
                            @click="showTaskList('processing')">
                            <el-statistic :title="t('statistics.processing')" :value="processingTasks"
                                class="task-statistic processing-statistic">
                                <template #suffix>
                                    <el-icon>
                                        <Loading />
                                    </el-icon>
                                </template>
                            </el-statistic>
                        </el-button>

                        <!-- 任务列表对话框 -->
                        <el-dialog v-model="dialogVisible" :title="dialogTitle" width="60%">
                            <el-table :data="paginatedData" style="width: 100%" :max-height="500" stripe>
                                <el-table-column prop="createTime" label="创建时间" width="180" sortable>
                                    <template #default="scope">
                                        <el-tooltip :content="scope.row.createTime" placement="top">
                                            <span>{{ scope.row.createTime }}</span>
                                        </el-tooltip>
                                    </template>
                                </el-table-column>

                                <el-table-column prop="url" label="URL" min-width="200">
                                    <template #default="scope">
                                        <el-tooltip :content="scope.row.url" placement="top">
                                            <el-link type="primary" :href="scope.row.url" target="_blank"
                                                :underline="false">
                                                {{ scope.row.url }}
                                            </el-link>
                                        </el-tooltip>
                                    </template>
                                </el-table-column>

                                <el-table-column prop="status" label="状态" width="120" align="center">
                                    <template #default="scope">
                                        <el-tag :type="getStatusType(scope.row.status)" effect="light">
                                            {{ getStatusText(scope.row.status) }}
                                        </el-tag>
                                    </template>
                                </el-table-column>

                                <el-table-column prop="info" label="详细信息" min-width="150">
                                    <template #default="scope">
                                        <el-tooltip :content="scope.row.info" placement="top">
                                            <span>{{ scope.row.info }}</span>
                                        </el-tooltip>
                                    </template>
                                </el-table-column>
                            </el-table>

                            <!-- 添加分页器 -->
                            <div class="pagination-container">
                                <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize"
                                    :page-sizes="[5, 10]" :small="false" :background="true"
                                    layout="total, sizes, prev, pager, next, jumper" :total="totalItems"
                                    @size-change="handleSizeChange" @current-change="handleCurrentChange" />
                            </div>

                            <template #footer>
                                <div class="dialog-footer">
                                    <el-button @click="dialogVisible = false">关闭</el-button>
                                    <el-button type="primary" @click="refreshTasks">
                                        刷新
                                        <el-icon class="refresh-icon">
                                            <Refresh />
                                        </el-icon>
                                    </el-button>
                                </div>
                            </template>
                        </el-dialog>
                    </div>

                    <!-- 语言切换 -->
                    <el-dropdown @command="handleLanguageChange" class="right-menu-item">
                        <span class="el-dropdown-link">
                            {{ currentLanguage === 'zh' ? '中文' : 'English' }}
                            <el-icon>
                                <ArrowDown />
                            </el-icon>
                        </span>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item command="zh">中文</el-dropdown-item>
                                <el-dropdown-item command="en">English</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>

                    <!-- 主题切换 -->
                    <el-switch v-model="isDark" class="right-menu-item" inline-prompt :active-icon="Moon"
                        :inactive-icon="Sunny" @change="toggleTheme" />
                </div>
            </el-menu>
        </el-header>

        <!-- 主体内容 -->
        <el-main class="bc_color">
            <!-- 使用条件渲染切换内容 -->
            <template v-if="activeIndex === '1'">
                <influencer-table />
            </template>
            <template v-else-if="activeIndex === '2'">
                <VideoTable />
            </template>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref, onMounted, watch, computed, onUnmounted } from 'vue'
import { Moon, Sunny, Clock, Check, Warning, ArrowDown, Refresh, Loading } from '@element-plus/icons-vue'
import InfluencerTable from '@/components/business/influencer/influencer_table.vue'
import VideoTable from '@/components/business/video/video_table.vue'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'
import { useDark, useToggle } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { useInfluencerStore } from '@/store/useInfluencerStore'


// 导航激活项
const activeIndex = ref(localStorage.getItem('lastActiveTab') || '1')
// 使用 vueuse 的 useDark 来管理主题
const isDark = useDark({
    selector: 'html',
    attribute: 'class',
    valueDark: 'dark',
    valueLight: 'light',
    // 添加系统主题跟随
    storageKey: 'vueuse-color-scheme',
    storage: localStorage,
    disableTransition: false,
})
const dialogTitle = ref();
const dialogVisible = ref();
const toggleTheme = useToggle(isDark)
// 语言切换
// 获取i18n实例
const { t, locale } = useI18n()

// 获取浏览器默认语言
const getBrowserLanguage = () => {
    const browserLang = navigator.language.toLowerCase()
    return browserLang.startsWith('zh') ? 'zh' : 'en'
}

// 初始化语言设置
const currentLanguage = ref(localStorage.getItem('user-language') || getBrowserLanguage())

// 语言切换处理
const handleLanguageChange = (lang) => {
    currentLanguage.value = lang
    locale.value = lang
    localStorage.setItem('user-language', lang)
    document.title = t('title')
}

// 主题切换
// 监听主题变化，同步更新 Element Plus 主题
watch(isDark, (val) => {
    const html = document.documentElement
    if (val) {
        html.classList.add('dark')
        document.body.style.setProperty('--el-bg-color', '#141414')
        document.body.style.setProperty('--el-text-color-primary', '#ffffff')
    } else {
        html.classList.remove('dark')
        document.body.style.removeProperty('--el-bg-color')
        document.body.style.removeProperty('--el-text-color-primary')
    }
})

// Echarts logo动画
let myChart = null;

const initECharts = () => {
    const chartDom = document.querySelector('.echarts-logo')
    if (!chartDom) return;

    // 确保DOM元素有尺寸
    if (chartDom.clientWidth === 0 || chartDom.clientHeight === 0) {
        console.warn('DOM元素尺寸为0，等待重试...');
        return;
    }

    // 如果已经存在实例，先销毁
    if (myChart) {
        myChart.dispose();
    }

    myChart = echarts.init(chartDom)

    const option = {
        graphic: {
            elements: [{
                type: 'text',
                left: 'center',
                top: 'center',
                style: {
                    text: 'DeOne KOL',
                    fontSize: 20,
                    fontWeight: 'bold',
                    lineDash: [0, 200],
                    lineDashOffset: 0,
                    fill: 'transparent',
                    stroke: '#ffd04b',
                    lineWidth: 1
                },
                // 在渲染前计算文本宽度
                onCreate: function (el) {
                    const text = el.style.text;
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    ctx.font = `${el.style.fontWeight} ${el.style.fontSize}px sans-serif`;
                    const textWidth = ctx.measureText(text).width;

                    // 更新 lineDash 设置
                    el.style.lineDash = [0, textWidth + 50]; // 添加一些额外空间

                    // 更新动画关键帧中的 lineDash
                    el.keyframeAnimation.keyframes[0].style.lineDash = [textWidth + 50, 0];
                },
                keyframeAnimation: {
                    duration: 3000,
                    loop: true,
                    keyframes: [{
                        percent: 0.7,
                        style: {
                            fill: '#ffd04b',
                            lineDashOffset: 200,
                            // lineDash 将在 onCreate 中动态设置
                        }
                    }, {
                        // 淡出效果
                        percent: 1,
                        style: {
                            fill: 'transparent'
                        }
                    }]
                }
            }]
        }
    }

    myChart.setOption(option)
}

onMounted(() => {
    // 设置初始语言
    handleLanguageChange(currentLanguage.value)

    // 初始化尝试
    initECharts();

    // 如果初始化失败，等待一段时间后重试
    if (!myChart) {
        setTimeout(initECharts, 100);
    }

    // 监听窗口大小变化
    window.addEventListener('resize', () => {
        if (myChart) {
            myChart.resize();
        }
    });
})

// 在组件卸载时清理
onUnmounted(() => {
    if (myChart) {
        myChart.dispose();
        myChart = null;
    }
    window.removeEventListener('resize', () => {
        if (myChart) {
            myChart.resize();
        }
    });
})

// 更新菜单文本
const menuItems = computed(() => ({
    kolInfo: t('menu.kolInfo'),
    kolVideos: t('menu.kolVideos'),
    platformName: t('menu.platformName')
}))

const influencerStore = useInfluencerStore()
const { taskStats } = storeToRefs(influencerStore)

// 处理菜单选择
const handleSelect = (index) => {
    activeIndex.value = index
    // 保存用户的选择到本地存储
    localStorage.setItem('lastActiveTab', index)
    if (index === '1') {
        // 加载KOL信息数据
        influencerStore.getInfluencerList()
    } else if (index === '2') {
        // 加载视频列表数据
        influencerStore.getVideoList()
    }
}

// 使用统计数据
const pendingTasks = computed(() => taskStats.value.created)
const completedTasks = computed(() => taskStats.value.finish)
const errorTasks = computed(() => taskStats.value.error)
const processingTasks = computed(() => taskStats.value.processing)

// 初始化加载数据
onMounted(() => {
    // 根据默认标签加载相应数据
    if (activeIndex.value === '1') {
        influencerStore.getInfluencerList()
    }
    influencerStore.startPolling();
})

// 在组件卸载时停止轮询
onUnmounted(() => {
    influencerStore.stopPolling()
})


// 获取特定状态的任务详情
const getTaskDetails = (status) => {
    return taskStats.value.taskDetails[status] || []
}

const activeStat = ref(null)

// 更新对话框标题生成逻辑
const getDialogTitle = (status) => {
    const statusMap = {
        pending: t('statistics.pendingTasks'),
        finish: t('statistics.completedTasks'),
        error: t('statistics.errorTasks')
    }
    return statusMap[status] || t('statistics.taskList')
}

const showTaskList = (status) => {
    activeStat.value = status
    dialogTitle.value = getDialogTitle(status)
    dialogVisible.value = true
}

// 获取状态显示文本
const getStatusText = (status) => {
    const statusMap = {
        created: t('statistics.pending'),
        processing: t('statistics.processing'),
        finish: t('statistics.completed'),
        error: t('statistics.error')
    }
    return statusMap[status] || status
}

// 获取状态标签类型
const getStatusType = (status) => {
    const typeMap = {
        created: 'info',
        processing: 'warning',
        finish: 'success',
        error: 'danger'
    }
    return typeMap[status] || 'info'
}

// 刷新任务列表
const refreshTasks = async () => {
    await influencerStore.findInfluencerList()
}

// 分页相关的响应式变量
const currentPage = ref(1)
const pageSize = ref(5)
const totalItems = computed(() => {
    const tasks = getTaskDetails(activeStat.value)
    return tasks ? tasks.length : 0
})

// 分页数据计算
const paginatedData = computed(() => {
    const tasks = getTaskDetails(activeStat.value)
    if (!tasks) return []

    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return tasks.slice(start, end)
})

// 处理页码改变
const handleCurrentChange = (val) => {
    currentPage.value = val
}

// 处理每页条数改变
const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1  // 重置到第一页
}

// 当切换任务类型时重置分页
watch(activeStat, () => {
    currentPage.value = 1
})
</script>

<style scoped>
.nav-menu {
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.echarts-logo {
    width: 120px;
    height: 40px;
}



.right-menu {
    display: flex;
    align-items: center;
    gap: 20px;
}

.right-menu-item {
    color: #fff;
    margin-left: 15px;
}

.el-dropdown-link {
    cursor: pointer;
    color: #1f1f1f;
    display: flex;
    align-items: center;
    gap: 5px;
}

.el-header {
    padding: 0;
    height: 10%;
}

.el-menu {
    width: 100%;
    height: 100%;
}

.float-container {
    position: relative;
    min-height: 500px;
}

.float-box {
    width: 45%;
    position: absolute;
    top: 20px;
}

.left {
    left: 0;
}

.right {
    right: 0;
}

.el-card {
    margin-bottom: 20px;
}

.el-container {
    height: 100%;
}

.el-main {
    padding: 20px;
    /* 添加背景色 */
}

.statistics-item {
    cursor: pointer;
}

.statistics-badge :deep(.el-badge__content) {
    background-color: #ffd04b;
    color: #1f1f1f;
}

.statistics-container {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 0 20px;
}

.stat-button {
    height: 80px;
    width: 80px;
    margin: 0;
    padding: 8px 15px;
    border: none;
    transition: all 0.3s ease;
    border-radius: 0;
    background-color: transparent;
}

.stat-button:first-child {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
}

.stat-button:last-child {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

/* 悬浮和激活状态 */
.stat-button:hover,
.pending-active {
    background-color: var(--el-color-info-light-9);
}

.success-statistic:hover .stat-button,
.success-active {
    background-color: var(--el-color-success-light-9);
}

.error-statistic:hover .stat-button,
.error-active {
    background-color: var(--el-color-danger-light-9);
}

/* 暗色主题 */
:deep(.dark) .stat-button:hover,
:deep(.dark) .pending-active {
    background-color: var(--el-color-info-dark-2);
}

:deep(.dark) .success-statistic:hover .stat-button,
:deep(.dark) .success-active {
    background-color: var(--el-color-success-dark-2);
}

:deep(.dark) .error-statistic:hover .stat-button,
:deep(.dark) .error-active {
    background-color: var(--el-color-danger-dark-2);
}

.task-statistic {
    padding: 0;
}

.task-statistic :deep(.el-statistic__content) {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 16px;
}

.task-statistic :deep(.el-statistic__title) {
    font-size: 12px;
    margin-bottom: 2px;
}

.success-statistic :deep(.el-statistic__content) {
    color: var(--el-color-success);
}

.error-statistic :deep(.el-statistic__content) {
    color: var(--el-color-danger);
}

:deep(.dark) .task-statistic {
    color: var(--el-text-color-primary);
}

:deep(.dark) .success-statistic .el-statistic__content {
    color: var(--el-color-success);
}

:deep(.dark) .error-statistic .el-statistic__content {
    color: var(--el-color-danger);
}

:deep(.dark) .pending-button {
    background-color: var(--el-color-info-dark-2);
}

:deep(.dark) .success-button {
    background-color: var(--el-color-success-dark-2);
}

:deep(.dark) .error-button {
    background-color: var(--el-color-danger-dark-2);
}

:deep(.dark) .pending-button:hover {
    background-color: var(--el-color-info);
}

:deep(.dark) .success-button:hover {
    background-color: var(--el-color-success);
}

:deep(.dark) .error-button:hover {
    background-color: var(--el-color-danger);
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
}

.refresh-icon {
    margin-left: 4px;
}

:deep(.el-table) {
    --el-table-border-color: var(--el-border-color-lighter);
    --el-table-header-bg-color: var(--el-fill-color-light);
    border-radius: 8px;
    overflow: hidden;
}

:deep(.el-table th) {
    background-color: var(--el-fill-color-light);
    font-weight: bold;
}

:deep(.el-tag) {
    width: 80px;
}

:deep(.el-link) {
    display: inline-block;
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 暗色主题适配 */
:deep(.dark) .el-dialog {
    background-color: var(--el-bg-color);
}

:deep(.dark) .el-table {
    --el-table-bg-color: var(--el-bg-color);
    --el-table-tr-bg-color: var(--el-bg-color);
    --el-table-header-bg-color: var(--el-bg-color-overlay);
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
    padding: 0 20px;
}

:deep(.el-pagination) {
    margin: 16px 0;
    justify-content: flex-end;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
    background-color: var(--el-color-primary);
}

/* 暗色主题适配 */
:deep(.dark) .el-pagination {
    --el-pagination-button-bg-color: var(--el-bg-color-overlay);
    --el-pagination-hover-color: var(--el-color-primary);
}

/* 添加处理中状态的样式 */
.processing-statistic :deep(.el-statistic__content) {
    color: var(--el-color-warning);
}

.stat-button:hover,
.processing-active {
    background-color: var(--el-color-warning-light-9);
}

:deep(.dark) .processing-active {
    background-color: var(--el-color-warning-dark-2);
}

/* 添加旋转动画 */
.processing-statistic :deep(.el-icon) {
    animation: rotating 2s linear infinite;
}

@keyframes rotating {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

/* 菜单项样式 */
.menu-item {
    position: relative;
    transition: all 0.3s ease;
}

.menu-item:hover,
.menu-item.is-active {
    background-color: var(--el-color-primary-light-9) !important;
}

/* 暗黑模式适配 */
:deep(.dark) .menu-item:hover,
:deep(.dark) .menu-item.is-active {
    background-color: var(--el-color-primary-dark-2) !important;
}

/* 添加底部指示条 */
.menu-item.is-active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background-color: var(--el-color-primary);
}

/* 确保菜单项文字在暗黑模式下可见 */
:deep(.dark) .el-menu--horizontal>.el-menu-item {
    color: var(--el-text-color-primary);
}

:deep(.dark) .el-menu--horizontal>.el-menu-item.is-active {
    color: var(--el-color-primary);
    border-bottom-color: var(--el-color-primary);
}
</style>
