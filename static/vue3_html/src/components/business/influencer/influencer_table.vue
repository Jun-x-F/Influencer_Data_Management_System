<script lang="ts" setup>
import {useInfluencerStore} from '@/store/useInfluencerStore';
import {computed, nextTick, onMounted, ref, watch} from 'vue';
import {parsePhoneNumberFromString} from 'libphonenumber-js';
import {Loading, Picture, Plus, Search} from '@element-plus/icons-vue'
import {ElMessage, ElMessageBox} from "element-plus";
import useClipboard from 'vue-clipboard3'
import addInfluencer from './addInfluencer.vue'
import updateInfluencer from './updateInfluencer.vue'
// @/components/common/icons
import EmailIcon from '@/components/common/icons/EmailIcon.vue'
import {useI18n} from 'vue-i18n'
import MapIcon from '@/components/common/icons/MapIcon.vue'
import WechatIcon from '@/components/common/icons/WechatIcon.vue'
import DiscordIcon from '@/components/common/icons/DiscordIcon.vue'
// 导入图片资源
// import mapLogo from '../src/assets/map_logo.png'
// import discordLogo from '../src/assets/discord.png'
// import chatLogo from '../src/assets/chat_logo.png'

// 获取i18n实例
const { t } = useI18n()

// 确保 videoData 是响应式的
const influencerStore = useInfluencerStore();
const toClipboard = useClipboard();
const searchKeyword = ref('');
const activeKeywords = ref<string[]>([])
const pageSize = ref(10);
const currentPage = ref(1);
const displayData = ref<any[]>([])
const isLoading = ref(false)
const isAdd = ref(false)
const updateDrawerVisible = ref(false)
const currentRow = ref({})

// 添加排序状态
const sortConfig = ref({
    prop: 'id',
    order: 'descending'
})

// 添加更新loading状态
const updateLoading = ref(false)

// 添加删除loading状态
const deleteLoading = ref(false)

// 添加状态保持相关的变量
const currentState = ref({
    keywords: [] as string[],
    currentData: [] as any[],
    scrollPosition: 0,
    searchTags: [] as string[]
});

// 异步初始化
onMounted(async () => {
    try {
        await influencerStore.getInfluencerList();
        // filteredTableData.value = influencerStore.influencerList; // 更新响应式数据
        await loadInitialData();
    } catch (error) {
        console.error('初始化失败', error);
    }
});

// 监听 influencerStore.isInfluencerLoading
watch(() => influencerStore.isInfluencerLoading, (newValue) => {
    isLoading.value = newValue;
});


const loadInitialData = async () => {
    // 如果有保存的状态，恢复它
    if (currentState.value.keywords.length > 0) {
        activeKeywords.value = [...currentState.value.keywords];
        const results = influencerStore.influencerList.filter((row: any) => {
            return currentState.value.keywords.every(keyword => {
                if (!keyword) return true;
                const searchText = keyword.toLowerCase();
                return ['红人名称', '平台', '标签', '地区'].some(field => {
                    const fieldValue = String(row[field] || '').toLowerCase();
                    return fieldValue.includes(searchText);
                });
            });
        });
        displayData.value = results;
    } else {
        displayData.value = filteredTableData.value.slice(0, pageSize.value);
    }

    // 恢复滚动位置
    nextTick(() => {
        const tableBody = document.querySelector('.el-table__body-wrapper');
        if (tableBody) {
            tableBody.scrollTop = currentState.value.scrollPosition;
        }
    });
}

// 定义列数据类型
interface Column {
    prop: string;
    label: string;
    width: string;
    sortable?: boolean;
    sortMethod?: (a: any, b: any) => number;
    filters?: any[];
    filterMethod?: (value: any, row: any, column: Column) => boolean;
    filteredValue?: any[];
    isLink?: boolean;
    merge?: boolean;
    isTag?: boolean;
    formatter?: (row: any, column: any) => string;
}

