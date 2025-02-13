<template>
    <div class="video-table table_color">
        <!-- 新增视频抽屉 -->
        <AddVideo v-model="isAdd" @close="handleDrawerClose" @update-success="handleUpdateSuccess" />

        <!-- 更新视频抽屉 -->
        <UpdateVideo v-if="updateDrawerVisible" v-model="updateDrawerVisible" :row-data="currentRow"
            @close="handleDrawerClose" @update-success="handleUpdateSuccess" />

        <el-card class="video_card">
            <!-- 添加搜索区域 -->
            <div class="search-area">
                <div class="search-left">
                    <el-input v-model="searchInput" :placeholder="t('influencer.searchPlaceholder')" clearable
                        @keyup.enter="handleSearch" @clear="handleClear" class="search-input">
                        <template #prefix>
                            <el-icon>
                                <Search />
                            </el-icon>
                        </template>
                    </el-input>
                    <el-tag v-for="(tag, index) in searchTags" :key="index" closable class="search-tag"
                        @close="removeSearchTag(index)">
                        {{ tag }}
                    </el-tag>
                </div>
                <div class="search-right">
                    <el-button type="primary" @click="handleAdd">
                        <el-icon>
                            <Plus />
                        </el-icon>
                        {{ t('video.addVideo') }}
                    </el-button>
                    <el-button type="info" @click="showMetrics">
                        <el-icon>
                            <DataLine />
                        </el-icon>
                        查看指标
                    </el-button>
                </div>
            </div>

            <el-table v-loading="influencerStore.isVideoLoading" :data="filteredData" height="650" fixed border
                style="width: 100%" :default-sort="{ prop: 'parentId', order: 'descending' }"
                :span-method="handleSpanMethod" :row-class-name="tableRowClassName" element-loading-text="Loading..."
                element-loading-background="rgba(197, 197, 197, 0.562)" v-el-table-infinite-scroll="handleTableScroll"
                :infinite-scroll-distance="50" :infinite-scroll-delay="200">
                <!-- ID列 -->
                <el-table-column prop="parentId" label="ID" width="80" sortable fixed="left" />
                <!-- 红人名称列 -->
                <el-table-column prop="红人名称" label="红人名称" width="200" fixed="left">
                    <template #default="scope">
                        <span v-html="highlightText(scope.row.红人名称 || scope.row.红人全称)"></span>
                    </template>
                </el-table-column>
                <!-- 其他列 -->
                <el-table-column
                    v-for="column in displayColumns.filter(col => !['parentId', '红人名称'].includes(col.prop))"
                    :key="column.prop" v-bind="column" resizable @header-dragend="handleHeaderDragend">
                    <template #header="{ column }">
                        <div class="draggable-header">
                            <el-icon class="drag-handle">
                                <Operation />
                            </el-icon>
                            <span class="column-title">{{ column.label }}</span>
                        </div>
                    </template>
                    <template #default="scope">
                        <template v-if="column.prop === '平台'">
                            <a v-if="isValidURL(scope.row.视频链接)" :href="scope.row.视频链接" target="_blank"
                                rel="noopener noreferrer">
                                <el-tag :type="getPlatformTagType(scope.row.平台)" effect="dark" class="tag platform-tag">
                                    <span class="platform-icon">{{ getPlatformIcon(scope.row.平台) }}</span>
                                    <span class="platform-text">{{ scope.row.平台 }}</span>
                                </el-tag>
                            </a>
                            <el-tag v-else :type="getPlatformTagType(scope.row.platform)" effect="dark"
                                class="tag platform-tag">
                                <span class="platform-icon">{{ getPlatformIcon(scope.row.platform) }}</span>
                                <span class="platform-text">{{ scope.row.platform }}</span>
                            </el-tag>
                        </template>
                        <template v-else-if="column.prop === '类型'">
                            <a v-if="isValidURL(scope.row.视频链接)" :href="scope.row.视频链接" target="_blank"
                                rel="noopener noreferrer">
                                <el-tag :type="getTypeTagType(scope.row.类型)" effect="light" class="type-tag">
                                    {{ scope.row.类型 }}
                                </el-tag>
                            </a>
                            <el-tag v-else :type="getTypeTagType(scope.row.类型)" effect="light" class="type-tag">
                                {{ scope.row.类型 }}
                            </el-tag>
                        </template>
                        <template v-else-if="column.prop === '物流进度'">
                            <div class="logistics-container">
                                <template v-if="scope.row.物流单号">
                                    <el-tooltip placement="top" :show-after="200" :effect="isDark ? 'dark' : 'light'"
                                        :popper-class="[isDark ? 'dark-tooltip' : 'light-tooltip']">
                                        <template #content>
                                            <div v-loading="logisticsLoading[scope.row.id]" class="logistics-details">
                                                <template v-if="scope.row.物流单号">
                                                    <div v-for="(status, index) in trackingInfo" :key="index"
                                                        class="logistics-item">
                                                        <div class="logistics-item-content">
                                                            <span class="logistics-number">{{ status.number }}</span>
                                                            <el-tag size="small"
                                                                :type="getLogisticsTagType(status.status)"
                                                                effect="light">
                                                                {{ getLogisticsIcon(status.status) }}
                                                                {{ status.status }}
                                                            </el-tag>
                                                        </div>
                                                    </div>
                                                </template>
                                                <div v-else class="no-logistics">暂无物流信息</div>
                                            </div>
                                        </template>
                                        <div class="logistics-display"
                                            @mouseenter="handleLogisticsHover(parseTrackingNumbers(scope.row.物流单号), scope.row.id)">
                                            <el-tag effect="light" class="logistics-tag">
                                                <span class="logistics-icon">📦</span>
                                                <span v-if="getTrackingNumbersCount(scope.row.物流单号) > 0"
                                                    class="logistics-badge">
                                                    {{ getTrackingNumbersCount(scope.row.物流单号) }}
                                                </span>
                                            </el-tag>
                                        </div>
                                    </el-tooltip>
                                </template>
                                <template v-else>
                                    <div class="logistics-display">
                                        <el-tag effect="light" class="logistics-tag">
                                            <span class="logistics-icon">📦</span>
                                        </el-tag>
                                    </div>
                                </template>
                            </div>
                        </template>
                        <template v-else-if="column.prop === '红人名称'">
                            <span v-html="highlightText(scope.row.红人名称 || scope.row.红人全称)"></span>
                        </template>
                        <template v-else-if="column.prop === '合作进度'">
                            <el-tag :type="getProgressTagType(scope.row.合作进度)" effect="dark">
                                {{ scope.row.合作进度 }}
                            </el-tag>
                        </template>
                        <template v-else-if="column.prop === '发布时间'">
                            <el-tooltip :content="getTimeAgo(scope.row.发布时间)" placement="top">
                                <div class="time-wrapper">
                                    <span class="publish-time">{{ formatDateTime(scope.row.发布时间) }}</span>
                                    <span class="time-ago-badge">{{ getShortTimeAgo(scope.row.发布时间) }}</span>
                                </div>
                            </el-tooltip>
                        </template>
                        <template v-else>
                            <span v-html="highlightText(String(scope.row[column.prop] || ''))"></span>
                        </template>
                    </template>
                </el-table-column>

                <!-- 操作列 -->
                <el-table-column fixed="right" label="操作" width="150">
                    <template #default="scope">
                        <el-row :gutter="10">
                            <el-col :span="12">
                                <el-tooltip content="更新" placement="top">
                                    <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                                        更新
                                    </el-button>
                                </el-tooltip>
                            </el-col>
                            <el-col :span="12">
                                <el-tooltip content="删除" placement="top">
                                    <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                                        删除
                                    </el-button>
                                </el-tooltip>
                            </el-col>
                        </el-row>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <!-- 指标组件 -->
        <MetricsList v-model="metricsVisible" />
    </div>