// 定义固定列
const fixedColumns: Column[] = [
    { prop: 'id', label: 'ID', width: '80px', sortable: true, merge: true },
    { prop: '红人头像地址', label: t('influencer.avatar'), width: '120px', merge: true, isLink: true },
    { prop: '红人名称', label: t('influencer.name'), width: '200px', isLink: true, merge: true },
    { prop: '平台', label: t('influencer.platform'), width: '160px', merge: true, isTag: true },
    { prop: '粉丝数量', label: t('influencer.fans'), width: '160px', merge: true, sortable: true, sortMethod: (a: any, b: any) => Number(a) - Number(b) },
    {
        prop: '平均播放量',
        label: t('influencer.avgViews'),
        width: '160px',
        merge: true,
        sortable: true,
        sortMethod: (a: any, b: any) => Number(a) - Number(b),
        formatter: (row: any, column: any) => Math.round(Number(row[column.property])).toString()
    },
    {
        prop: '平均点赞数量',
        label: t('influencer.avgLikes'),
        width: '160px',
        merge: true,
        sortable: true,
        sortMethod: (a: any, b: any) => Number(a) - Number(b),
        formatter: (row: any, column: any) => Math.round(Number(row[column.property])).toString()
    },
    {
        prop: '平均评论数量',
        label: t('influencer.avgComments'),
        width: '160px',
        merge: true,
        sortable: true,
        sortMethod: (a: any, b: any) => Number(a) - Number(b),
        formatter: (row: any, column: any) => Math.round(Number(row[column.property])).toString()
    },
    {
        prop: '平均参与率',
        label: t('influencer.engagementRate'),
        width: '160px',
        merge: true,
        sortable: true,
        sortMethod: (a: any, b: any) => {
            const valueA = typeof a === 'string' ? Number(a.replace('%', '')) : Number(a);
            const valueB = typeof b === 'string' ? Number(b.replace('%', '')) : Number(b);
            return valueA - valueB;
        },
        formatter: (row: any, column: any) => {
            const rawValue = row[column.property];
            const value = typeof rawValue === 'string' ?
                Number(rawValue.replace('%', '')) :
                Number(rawValue) * 100;
            return value.toFixed(2) + '%';
        }
    },
    { prop: '地区', label: t('influencer.region'), width: '100px', merge: true, isLink: true },
    { prop: '地址', label: t('influencer.address'), width: 'auto', merge: true },
    { prop: '联系方式', label: t('influencer.contact'), width: '200px', merge: true },
    { prop: '标签', label: t('influencer.tags'), width: '200px', merge: true, isTag: true },
    { prop: '评级', label: t('influencer.rating'), width: '80px', merge: true },
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
    // console.log("联系方式", links)
    return links ? links.split(',').map(link => link.trim()) : [];
};

const isDiscordLink = (url: string) => {
    return url.includes("discord.com");
};

const isEmailLink = (url: string) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(url);
};

// 定义接口
interface SortConfig {
    prop: string;
    order: 'ascending' | 'descending' | null;
}

interface PlatformType {
    [key: string]: string;
}

interface InfluencerData {
    id: number;
    红人名称: string;
    平台: string;
    红人主页地址: string;
    [key: string]: any;
}

// 获取平台对应的标签类型和样式
const getPlatformTagType = (platform: string): string => {
    const typeMap: PlatformType = {
        'youtube': 'danger',
        'instagram': 'warning',
        'tiktok': 'success',
        'x': 'info',
        'facebook': 'primary',
        'twitch': 'purple',
        'linkedin': 'info',
    }
    return typeMap[platform] || 'info'
}

// 获取平台对应的图标
const getPlatformIcon = (platform: string): string => {
    const iconMap: { [key: string]: string } = {
        'youtube': '📺',
        'instagram': '📷',
        'tiktok': '🎵',
        'x': '🐦',
        'facebook': '👥',
        'twitch': '🎮',
        'linkedin': '💼',
    }
    return iconMap[platform] || '🌐'
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

// 生成随机颜色
const getRandomColor = () => {
    const colors = [
        // '#FF8E8F', '#E178C5', '#FFB38E', '#FFFDCB', '#FFFF80',
        '#FFAA80', '#FF5580', '#FF0080', '#EB5B00', '#ff9800'
    ]
    return colors[Math.floor(Math.random() * colors.length)]
}

// 处理搜索关键词，允许空格存在
const processKeywords = (value: string): string[] => {
    return value
        .split(' ')
        .filter(keyword => keyword.length > 0)
        .map(keyword => keyword.toLowerCase())
}

// 高亮文本处理函数
const highlightText = (text: string, keywords: string[]) => {
    if (!keywords.length) return text

    let result = text
    const processedText = String(text).toLowerCase()
    const spans: { keyword: string; color: string }[] = []

    keywords.forEach(keyword => {
        if (keyword && processedText.includes(keyword.toLowerCase())) {
            spans.push({
                keyword: keyword,
                color: getRandomColor()
            })
        }
    })

    // 按关键词长度降序排序，避免短词替换长词的一部分
    spans.sort((a, b) => b.keyword.length - a.keyword.length)

    spans.forEach(({ keyword, color }) => {
        const regex = new RegExp(`(${keyword})`, 'gi')
        result = result.replace(regex, `<span class="highlight" style="color: ${color}">$1</span>`)
    })

    return result
}

// 修改过滤后的数据计算属性
const filteredTableData = computed(() => {
    let result = [...influencerStore.influencerList]

    // 先进行排序
    if (sortConfig.value.prop && sortConfig.value.order) {
        result.sort((a, b) => {
            const isAsc = sortConfig.value.order === 'ascending'
            if (typeof a[sortConfig.value.prop] === 'number') {
                return isAsc ? a[sortConfig.value.prop] - b[sortConfig.value.prop] : b[sortConfig.value.prop] - a[sortConfig.value.prop]
            }
            return isAsc ?
                String(a[sortConfig.value.prop]).localeCompare(String(b[sortConfig.value.prop])) :
                String(b[sortConfig.value.prop]).localeCompare(String(a[sortConfig.value.prop]))
        })
    }

    // 再进行关键词过滤
    if (activeKeywords.value.length === 0) {
        return result
    }

    return result.filter((item) => {
        const searchableFields = ['红人名称', '平台', '标签', '地区']
        const searchableValues = searchableFields
            .map(field => String(item[field] || '').toLowerCase())
            .join(' ')

        return activeKeywords.value.some(keyword => {
            const searchTerm = keyword.toLowerCase()
            return searchableValues.includes(searchTerm)
        })
    })
})

// 添加排序变化处理函数
const handleSortChange = ({ prop, order }: { prop: string; order: 'ascending' | 'descending' | null }) => {
    if (prop && order) {
        sortConfig.value = { prop, order }
        // 重置分页和显示数据
        currentPage.value = 1
        displayData.value = []
        loadInitialData()
    }
}

// 移除单个关键词
const removeKeyword = (keyword: string) => {
    activeKeywords.value = activeKeywords.value.filter(k => k !== keyword)
}

// 清空输入框时只清空输入框内容，不影响已保存的关键词
const handleInputClear = () => {
    searchKeyword.value = ''
}

// 搜索处理：按回车保存关键词
const handleSearch = () => {
    if (!searchKeyword.value.trim()) return

    const newKeywords = processKeywords(searchKeyword.value)

    // 过滤出不在当前活动关键词中的新关键词
    const uniqueNewKeywords = newKeywords.filter(
        keyword => !activeKeywords.value.includes(keyword)
    )

    if (uniqueNewKeywords.length > 0) {
        // 追加新的关键词
        activeKeywords.value = [...activeKeywords.value, ...uniqueNewKeywords]
    }

    // 清空输入框，方便继续输入新关键词
    searchKeyword.value = ''
}

// 监听筛选条件变化
watch(filteredTableData, () => {
    currentPage.value = 1
    loadInitialData()
}, { deep: true })

// 处理新增按钮点击
const handleTableAdd = () => {
    isAdd.value = true
}

// 监听抽屉关闭事件
const handleDrawerClose = () => {
    isAdd.value = false
}

// 加载更多数据
// 添加滚动
function handleTableScroll() {
    console.log('滚动分页')
    // 如果正在加载，直接返回
    if (isLoading.value) return

    isLoading.value = true
    try {
        const start = displayData.value.length
        const end = start + pageSize.value

        // 提前加载：当滚动到距离底部还有一定距离时就开始加载
        if (start >= filteredTableData.value.length) {
            isLoading.value = false
            return
        }

        // 追加新数据
        const newData = filteredTableData.value.slice(start, end)
        displayData.value = [...displayData.value, ...newData]
        currentPage.value++
    } finally {
        setTimeout(() => {
            isLoading.value = false
        }, 300) // 添加小延迟，避免加载过快
    }
}

const handleUpdate = (row: InfluencerData) => {
    currentRow.value = row
    updateDrawerVisible.value = true
}

const handleUpdateSubmit = async (formData: InfluencerData) => {
    // 保存当前状态
    currentState.value = {
        keywords: activeKeywords.value,
        currentData: [...displayData.value],
        scrollPosition: document.querySelector('.el-table__body-wrapper')?.scrollTop || 0,
        searchTags: [...activeKeywords.value]
    };

    updateLoading.value = true;
    try {
        await influencerStore.updateInfluencerInfo(formData);
        await influencerStore.getInfluencerList();

        // 恢复搜索状态
        if (currentState.value.keywords.length > 0) {
            activeKeywords.value = [...currentState.value.keywords];
            const results = influencerStore.influencerList.filter((row: any) => {
                return currentState.value.keywords.every(keyword => {
                    if (!keyword) return true;
                    const searchText = keyword.toLowerCase();
                    return ['红人名称', '平台', '标签', '地区'].some(field => {
                        const fieldValue = String(row[field] || '').toLowerCase();
                        return fieldValue.includes(searchText);
                    });
                });
            });
            displayData.value = results;
        } else {
            const currentLength = currentState.value.currentData.length;
            displayData.value = influencerStore.influencerList.slice(0, currentLength);
        }

        // 恢复滚动位置
        nextTick(() => {
            const tableBody = document.querySelector('.el-table__body-wrapper');
            if (tableBody) {
                tableBody.scrollTop = currentState.value.scrollPosition;
            }
        });

        ElMessage.success('更新成功');
    } catch (error: any) {
        console.error('Update failed:', error);
        ElMessage.error('更新失败：' + (error.message || '未知错误'));
    } finally {
        updateLoading.value = false;
    }
};

// 处理删除操作
const handleDelete = async (row: InfluencerData) => {
    try {
        // 保存当前状态
        currentState.value = {
            keywords: activeKeywords.value,
            currentData: [...displayData.value],
            scrollPosition: document.querySelector('.el-table__body-wrapper')?.scrollTop || 0,
            searchTags: [...activeKeywords.value]
        };

        await ElMessageBox.confirm(
            '此操作将永久删除该红人信息, 是否继续?',
            '警告',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
                draggable: true,
                closeOnClickModal: false,
                beforeClose: async (action, instance, done) => {
                    if (action === 'confirm') {
                        instance.confirmButtonLoading = true;
                        deleteLoading.value = true;
                        try {
                            await influencerStore.deleteInfluencerInfo({ id: row.id });
                            await influencerStore.getInfluencerList();

                            // 恢复搜索状态
                            if (currentState.value.keywords.length > 0) {
                                activeKeywords.value = [...currentState.value.keywords];
                                const results = influencerStore.influencerList.filter((row: any) => {
                                    return currentState.value.keywords.every(keyword => {
                                        if (!keyword) return true;
                                        const searchText = keyword.toLowerCase();
                                        return ['红人名称', '平台', '标签', '地区'].some(field => {
                                            const fieldValue = String(row[field] || '').toLowerCase();
                                            return fieldValue.includes(searchText);
                                        });
                                    });
                                });
                                displayData.value = results;
                            } else {
                                const currentLength = currentState.value.currentData.length;
                                displayData.value = influencerStore.influencerList.slice(0, currentLength);
                            }

                            // 恢复滚动位置
                            nextTick(() => {
                                const tableBody = document.querySelector('.el-table__body-wrapper');
                                if (tableBody) {
                                    tableBody.scrollTop = currentState.value.scrollPosition;
                                }
                            });

                            ElMessage.success('删除成功');
                            done();
                        } catch (error: any) {
                            ElMessage.error('删除失败：' + (error.message || '未知错误'));
                        } finally {
                            instance.confirmButtonLoading = false;
                            deleteLoading.value = false;
                        }
                    } else {
                        done();
                    }
                }
            }
        );
    } catch (error) {
        console.log('取消删除');
    }
};