</template>

<script setup lang="ts">
import { useInfluencerStore } from '@/store/useInfluencerStore'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import UpdateVideo from './updateVideo.vue'
import { DataLine, Operation, Plus, Search } from '@element-plus/icons-vue'
import AddVideo from './addVideo.vue'
import { useI18n } from 'vue-i18n'
import Sortable from 'sortablejs'
import MetricsList from '@/components/business/influencer/metrics_list.vue'
import { useDark } from '@vueuse/core'

// 定义物流项接口
interface LogisticsItem {
    number: string;
    status: string;

}

// 扩展 VideoData 接口
interface VideoData {
    id: number;
    parentId: number;
    红人名称?: string;
    红人全称?: string;
    品牌?: string;
    项目?: string;
    平台?: string;
    类型?: string;
    发布时间?: string;
    物流进度?: string;
    合作进度?: string;
    物流链接?: Array<LogisticsItem>;
    视频链接?: string;
    负责人?: string;
    花费?: number;
    币种?: string;
    预估观看量?: number;
    预估上线时间?: string;
    物流单号?: string;
    products?: Array<{
        品牌: string;
        项目: string;
        产品: string;
    }>;
    [key: string]: any; // 添加索引签名以支持动态属性访问
}

// 添加类型定义
type SearchableField = keyof Pick<VideoData,
    'parentId' | '负责人' | '红人名称' | '合作进度' | '物流进度' |
    '品牌' | '项目' | '产品' | '平台' | '类型' | '花费' |
    '预估观看量' | '预估上线时间' | '币种'
>;

// 修改搜索字段配置
const searchableFields: SearchableField[] = [
    'parentId', '负责人', '红人名称', '合作进度', '物流进度',
    '品牌', '项目', '产品', '平台', '类型', '花费',
    '预估观看量', '预估上线时间', '币种'
];

const { t } = useI18n()
const influencerStore = useInfluencerStore()
const editDrawerVisible = ref(false)
const addDrawerVisible = ref(false)
const currentRow = ref<VideoData | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const displayData = ref<VideoData[]>([])
const isDark = useDark()
const trackingInfo = ref<LogisticsItem[]>([])


// influencerStore.isInfluencerLoading.value
// 定义表格列配置
const tableColumns = [
    { prop: 'parentId', label: 'ID', width: 80, sortable: true, fixed: 'left' },
    { prop: '红人名称', label: '红人名称', width: 200, fixed: 'left' },
    { prop: '负责人', label: '负责人', width: 100 },
    { prop: '合作进度', label: '合作进度', width: 120 },
    { prop: '物流进度', label: '物流进度', width: 120 },
    { prop: '品牌', label: '品牌', width: 100 },
    { prop: '项目', label: '项目', width: 200 },
    { prop: '产品', label: '产品', width: 200 },
    { prop: '平台', label: '平台', width: 160 },
    { prop: '类型', label: '类型', width: 140 },
    { prop: '发布时间', label: '发布时间', width: 220, sortable: true },
    { prop: '播放量', label: '播放量', width: 100, sortable: true },
    { prop: '点赞数', label: '点赞数', width: 100, sortable: true },
    { prop: '评论数', label: '评论数', width: 100, sortable: true },
    { prop: '收藏数', label: '收藏数', width: 100, sortable: true },
    { prop: '转发数', label: '转发数', width: 100, sortable: true },
    { prop: '参与率', label: '参与率', width: 100, sortable: true },
    { prop: '花费', label: '花费', width: 100 },
    { prop: '预估观看量', label: '预估观看量', width: 120 },
    { prop: '预估上线时间', label: '预估上线时间', width: 120 },
    { prop: '币种', label: '币种', width: 100 }
]

// 用于显示的列顺序
const displayColumns = ref([...tableColumns])

const searchInput = ref('')
const searchTags = ref<string[]>([])