// 修改电话号码验证函数
const validatePhoneNumber = (contact: string): boolean => {
    // 移除所有非数字字符
    const cleanNumber = contact.replace(/[^\d]/g, '');
    // 尝试解析清理后的号码
    try {
        const parsedNumber = parsePhoneNumberFromString('+' + cleanNumber);
        return parsedNumber?.isValid() || false;
    } catch {
        return false;
    }
}

// 添加联系方式排序函数
const sortContacts = (contacts: string[]): string[] => {
    if (!contacts || !Array.isArray(contacts)) return [];

    // 对联系方式进行分类
    const emailContacts = contacts.filter(link => isEmailLink(link));
    const phoneContacts = contacts.filter(link => validatePhoneNumber(link));
    const discordContacts = contacts.filter(link => isDiscordLink(link));
    const otherContacts = contacts.filter(link =>
        !isEmailLink(link) && !validatePhoneNumber(link) && !isDiscordLink(link)
    );

    // 按照指定顺序合并
    return [...emailContacts, ...phoneContacts, ...discordContacts, ...otherContacts];
};

// 在script setup中添加组件引用
const tableRef = ref();
</script>

<template>
    <div class="influencer-table table_color">
        <el-card class="influencer_card">
            <div class="table-header">
                <div class="search-area">
                    <el-tooltip :content="t('influencer.searchTip')" placement="top">
                        <el-input v-model="searchKeyword" :placeholder="t('influencer.searchPlaceholder')"
                            class="search-input" clearable @change="handleSearch" @clear="handleInputClear">
                            <template #prefix>
                                <el-icon>
                                    <Search />
                                </el-icon>
                            </template>
                        </el-input>
                    </el-tooltip>

                    <!-- 搜索关键词标签 -->
                    <div v-if="activeKeywords.length > 0" class="search-tips">
                        <span class="tips-label">{{ t('influencer.savedKeywords') }}：</span>
                        <el-tag v-for="keyword in activeKeywords" :key="keyword" class="keyword-tag" closable
                            size="small" @close="removeKeyword(keyword)">
                            {{ keyword }}
                        </el-tag>
                    </div>
                </div>

                <!-- 右侧新增按钮 -->
                <div class="button-area">
                    <el-button type="primary" @click="isAdd = true">
                        <el-icon>
                            <Plus />
                        </el-icon>
                        {{ t('influencer.add') }}
                    </el-button>
                </div>
            </div>

            <!-- 绑定新增弹窗 -->
            <addInfluencer :drawer="isAdd" @update:drawer="isAdd = $event" @close="handleDrawerClose" />

            <el-table ref="tableRef" :data="displayData" :loading="isLoading"
                :searchable-fields="['红人名称', '平台', '标签', '地区']" :default-sort="{ prop: 'id', order: 'descending' }"
                v-el-table-infinite-scroll="handleTableScroll" @search="handleSearch" @sort-change="handleSortChange"
                height="650" border>
                <template #buttons>
                    <el-button type="primary" @click="handleTableAdd">
                        <el-icon>
                            <Plus />
                        </el-icon>
                        {{ t('influencer.add') }}
                    </el-button>
                </template>
                <!-- 表格列定义 -->
                <el-table-column v-for="column in columns" :key="column.prop" :prop="column.prop" :label="column.label"
                    :width="column.width" :sortable="column.sortable" :filters="column.filters"
                    :filter-method="column.filterMethod" :filtered-value="column.filteredValue">
                    <!-- Custom Cell Content -->
                    <!-- Custom Cell Content for Image -->
                    <template v-if="column.isLink" #default="scope">
                        <el-image v-if="column.prop === '红人头像地址'" :src="scope.row[column.prop]" fit="cover"
                            :preview-src-list="[scope.row[column.prop]]" class="influencer-avatar" loading="lazy">
                            <template #error>
                                <div class="image-error">
                                    <el-icon>
                                        <Picture />
                                    </el-icon>
                                </div>
                            </template>
                            <template #placeholder>
                                <div class="image-placeholder">
                                    <el-icon>
                                        <Loading />
                                    </el-icon>
                                </div>
                            </template>
                        </el-image>
                        <a v-else-if="column.prop === '红人名称' && isValidURL(scope.row['红人主页地址'])"
                            :href="scope.row['红人主页地址']" target="_blank" rel="noopener noreferrer"
                            v-html="highlightText(scope.row[column.prop], activeKeywords)">
                        </a>
                        <!-- <span>{{ scope.row[column.prop] }}</span> -->
                    </template>
                    <!-- Custom Cell Content for Tags -->
                    <template v-else-if="column.prop === '标签' && column.isTag" #default="scope">
                        <el-row>
                            <div v-if="scope.row[column.prop]">
                                <el-col :span="30">
                                    <el-tag v-for="(tag, index) in processTags(scope.row[column.prop])" :key="index"
                                        :closable="false" class="contact_tag"
                                        v-html="highlightText(tag, activeKeywords)">
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
                                        <MapIcon class="contact_logo" :size="40" color="#409EFF" />
                                    </a>
                                </el-tooltip>
                            </el-col>
                        </el-row>
                    </template>
                    <template v-else-if="column.prop === '联系方式'" #default="scope">
                        <el-row class="contact-row">
                            <el-col v-for="(link, index) in sortContacts(splitLinks(scope.row['联系方式']))" :key="index"
                                :span="6" class="contact-col">
                                <el-tooltip :content="link" placement="bottom" effect="dark">
                                    <a href="#" @click="open(link)">
                                        <template v-if="isEmailLink(link)">
                                            <EmailIcon class="contact_logo" />
                                        </template>
                                        <template v-else-if="validatePhoneNumber(link)">
                                            <WechatIcon class="contact_logo" :size="40" />
                                        </template>
                                        <template v-else-if="isDiscordLink(link)">
                                            <DiscordIcon class="contact_logo" :size="40" />
                                        </template>
                                    </a>
                                </el-tooltip>
                            </el-col>
                        </el-row>
                    </template>
                    <!-- 平台标签显示 -->
                    <template v-else-if="column.prop === '平台'" #default="scope">
                        <a v-if="isValidURL(scope.row['红人主页地址'])" :href="scope.row['红人主页地址']" target="_blank"
                            rel="noopener noreferrer" class="platform-link">
                            <el-tag :type="getPlatformTagType(scope.row[column.prop])" effect="dark"
                                class="platform-tag">
                                <span class="platform-icon">{{ getPlatformIcon(scope.row[column.prop]) }}</span>
                                <span class="platform-text"
                                    v-html="highlightText(scope.row[column.prop], activeKeywords)"></span>
                            </el-tag>
                        </a>
                        <el-tag v-else :type="getPlatformTagType(scope.row[column.prop])" effect="dark"
                            class="platform-tag">
                            <span class="platform-icon">{{ getPlatformIcon(scope.row[column.prop]) }}</span>
                            <span class="platform-text"
                                v-html="highlightText(scope.row[column.prop], activeKeywords)"></span>
                        </el-tag>
                    </template>
                    <!-- Default Cell Content -->
                    <template v-else #default="scope">
                        <span v-if="['平均播放量', '平均点赞数量', '平均评论数量'].includes(column.prop)"
                            v-html="highlightText(Math.round(Number(scope.row[column.prop])).toString(), activeKeywords)">
                        </span>
                        <span v-else-if="column.prop === '平均参与率'" v-html="highlightText((() => {
                            const rawValue = scope.row[column.prop];
                            const value = typeof rawValue === 'string' ?
                                Number(rawValue.replace('%', '')) :
                                Number(rawValue) * 100;
                            return value.toFixed(2) + '%';
                        })(), activeKeywords)">
                        </span>
                        <span v-else v-html="highlightText(scope.row[column.prop], activeKeywords)"></span>
                    </template>

                </el-table-column>
                <el-table-column fixed="right" :label="t('influencer.operations')" min-width="150">
                    <template #default="scope">
                        <el-row :gutter="10">
                            <el-col :span="12">
                                <el-tooltip :content="t('influencer.update')" placement="top">
                                    <el-button type="primary" key="更新" size="small" @click="handleUpdate(scope.row)">
                                        {{ t('influencer.update') }}
                                    </el-button>
                                </el-tooltip>
                            </el-col>
                            <el-col :span="12">
                                <el-tooltip :content="t('influencer.delete')" placement="top">
                                    <el-button type="danger" key="删除" size="small" :loading="deleteLoading"
                                        @click="handleDelete(scope.row)">
                                        {{ t('influencer.delete') }}
                                    </el-button>
                                </el-tooltip>
                            </el-col>
                        </el-row>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
        <update-influencer v-model="updateDrawerVisible" :row-data="currentRow" :loading="updateLoading"
            @submit="handleUpdateSubmit" />
    </div>