// 添加 searchKeywords 计算属性
const searchKeywords = computed(() => {
    const keywords: string[] = [...searchTags.value]
    if (searchInput.value.trim()) {
        keywords.push(searchInput.value.trim())
    }
    return keywords
})

// 添加 searchCache 计算属性
const searchCache = ref(new Map())

// 添加 filteredData 计算属性
const filteredData = computed<VideoData[]>(() => {
    return displayData.value
})

// 计算处理后的数据
const processedData = computed<VideoData[]>(() => {
    return displayData.value
})

// 添加状态保持相关的变量
const currentSearchState = ref({
    keywords: [] as string[],
    currentData: [] as VideoData[],
    scrollPosition: 0
});

// 修改handleSearch方法
const handleSearch = () => {
    if (!searchInput.value.trim()) {
        displayData.value = influencerStore.videoList.slice(0, pageSize.value)
        return
    }

    const searchText = searchInput.value.trim()
    searchTags.value.push(searchText)
    searchInput.value = ''

    const keywords = searchKeywords.value
    const cacheKey = keywords.sort().join(',')

    if (searchCache.value.has(cacheKey)) {
        displayData.value = searchCache.value.get(cacheKey)
        return
    }

    const results = influencerStore.videoList.filter((row: VideoData) => {
        return keywords.every(keyword => {
            if (!keyword) return true
            const searchText = keyword.toLowerCase()
            return searchableFields.some(field => {
                const fieldValue = String(row[field] || '').toLowerCase()
                return fieldValue.includes(searchText)
            })
        })
    })

    searchCache.value.set(cacheKey, results)
    displayData.value = results
}

// 修改handleTableScroll方法
const handleTableScroll = async () => {
    if (influencerStore.isVideoLoading) return;

    influencerStore.isVideoLoading = true;

    try {
        // 判断是否处于搜索状态
        const isSearching = searchTags.value.length > 0;
        // 获取源数据
        const sourceList = isSearching
            ? displayData.value  // 如果在搜索状态，使用当前显示的数据
            : influencerStore.videoList;

        const start = displayData.value.length;
        const end = start + pageSize.value;

        if (start >= sourceList.length) {
            influencerStore.isVideoLoading = false;
            return;
        }

        const newData = sourceList.slice(start, end);
        displayData.value = [...displayData.value, ...newData];
    } catch (error) {
        console.error('加载数据失败:', error);
        ElMessage.error('加载数据失败');
    } finally {
        setTimeout(() => {
            influencerStore.isVideoLoading = false;
        }, 300);
    }
};

// 初始化加载
onMounted(async () => {
    currentPage.value = 1
    displayData.value = []
    await influencerStore.getVideoList()
    displayData.value = influencerStore.videoList.slice(0, pageSize.value)
    initSortable()
})

// 组件卸载时清理
onBeforeUnmount(() => {
    displayData.value = []
    currentPage.value = 1
    influencerStore.videoList = []
    clearSearchCache()
})

// 处理单元格合并
const handleSpanMethod = ({ row, column, rowIndex }: { row: VideoData; column: { property: string }; rowIndex: number }) => {
    if (!row.parentId) return [1, 1]

    // 特殊处理品牌、项目、产品的合并逻辑
    if (column.property === '品牌' || column.property === '项目' || column.property === '产品') {
        const prevRow = filteredData.value[rowIndex - 1]
        let span = 1

        // 如果是品牌列
        if (column.property === '品牌') {
            // 与前一行比较品牌
            if (prevRow && prevRow.parentId === row.parentId && prevRow.品牌 === row.品牌) {
                return [0, 1]
            }
            // 计算后续相同品牌的行数
            for (let i = rowIndex + 1; i < filteredData.value.length; i++) {
                const nextRow = filteredData.value[i]
                if (nextRow.parentId === row.parentId && nextRow.品牌 === row.品牌) {
                    span++
                } else {
                    break
                }
            }
        }
        // 如果是项目列
        else if (column.property === '项目') {
            // 与前一行比较品牌和项目
            if (prevRow && prevRow.parentId === row.parentId &&
                prevRow.品牌 === row.品牌 && prevRow.项目 === row.项目) {
                return [0, 1]
            }
            // 计算后续相同品牌和项目的行数
            for (let i = rowIndex + 1; i < filteredData.value.length; i++) {
                const nextRow = filteredData.value[i]
                if (nextRow.parentId === row.parentId &&
                    nextRow.品牌 === row.品牌 && nextRow.项目 === row.项目) {
                    span++
                } else {
                    break
                }
            }
        }
        // 产品列不合并
        else if (column.property === '产品') {
            return [1, 1]
        }

        return [span, 1]
    }

    // 其他列的合并逻辑保持不变
    const spanMap = new Map()
    filteredData.value.forEach((item, index) => {
        if (!spanMap.has(item.parentId)) {
            spanMap.set(item.parentId, {
                start: index,
                count: 1,
                value: item[column.property]
            })
        } else {
            const info = spanMap.get(item.parentId)
            if (info.value === item[column.property]) {
                info.count++
            } else {
                info.count = 1
                info.start = index
                info.value = item[column.property]
            }
        }
    })

    const prevRow = filteredData.value[rowIndex - 1]
    if (prevRow && prevRow.parentId === row.parentId &&
        prevRow[column.property] === row[column.property]) {
        return [0, 0]
    }

    let span = 1
    for (let i = rowIndex + 1; i < filteredData.value.length; i++) {
        const nextRow = filteredData.value[i]
        if (nextRow.parentId === row.parentId &&
            nextRow[column.property] === row[column.property]) {
            span++
        } else {
            break
        }
    }
    return [span, 1]
}

// 表格行样式
const tableRowClassName = ({ row }: { row: VideoData }) => {
    if (!row.parentId) return ''
    return row.parentId % 2 === 0 ? 'even-row' : 'odd-row'
}

// 修改高亮文本方法
const highlightText = (text: string): string => {
    if (!text) return ''
    let result = text
    searchKeywords.value.forEach(keyword => {
        if (!keyword) return
        // 转义正则表达式中的特殊字符
        const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        // 使用零宽断言确保不会匹配到已经高亮的文本
        const reg = new RegExp(`(?<!<[^>]*)(${escapedKeyword})(?![^<]*>)`, 'gi')
        result = result.replace(reg, '<span class="highlight-text">$1</span>')
    })
    return result
}

// 更新成功回调
const handleUpdateSuccess = async () => {
    try {
        // 保存当前状态
        currentSearchState.value = {
            keywords: [...searchTags.value],
            currentData: [...displayData.value],
            scrollPosition: document.querySelector('.el-table__body-wrapper')?.scrollTop || 0
        };

        // 重新加载数据
        await influencerStore.getVideoList();

        // 如果有搜索关键词，应用现有的筛选条件
        if (currentSearchState.value.keywords.length > 0) {
            searchTags.value = [...currentSearchState.value.keywords];
            const results = influencerStore.videoList.filter((row: VideoData) => {
                return searchTags.value.every(keyword => {
                    if (!keyword) return true;
                    const searchText = keyword.toLowerCase();
                    return searchableFields.some(field => {
                        const fieldValue = String(row[field] || '').toLowerCase();
                        return fieldValue.includes(searchText);
                    });
                });
            });
            displayData.value = results;
        } else {
            // 如果没有搜索关键词，保持当前显示的数据量
            const currentLength = currentSearchState.value.currentData.length;
            displayData.value = influencerStore.videoList.slice(0, currentLength);
        }

        // 恢复滚动位置
        nextTick(() => {
            const tableBody = document.querySelector('.el-table__body-wrapper');
            if (tableBody) {
                tableBody.scrollTop = currentSearchState.value.scrollPosition;
            }
        });

        ElMessage.success(t('message.updateSuccess'));
    } catch (error) {
        console.error('更新列表失败:', error);
        ElMessage.error(t('message.updateFailed'));
    }
};

// 修改组件状态变量
const isAdd = ref(false)
const updateDrawerVisible = ref(false)

// 处理编辑
const handleEdit = (row: VideoData) => {
    currentRow.value = { ...row };
    updateDrawerVisible.value = true;
}

// 处理新增
const handleAdd = () => {
    isAdd.value = true;
}

// 处理抽屉关闭
const handleDrawerClose = () => {
    isAdd.value = false;
    updateDrawerVisible.value = false;
    currentRow.value = null;
}

// 修改 Sortable 的类型定义
interface SortableEvent {
    oldIndex?: number;
    newIndex?: number;
}

// 修改 initSortable 方法
const initSortable = () => {
    const maxRetries = 5;
    let retryCount = 0;

    const tryInit = () => {
        const el = document.querySelector('.el-table__header-wrapper .el-table__header thead tr');
        if (!el || el.clientWidth === 0) {
            if (retryCount < maxRetries) {
                retryCount++;
                setTimeout(tryInit, 200); // 200ms 后重试
                return;
            }
            console.warn('初始化表格布局失败，请检查表格是否正确渲染');
            return;
        }

        // 恢复列宽度
        const savedWidths = localStorage.getItem('tableColumnWidths');
        if (savedWidths) {
            try {
                const widths = JSON.parse(savedWidths);
                displayColumns.value = displayColumns.value.map(col => ({
                    ...col,
                    width: widths[col.prop] || col.width
                }));
            } catch (e) {
                console.error('Error parsing saved column widths:', e);
            }
        }

        // 初始化拖拽排序
        Sortable.create(el as HTMLElement, {
            handle: '.drag-handle',
            animation: 150,
            onEnd(event: SortableEvent) {
                const { oldIndex, newIndex } = event;
                if (typeof oldIndex === 'number' && typeof newIndex === 'number' && oldIndex !== newIndex) {
                    const columnsCopy = [...displayColumns.value];
                    const [removed] = columnsCopy.splice(oldIndex, 1);
                    columnsCopy.splice(newIndex, 0, removed);
                    displayColumns.value = columnsCopy;
                    localStorage.setItem('tableColumnsOrder', JSON.stringify(columnsCopy));
                }
            }
        });

        // 监听列宽度变化
        const table = document.querySelector('.el-table');
        if (table) {
            const observer = new MutationObserver(() => {
                const headers = document.querySelectorAll('.el-table__header-wrapper th');
                const widths: { [key: string]: number } = {};
                headers.forEach((header: Element) => {
                    const prop = header.getAttribute('data-column-id');
                    if (prop) {
                        const width = (header as HTMLElement).style.width;
                        if (width) {
                            widths[prop] = parseInt(width);
                        }
                    }
                });
                if (Object.keys(widths).length > 0) {
                    localStorage.setItem('tableColumnWidths', JSON.stringify(widths));
                }
            });

            observer.observe(table, {
                attributes: true,
                subtree: true,
                attributeFilter: ['style']
            });
        }
    };

    // 开始尝试初始化
    tryInit();
};


// 添加物流状态标签类型获取函数
const getLogisticsTagType = (status: string): string => {
    switch (status) {
        case '成功签收':
            return 'success';
        case '运输途中':
            return 'warning';
        case '待发货':
            return 'info';
        case '异常':
            return 'danger';
        default:
            return 'info';
    }
}


// 在组件挂载时恢复保存的列顺序
onMounted(() => {
    const savedOrder = localStorage.getItem('tableColumnsOrder');
    if (savedOrder) {
        try {
            displayColumns.value = JSON.parse(savedOrder);
        } catch (e) {
            console.error('Error parsing saved column order:', e);
        }
    }
    initSortable();
});

const getProgressTagType = (progress: string): string => {
    if (!progress) return 'info'
    switch (progress) {
        case '合作完成':
            return 'success'
        case '进行中':
            return 'warning'
        case '待开始':
            return 'info'
        case '合作失败':
            return 'danger'
        default:
            return 'info'
    }
}