</template>

<style scoped>
.influencer-table {
    width: 100%;
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

.table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 0 10px;
}

.search-area {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: 600px;
}

.search-input {
    width: 100%;
}

.button-area {
    margin-left: 16px;
}

/* 响应式布局 */
@media screen and (max-width: 768px) {
    .table-header {
        flex-direction: column;
        gap: 16px;
    }

    .search-area {
        max-width: none;
        width: 100%;
    }

    .button-area {
        margin-left: 0;
        width: 100%;
    }

    .button-area .el-button {
        width: 100%;
    }
}

/* 新增样式 */
.icon-center {
    display: flex;
    align-items: center;
    justify-content: center;
}

.button-center {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    /* 图标和文字之间的间距 */
}

/* 调整搜索框内部元素的垂直对齐 */
:deep(.el-input__prefix) {
    display: flex;
    align-items: center;
}

:deep(.el-input__inner) {
    line-height: 1.5;
    /* 调整输入框文字的行高 */
}

/* 调整按钮内部元素的垂直对齐 */
:deep(.el-button) {
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

:deep(.el-button .el-icon) {
    margin-right: 8px;
    /* 图标和文字之间的间距 */
}

.search-tips {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    padding: 4px 0;
}

.tips-label {
    color: #606266;
    font-size: 13px;
}

.keyword-tag {
    margin-right: 4px;
}

:deep(.el-tag) {
    margin: 2px;
}

:deep(.el-tag .el-tag__close) {
    color: #909399;
}

:deep(.el-tag .el-tag__close:hover) {
    color: #fff;
    background-color: #909399;
}

/* 高亮匹配文本 */
:deep(.highlight) {
    font-weight: bold;
    position: relative;
    display: inline-block;
    animation: glow 1.5s ease-in-out infinite alternate;
    transition: color 0.3s ease;
}

@keyframes glow {
    from {
        text-shadow: 0 0 2px rgba(255, 255, 255, 0.2),
            0 0 4px rgba(255, 255, 255, 0.2),
            0 0 6px rgba(255, 255, 255, 0.2);
    }

    to {
        text-shadow: 0 0 4px rgba(255, 255, 255, 0.4),
            0 0 8px rgba(255, 255, 255, 0.4),
            0 0 12px rgba(255, 255, 255, 0.4);
    }
}

/* 标签高亮样式 */
:deep(.el-tag .highlight) {
    display: inline-block;
    padding: 0 2px;
    border-radius: 2px;
}

/* 链接高亮样式 */
:deep(a .highlight) {
    text-decoration: underline;
}

/* 响应式布局 */
@media screen and (max-width: 768px) {
    .search-area {
        max-width: none;
        width: 100%;
    }

    .search-tips {
        flex-direction: column;
        align-items: flex-start;
    }
}

:deep(.el-table__body-wrapper) {
    overflow-y: auto;
    scroll-behavior: smooth;
}

:deep(.el-loading-mask) {
    background-color: rgba(255, 255, 255, 0.5);
}

.influencer_card {
    margin: 0 auto;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    background: #fff;
    transition: all 0.3s ease;

    /* 添加渐变边框效果 */
    /* background: linear-gradient(#fff, #fff) padding-box,
        linear-gradient(45deg, #409EFF, #67C23A) border-box;
    border: 1px solid transparent; */

    /* 添加悬浮效果 */
    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }

    /* 添加载入动画 */
    animation: cardFadeIn 0.5s ease-out;
}

/* 卡片载入动画 */
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

/* 添加内容过渡效果 */
.influencer_card :deep(.el-card__body) {
    transition: all 0.3s ease;
}

/* 优化表格内容显示 */
.influencer_card :deep(.el-table) {
    border-radius: 4px;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* 表格hover效果 */
.influencer_card :deep(.el-table__row) {
    transition: all 0.2s ease;

    &:hover {
        background-color: #f5f7fa;
        transform: scale(1.001);
    }
}

/* 优化加载状态显示 */
.influencer_card :deep(.el-loading-mask) {
    backdrop-filter: blur(2px);
    background-color: rgba(255, 255, 255, 0.8);
}

/* 表格头部样式优化 */
.influencer_card :deep(.el-table__header-wrapper) {
    th {
        background-color: #f5f7fa;
        font-weight: 600;
        color: #606266;
    }
}

/* 滚动条美化 */
.influencer_card :deep(.el-table__body-wrapper::-webkit-scrollbar) {
    width: 6px;
    height: 6px;
}

.influencer_card :deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
    border-radius: 3px;
    background-color: #dcdfe6;

    &:hover {
        background-color: #c0c4cc;
    }
}

.influencer_card :deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
    background-color: #f5f7fa;
}

/* 暗黑模式样式 */
html.dark {
    .influencer_card {
        background: #1f1f1f;
        border-color: #363636;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

        /* 暗色渐变边框 */
        background: linear-gradient(#1f1f1f, #1f1f1f) padding-box,
            linear-gradient(45deg, #409EFF, #67C23A) border-box;
    }

    /* 表格行hover效果 - 暗色模式 */
    .influencer_card :deep(.el-table__row) {
        &:hover {
            background-color: #363636 !important;
        }
    }

    /* 表格背景 - 暗色模式 */
    .influencer_card :deep(.el-table) {
        background-color: #1f1f1f;
        color: #ffffff;

        /* 表格单元格 */
        td.el-table__cell {
            background-color: #1f1f1f;
            border-bottom: 1px solid #363636;
        }

        /* 表头 */
        th.el-table__cell {
            background-color: #2c2c2c !important;
            border-bottom: 1px solid #363636;
            color: #ffffff;
        }
    }

    /* 加载遮罩 - 暗色模式 */
    .influencer_card :deep(.el-loading-mask) {
        backdrop-filter: blur(2px);
        background-color: rgba(0, 0, 0, 0.8);
    }

    /* 滚动条 - 暗色模式 */
    .influencer_card :deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
        background-color: #4a4a4a;

        &:hover {
            background-color: #5c5c5c;
        }
    }

    .influencer_card :deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
        background-color: #2c2c2c;
    }

    /* 斑马纹 - 暗色模式 */
    .influencer_card :deep(.el-table__row--striped) {
        td.el-table__cell {
            background-color: #2c2c2c;
        }
    }

    /* 表格边框 - 暗色模式 */
    .influencer_card :deep(.el-table--border) {
        border: 1px solid #363636;

        &::after,
        &::before {
            background-color: #363636;
        }
    }

    /* 空数据 - 暗色模式 */
    .influencer_card :deep(.el-table__empty-block) {
        background-color: #1f1f1f;

        .el-table__empty-text {
            color: #909399;
        }
    }

    /* 固定列阴影 - 暗色模式 */
    .influencer_card :deep(.el-table__fixed-right::before),
    .influencer_card :deep(.el-table__fixed::before) {
        background-color: #363636;
    }

    /* 排序图标 - 暗色模式 */
    .influencer_card :deep(.el-table__column-sort) {
        color: #409EFF;
    }

    /* 高亮文本 - 暗色模式 */
    :deep(.highlight) {
        color: #409EFF;
        text-shadow: 0 0 8px rgba(64, 158, 255, 0.4);
    }
}