const getTypeTagType = (type: string) => {
    switch (type) {
        case '视频':
            return 'primary'
        case '短视频':
            return 'success'
        case '图片':
            return 'warning'
        default:
            return 'info'
    }
}

interface PlatformType {
    [key: string]: string;
}

// 验证URL的函数
const isValidURL = (url: string): boolean => {
    if (!url) return false
    try {
        new URL(url)
        return true
    } catch {
        return false
    }
}

const getPlatformTagType = (platform: string | undefined): string => {
    if (!platform) return 'info'
    const typeMap: PlatformType = {
        'youtube': 'danger',
        'instagram': 'warning',
        'tiktok': 'success',
        'x': 'info',
        'facebook': 'primary',
        'twitch': 'purple',
        'linkedin': 'info',
    }
    return typeMap[platform.toLowerCase()] || 'info'
}

const getPlatformIcon = (platform: string | undefined): string => {
    if (!platform) return '🌐'
    const iconMap: PlatformType = {
        'youtube': '📺',
        'instagram': '📷',
        'tiktok': '🎵',
        'x': '🐦',
        'facebook': '👥',
        'twitch': '🎮',
        'linkedin': '',
    }
    return iconMap[platform.toLowerCase()] || '🌐'
}

// 在script部分添加格式化函数
const formatDateTime = (dateTimeStr: string): string => {
    if (!dateTimeStr) return ''
    try {
        const date = new Date(dateTimeStr)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        const seconds = String(date.getSeconds()).padStart(2, '0')
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    } catch {
        return dateTimeStr
    }
}

// 获取时间间隔（详细版本）
const getTimeAgo = (dateTimeStr: string): string => {
    if (!dateTimeStr) return ''
    try {
        const date = new Date(dateTimeStr)
        const now = new Date()
        const diff = now.getTime() - date.getTime()
        const days = Math.floor(diff / (1000 * 60 * 60 * 24))
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

        if (days > 0) {
            return `在${days}天${hours}小时前发布`
        } else if (hours > 0) {
            return `在${hours}小时${minutes}分钟前发布`
        } else if (minutes > 0) {
            return `在${minutes}分钟前发布`
        } else {
            return '在刚刚发布'
        }
    } catch {
        return ''
    }
}

// 获取时间间隔（简短版本）
const getShortTimeAgo = (dateTimeStr: string): string => {
    if (!dateTimeStr) return ''
    try {
        const date = new Date(dateTimeStr)
        const now = new Date()
        const diff = now.getTime() - date.getTime()
        const days = Math.floor(diff / (1000 * 60 * 60 * 24))
        if (days > 0) {
            return days + '天前'
        }
        const hours = Math.floor(diff / (1000 * 60 * 60))
        if (hours > 0) {
            return hours + '小时前'
        }
        const minutes = Math.floor(diff / (1000 * 60))
        if (minutes > 0) {
            return minutes + '分钟前'
        }
        return '刚刚'
    } catch {
        return ''
    }
}

// 修改removeSearchTag方法
const removeSearchTag = (index: number) => {
    searchTags.value.splice(index, 1)
    clearSearchCache()

    if (searchTags.value.length === 0) {
        displayData.value = influencerStore.videoList.slice(0, pageSize.value)
        return
    }

    const keywords = searchKeywords.value
    const cacheKey = keywords.sort().join(',')

    if (searchCache.value.has(cacheKey)) {
        displayData.value = searchCache.value.get(cacheKey)
        return
    }

    const results = influencerStore.videoList.filter((row: VideoData) => {
        return keywords.every(keyword => {
            if (!keyword) return true
            const searchText = keyword.toLowerCase()
            return searchableFields.some(field => {
                const fieldValue = String(row[field] || '').toLowerCase()
                return fieldValue.includes(searchText)
            })
        })
    })

    searchCache.value.set(cacheKey, results)
    displayData.value = results
}

// 修改handleClear方法
const handleClear = () => {
    searchInput.value = ''
    searchTags.value = []
    clearSearchCache()
    displayData.value = influencerStore.videoList.slice(0, pageSize.value)
}

// 清理缓存的方法
const clearSearchCache = () => {
    searchCache.value.clear()
}

// 添加处理列宽度变化的方法
const handleHeaderDragend = (newWidth: number, oldWidth: number, column: any) => {
    // 保存新的列宽度
    const columnWidths = JSON.parse(localStorage.getItem('tableColumnWidths') || '{}')
    columnWidths[column.property] = newWidth
    localStorage.setItem('tableColumnWidths', JSON.stringify(columnWidths))

    // 更新 displayColumns 中的宽度
    const index = displayColumns.value.findIndex(col => col.prop === column.property)
    if (index !== -1) {
        displayColumns.value[index] = {
            ...displayColumns.value[index],
            width: newWidth
        }
    }
}

// 更新物流状态图标获取函数
const getLogisticsIcon = (status: string): string => {
    switch (status) {
        case '待发货':
            return '📦';
        case '成功签收':
            return '✅';
        case '交付':
            return '🔄';
        default:
            return '📋';
    }
};

// 获取主要显示的物流状态
const getMainLogisticsStatus = (row: VideoData): string => {
    if (!row.物流链接 || row.物流链接.length === 0) {
        return row.物流进度 || '暂无物流';
    }

    const pendingLogistics = row.物流链接.find((item: LogisticsItem) => item.status === '待发货');
    if (pendingLogistics) {
        return pendingLogistics.status;
    }

    const deliveringLogistics = row.物流链接.find((item: LogisticsItem) => item.status === '交付');
    if (deliveringLogistics) {
        return deliveringLogistics.status;
    }

    return row.物流链接[row.物流链接.length - 1].status;
}