/* 添加删除按钮的过渡效果 */
.el-button--danger {
    transition: all 0.3s ease;
}

.el-button--danger:hover {
    transform: scale(1.05);
}

/* 红人头像样式 */
.influencer-avatar {
    width: 80px;
    height: 80px;
    border-radius: 8px;
    object-fit: cover;
    transition: transform 0.3s ease;
    cursor: pointer;
}

.influencer-avatar:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 图片加载错误和占位符样式 */
.image-error,
.image-placeholder {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f7fa;
    border-radius: 8px;
}

.image-error .el-icon,
.image-placeholder .el-icon {
    font-size: 24px;
    color: #909399;
}

/* 平台链接样式 */
.platform-link {
    text-decoration: none;
    display: inline-block;
}

/* 平台标签基础样式 */
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

/* 平台特定样式 */
:deep(.el-tag.el-tag--danger) {
    background: linear-gradient(45deg, #FF0000, #FF4444) !important;
    border: none !important;
    color: white !important;
}

:deep(.el-tag.el-tag--warning) {
    background: linear-gradient(45deg, #C13584, #E1306C, #F77737) !important;
    border: none !important;
    color: white !important;
}

:deep(.el-tag.el-tag--success) {
    background: linear-gradient(45deg, #25F4EE, #000000, #FE2C55) !important;
    border: none !important;
    color: white !important;
}

:deep(.el-tag.el-tag--info) {
    background: linear-gradient(45deg, #1DA1F2, #14171A) !important;
    border: none !important;
    color: white !important;
}

:deep(.el-tag.el-tag--primary) {
    background: linear-gradient(45deg, #4267B2, #898F9C) !important;
    border: none !important;
    color: white !important;
}

:deep(.el-tag.el-tag--purple) {
    background: linear-gradient(45deg, #9146FF, #6441A4) !important;
    border: none !important;
    color: white !important;
}

/* 悬浮效果 */
.platform-tag:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    filter: brightness(1.1);
}

/* 点击效果 */
.platform-tag:active {
    transform: translateY(1px) scale(0.98);
    filter: brightness(0.95);
}

/* 暗黑模式适配 */
html.dark {
    :deep(.el-tag.el-tag--danger) {
        background: linear-gradient(45deg, #CC0000, #CC4422) !important;
    }

    :deep(.el-tag.el-tag--warning) {
        background: linear-gradient(45deg, #962A6C, #C42E5A, #C45E2C) !important;
    }

    :deep(.el-tag.el-tag--success) {
        background: linear-gradient(45deg, #1EC3BE, #000000, #CB2344) !important;
    }

    :deep(.el-tag.el-tag--info) {
        background: linear-gradient(45deg, #1780C2, #10131A) !important;
    }

    :deep(.el-tag.el-tag--primary) {
        background: linear-gradient(45deg, #324C85, #6B7179) !important;
    }

    :deep(.el-tag.el-tag--purple) {
        background: linear-gradient(45deg, #7438CC, #503483) !important;
    }

    .platform-tag {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .platform-tag:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
}

/* 图标样式 */
.platform-icon {
    font-size: 18px;
    line-height: 1;
}

/* 文本样式 */
.platform-text {
    font-size: 14px;
    letter-spacing: 0.5px;
    font-weight: 600;
}

/* 高亮文本样式 */
.platform-tag :deep(.highlight) {
    color: inherit;
    font-weight: 800;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
    animation: highlightGlow 1.5s ease-in-out infinite alternate;
}

@keyframes highlightGlow {
    from {
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.6);
    }

    to {
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
    }
}
</style>