// 获取主要物流状态的标签类型
const getMainLogisticsTagType = (row: VideoData): string => {
    const mainStatus = getMainLogisticsStatus(row);
    return getLogisticsTagType(mainStatus);
}

// 格式化物流详情
const formatLogisticsDetails = (logisticsList: Array<LogisticsItem>): Array<LogisticsItem> => {
    if (!logisticsList) return [];
    return logisticsList.map(line => {
        const [number, status] = line.split(': ').map(s => s.trim());
        return { number, status };
    });
}

// 添加指标相关的状态
const metricsVisible = ref(false)

// 添加显示指标的方法
const showMetrics = () => {
    metricsVisible.value = true
}

// 处理删除
const handleDelete = async (row: VideoData) => {
    try {
        // 保存当前状态
        currentSearchState.value = {
            keywords: [...searchTags.value],
            currentData: [...displayData.value],
            scrollPosition: document.querySelector('.el-table__body-wrapper')?.scrollTop || 0
        };

        const relatedRows = processedData.value.filter(item => item.parentId === row.parentId);
        const ids = relatedRows.map(item => item.id);

        await ElMessageBox.confirm(
            '确定要删除这些记录吗？',
            '警告',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }
        );

        await influencerStore.deleteVideo(row.parentId);
        ElMessage.success('删除成功');

        // 重新加载数据并应用筛选
        await influencerStore.getVideoList();
        if (currentSearchState.value.keywords.length > 0) {
            searchTags.value = [...currentSearchState.value.keywords];
            const results = influencerStore.videoList.filter((row: VideoData) => {
                return searchTags.value.every(keyword => {
                    if (!keyword) return true;
                    const searchText = keyword.toLowerCase();
                    return searchableFields.some(field => {
                        const fieldValue = String(row[field] || '').toLowerCase();
                        return fieldValue.includes(searchText);
                    });
                });
            });
            displayData.value = results;
        } else {
            const currentLength = currentSearchState.value.currentData.length;
            displayData.value = influencerStore.videoList.slice(0, currentLength);
        }

        // 恢复滚动位置
        nextTick(() => {
            const tableBody = document.querySelector('.el-table__body-wrapper');
            if (tableBody) {
                tableBody.scrollTop = currentSearchState.value.scrollPosition;
            }
        });
    } catch (error) {
        if (error !== 'cancel') {
            ElMessage.error('删除失败');
        }
    }
};

const logisticsLoading = ref<{ [key: number]: boolean }>({})

// 获取物流单号数量
const getTrackingNumbersCount = (trackingUrl: string): number => {
    if (!trackingUrl) return 0;
    const numbers = parseTrackingNumbers(trackingUrl);
    return numbers.length;
}

// 解析物流单号
const parseTrackingNumbers = (trackingUrl: string): string[] => {
    if (!trackingUrl) return [];

    try {
        // 处理17track的链接格式
        if (trackingUrl.includes('17track.net')) {
            const numsMatch = trackingUrl.match(/nums=([^#&]+)/);
            if (numsMatch && numsMatch[1]) {
                return numsMatch[1].split(',').map(num => num.trim());
            }
        }

        // 处理其他可能的格式
        if (trackingUrl.includes(',')) {
            return trackingUrl.split(',').map(num => num.trim());
        }

        // 如果只有单个单号
        return [trackingUrl.trim()];
    } catch (error) {
        console.error('解析物流单号失败:', error);
        return [];
    }
}

// 处理物流信息悬停
const handleLogisticsHover = async (numbers: any, id: any) => {
    console.log(numbers);
    if (numbers === null) {
        return
    }
    try {
        logisticsLoading[id] = true
        const tracking = await influencerStore.queryTrackingStatus(numbers);
        console.log(tracking);
        trackingInfo.value = tracking;
        console.log(trackingInfo.value);
    } catch (error) {
        console.error('处理物流信息悬停 ', error);
    } finally {
        logisticsLoading[id] = false
    }
}

</script>

<style scoped>
.video-table {
    width: 100%;
    border-radius: 5px;
}

.video_card {
    margin: 0 auto;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    background: #fff;
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }

    animation: cardFadeIn 0.5s ease-out;
}

@keyframes cardFadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 表格样式优化 */
:deep(.el-table) {
    border-radius: 4px;
    overflow: hidden;
    transition: all 0.3s ease;
}

:deep(.el-table__row) {
    transition: all 0.2s ease;
    height: 50px;
    line-height: 50px;

    &:hover {
        background-color: #f5f7fa;
        transform: scale(1.001);
    }
}

:deep(.el-table__cell) {
    padding: 8px 0;
}

:deep(.el-table__header-wrapper th) {
    background-color: #f5f7fa;
    font-weight: 600;
    color: #606266;
}

/* 滚动条美化 */
:deep(.el-table__body-wrapper::-webkit-scrollbar) {
    width: 6px;
    height: 6px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
    border-radius: 3px;
    background-color: #dcdfe6;

    &:hover {
        background-color: #c0c4cc;
    }
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
    background-color: #f5f7fa;
}

/* 按钮样式 */
.el-button {
    padding: 4px 8px;
    margin: 0 4px;
    transition: all 0.3s ease;
}

.el-button--danger:hover {
    transform: scale(1.05);
}

/* 暗黑模式适配 */
html.dark {
    .video_card {
        background: #1f1f1f;
        border-color: #363636;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    :deep(.el-table) {
        background-color: #1f1f1f;
        color: #ffffff;

        td.el-table__cell {
            background-color: #1f1f1f;
            border-bottom: 1px solid #363636;
        }

        th.el-table__cell {
            background-color: #2c2c2c !important;
            border-bottom: 1px solid #363636;
            color: #ffffff;
        }
    }

    :deep(.el-table__row:hover > td) {
        background-color: #363636 !important;
    }

    :deep(.el-table--striped .el-table__row--striped td) {
        background-color: #2c2c2c;
    }
}

/* 添加搜索区域样式 */
.search-area {
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
}

.search-left {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    flex: 1;
}

.search-right {
    display: flex;
    align-items: center;
    gap: 12px;
    /* 添加按钮间距 */
}

.search-input {
    width: 300px;
}

.search-tag {
    margin-right: 4px;
    animation: tagFadeIn 0.3s ease-out;
}

@keyframes tagFadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 暗黑模式适配 */
html.dark {
    .search-area {
        :deep(.el-input__inner) {
            background-color: var(--el-bg-color-overlay);
            border-color: var(--el-border-color-light);
        }
    }

    /* ... 其他暗黑模式样式保持不变 ... */
}

:deep(.highlight-text) {
    color: var(--el-color-primary);
    font-weight: bold;
}

/* 暗黑模式下的高亮样式 */
html.dark :deep(.highlight-text) {
    color: var(--el-color-primary-light-3);
}

:deep(.odd-row) {
    background-color: var(--el-table-row-hover-bg-color);
}

:deep(.even-row) {
    background-color: var(--el-bg-color);
}

/* 修改悬停样式 */
:deep(.el-table__row:hover > td) {
    background-color: var(--el-color-primary-light-9) !important;
}

/* 暗黑模式适配 */
html.dark {
    :deep(.odd-row) {
        background-color: #2a2a2a;
        /* 深色但比even-row略亮 */
    }

    :deep(.even-row) {
        background-color: #1a1a1a;
        /* 更深的背景色 */
    }

    /* 暗黑模式下的悬停样式 */
    :deep(.el-table__row:hover > td) {
        background-color: #363636 !important;
        /* 鼠标悬停时的颜色 */
    }

    /* 确保表格边框在暗色模式下可见 */
    :deep(.el-table) {
        --el-table-border-color: #4c4c4c;
        --el-table-header-bg-color: #2c2c2c;
    }

    /* 表头样式 */
    :deep(.el-table__header-wrapper th) {
        background-color: #2c2c2c !important;
        border-bottom: 1px solid #4c4c4c;
        color: #ffffff;
    }

    /* 单元格边框 */
    :deep(.el-table__cell) {
        border-bottom: 1px solid #363636;
    }
}

/* 新增按钮动画效果 */
.el-button {
    transition: all 0.3s ease;

    &:hover {
        transform: scale(1.05);
    }
}

.draggable-header {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: move;
    width: 100%;
    justify-content: space-between;
}

.column-title {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.drag-handle {
    cursor: move;
    padding: 2px;
    border-radius: 4px;
    transition: all 0.2s ease;
    margin-left: auto;

    &:hover {
        background-color: var(--el-color-primary-light-8);
        color: var(--el-color-primary);
    }
}

/* 确保表头内容不换行 */
:deep(.el-table__header th) {
    white-space: nowrap;

    .cell {
        display: flex;
        align-items: center;
    }
}

/* 确保排序图标在右侧 */
:deep(.el-table__column-sort-icon) {
    margin-left: auto;
}

/* 标签样式优化 */
:deep(.el-tag) {
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 500;
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
}

/* 进度标签特殊样式 */
:deep(.el-tag--success) {
    background-color: rgba(103, 194, 58, 0.1);
    border-color: rgba(103, 194, 58, 0.2);
    color: #67c23a;
}

:deep(.el-tag--warning) {
    background-color: rgba(230, 162, 60, 0.1);
    border-color: rgba(230, 162, 60, 0.2);
    color: #e6a23c;
}

:deep(.el-tag--danger) {
    background-color: rgba(245, 108, 108, 0.1);
    border-color: rgba(245, 108, 108, 0.2);
    color: #f56c6c;
}

:deep(.el-tag--info) {
    background-color: rgba(144, 147, 153, 0.1);
    border-color: rgba(144, 147, 153, 0.2);
    color: #909399;
}

/* 表头拖拽时的样式 */
:deep(.sortable-ghost) {
    background-color: var(--el-color-primary-light-9);
    opacity: 0.8;
}

:deep(.sortable-drag) {
    background-color: var(--el-color-primary-light-8);
    opacity: 0.9;
}

/* 平台标签基础样式 */
/* 平台标签基础样式（修改后，与 a.vue 保持一致） */
.platform-tag {
    padding: 8px 15px;
    font-weight: 600;
    border-radius: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-transform: capitalize;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-width: 100px;
    justify-content: center;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}


/* 图标样式 */
.platform-icon {
    font-size: 16px;
    line-height: 1;
    flex-shrink: 0;
}

/* 文本样式 */
.platform-text {
    font-size: 14px;
    letter-spacing: 0.5px;
    font-weight: 600;
    flex: 1;
    text-align: center;
    display: inline-block;
}

/* 类型标签样式 */
.type-tag {
    padding: 4px 8px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    /* 使用完整宽度 */
}

/* 确保表格单元格内容不会溢出 */
:deep(.el-table__cell) {
    .cell {
        white-space: nowrap;
    }
}

/* 发布时间样式 */
.publish-time {
    font-family: 'Roboto Mono', monospace;
    color: var(--el-text-color-primary);
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 500;
    letter-spacing: 0.5px;
    display: inline-block;
}

/* 暗黑模式下的发布时间样式 */
html.dark .publish-time {
    color: var(--el-text-color-primary);
}

.time-wrapper {
    position: relative;
    display: inline-block;
}

.time-ago-badge {
    position: absolute;
    top: -8px;
    right: -12px;
    font-size: 12px;
    padding: 1px 4px;
    border-radius: 8px;
    background: var(--el-color-primary-light-8);
    color: var(--el-color-primary);
    font-weight: 500;
    transform: scale(0.8);
}

/* 暗黑模式下的时间间隔标签样式 */
html.dark .time-ago-badge {
    background: var(--el-color-primary-light-3);
    color: var(--el-color-primary-light-9);
}

/* 物流容器样式 */
.logistics-container {
    padding: 4px;
    width: 100%;
    position: relative;
    /* 添加相对定位 */
}

.logistics-display {
    display: inline-flex;
    align-items: center;
    width: 100%;
    padding-right: 8px;
    /* 添加右边距，为徽标留出空间 */
}

.logistics-tag {
    width: 100%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 12px;
    border-radius: 6px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: visible;
    margin-right: 8px;
    /* 添加右边距，为徽标留出空间 */
}

.logistics-tag:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.logistics-tag.is-active {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(var(--el-color-warning-rgb), 0.4);
    }

    70% {
        box-shadow: 0 0 0 10px rgba(var(--el-color-warning-rgb), 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(var(--el-color-warning-rgb), 0);
    }
}

.logistics-icon {
    font-size: 16px;
    line-height: 1;
    flex-shrink: 0;
}

.logistics-text {
    font-weight: 500;
    flex-shrink: 0;
}

.logistics-badge {
    position: absolute;
    top: -6px;
    /* 调整上边距 */
    right: -12px;
    /* 调整右边距 */
    min-width: 18px;
    /* 增加最小宽度 */
    height: 18px;
    /* 增加高度 */
    padding: 0 6px;
    /* 增加水平内边距 */
    background-color: var(--el-color-primary);
    color: white;
    font-size: 12px;
    font-weight: bold;
    border-radius: 9px;
    /* 增加圆角 */
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transform: scale(0.9);
    /* 稍微缩小一点 */
    z-index: 1;
    /* 确保显示在最上层 */
}

.logistics-details {
    min-width: 300px;
    max-width: 400px;
    padding: 16px;
}

.logistics-item {
    padding: 8px;
    border-bottom: 1px solid var(--el-border-color-lighter);

    &:last-child {
        border-bottom: none;
    }
}

.logistics-item-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}

.logistics-number {
    font-family: 'Roboto Mono', monospace;
    font-size: 13px;
    color: var(--el-text-color-regular);
}

/* Tooltip 样式优化 */
:deep(.dark-tooltip) {
    background-color: var(--el-color-black) !important;
    color: var(--el-color-white) !important;
}

:deep(.light-tooltip) {
    background-color: var(--el-bg-color) !important;
    color: var(--el-text-color-primary) !important;
    border: 1px solid var(--el-border-color-light) !important;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) !important;
}

/* 暗黑模式适配 */
html.dark {
    .logistics-tag {
        background-color: var(--el-bg-color);
        border-color: var(--el-border-color-darker);
    }

    .logistics-number {
        color: var(--el-text-color-secondary);
    }

    .logistics-details {
        background-color: var(--el-bg-color);
        border: 1px solid var(--el-border-color-darker);
    }

    .logistics-item {
        border-bottom-color: var(--el-border-color-darker);
    }

    .logistics-time {
        color: var(--el-text-color-secondary);
    }

    .logistics-badge {
        background-color: var(--el-color-primary);
        color: white;
    }
}

/* 平台标签特定样式 */
:deep(.platform-tag.el-tag) {
    padding: 8px 15px !important;
    font-weight: 600 !important;
    border-radius: 20px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: capitalize !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    min-width: 100px !important;
    justify-content: center !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

/* 平台标签渐变背景 */
:deep(.platform-tag.el-tag--danger) {
    background: linear-gradient(45deg, #FF0000, #FF4444) !important;
    border: none !important;
    color: white !important;
}

:deep(.platform-tag.el-tag--warning) {
    background: linear-gradient(45deg, #C13584, #E1306C, #F77737) !important;
    border: none !important;
    color: white !important;
}

:deep(.platform-tag.el-tag--success) {
    background: linear-gradient(45deg, #25F4EE, #000000, #FE2C55) !important;
    border: none !important;
    color: white !important;
}

:deep(.platform-tag.el-tag--info) {
    background: linear-gradient(45deg, #1DA1F2, #14171A) !important;
    border: none !important;
    color: white !important;
}

:deep(.platform-tag.el-tag--primary) {
    background: linear-gradient(45deg, #4267B2, #898F9C) !important;
    border: none !important;
    color: white !important;
}

:deep(.platform-tag.el-tag--purple) {
    background: linear-gradient(45deg, #9146FF, #6441A4) !important;
    border: none !important;
    color: white !important;
}

/* 平台标签悬浮效果 */
:deep(.platform-tag.el-tag:hover) {
    transform: translateY(-2px) scale(1.05) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    filter: brightness(1.1) !important;
}

/* 平台标签点击效果 */
:deep(.platform-tag.el-tag:active) {
    transform: translateY(1px) scale(0.98) !important;
    filter: brightness(0.95) !important;
}

/* 暗黑模式适配 */
html.dark {
    :deep(.platform-tag.el-tag--danger) {
        background: linear-gradient(45deg, #CC0000, #CC4422) !important;
    }

    :deep(.platform-tag.el-tag--warning) {
        background: linear-gradient(45deg, #962A6C, #C42E5A, #C45E2C) !important;
    }

    :deep(.platform-tag.el-tag--success) {
        background: linear-gradient(45deg, #1EC3BE, #000000, #CB2344) !important;
    }

    :deep(.platform-tag.el-tag--info) {
        background: linear-gradient(45deg, #1780C2, #10131A) !important;
    }

    :deep(.platform-tag.el-tag--primary) {
        background: linear-gradient(45deg, #324C85, #6B7179) !important;
    }

    :deep(.platform-tag.el-tag--purple) {
        background: linear-gradient(45deg, #7438CC, #503483) !important;
    }

    :deep(.platform-tag.el-tag) {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }

    :deep(.platform-tag.el-tag:hover) {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
}

/* 平台图标和文本样式 */
.platform-icon {
    font-size: 18px !important;
    line-height: 1 !important;
}

.platform-text {
    font-size: 14px !important;
    letter-spacing: 0.5px !important;
    font-weight: 600 !important;
}
</style>
