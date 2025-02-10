<template>
    <el-dialog v-model="visible" :title="$t('metrics.title')" width="60%" :destroy-on-close="true">
        <div class="metrics-container">
            <!-- 搜索区域 -->
            <div class="search-area">
                <div class="search-header">
                    <el-select v-model="searchTags" multiple filterable allow-create default-first-option
                        :reserve-keyword="false" :placeholder="$t('metrics.searchPlaceholder')" class="search-input"
                        @change="handleSearchChange" :no-data-text="$t('common.noData')" :remote-method="() => { }">
                        <template #prefix>
                            <el-icon>
                                <Search />
                            </el-icon>
                        </template>
                    </el-select>
                    <el-button type="primary" @click="showAddDialog">
                        {{ $t('metrics.add') }}
                    </el-button>
                </div>
            </div>

            <!-- 表格区域 -->
            <el-table :data="filteredMetrics" height="400" border style="width: 100%" v-loading="loading">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="品牌" :label="$t('metrics.brand')" />
                <el-table-column prop="项目" :label="$t('metrics.project')" />
                <el-table-column prop="产品" :label="$t('metrics.product')" />

                <!-- 操作列 -->
                <el-table-column fixed="right" :label="$t('influencer.operations')" width="150">
                    <template #default="scope">
                        <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                            {{ $t('metrics.update') }}
                        </el-button>
                        <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                            {{ $t('metrics.delete') }}
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </el-dialog>

    <!-- 编辑指标的抽屉 -->
    <el-drawer v-if="editDrawerVisible" v-model="editDrawerVisible" :title="$t('metrics.editTitle')" direction="rtl"
        size="30%">
        <el-form ref="editFormRef" :model="editForm" label-width="80px" class="edit-form">
            <el-form-item :label="$t('metrics.brand')" prop="品牌">
                <el-input v-model="editForm.品牌" />
            </el-form-item>
            <el-form-item :label="$t('metrics.project')" prop="项目">
                <el-input v-model="editForm.项目" />
            </el-form-item>
            <el-form-item :label="$t('metrics.product')" prop="产品">
                <el-input v-model="editForm.产品" />
            </el-form-item>
            <div class="form-actions">
                <el-button type="primary" @click="submitEdit">{{ $t('common.submit') }}</el-button>
                <el-button @click="editDrawerVisible = false">{{ $t('common.cancel') }}</el-button>
            </div>
        </el-form>
    </el-drawer>

    <!-- 密码验证对话框 -->
    <el-dialog v-model="passwordDialogVisible" :title="$t('metrics.verifyPassword')" width="30%" append-to-body>
        <el-form :model="passwordForm">
            <el-form-item :label="$t('metrics.password')">
                <el-input v-model="passwordForm.password" type="password" show-password />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="passwordDialogVisible = false">{{ $t('common.cancel') }}</el-button>
                <el-button type="primary" @click="verifyPassword">{{ $t('common.confirm') }}</el-button>
            </span>
        </template>
    </el-dialog>

    <!-- 新增指标的抽屉 -->
    <el-drawer v-if="addDrawerVisible" v-model="addDrawerVisible" :title="$t('metrics.addTitle')" direction="rtl"
        size="30%">
        <el-form ref="addFormRef" :model="addForm" label-width="80px" class="edit-form">
            <el-form-item :label="$t('metrics.brand')" prop="品牌">
                <el-input v-model="addForm.品牌" />
            </el-form-item>
            <el-form-item :label="$t('metrics.project')" prop="项目">
                <el-input v-model="addForm.项目" />
            </el-form-item>
            <el-form-item :label="$t('metrics.product')" prop="产品">
                <el-input v-model="addForm.产品" />
            </el-form-item>
            <div class="form-actions">
                <el-button type="primary" @click="submitAdd">{{ $t('common.submit') }}</el-button>
                <el-button @click="addDrawerVisible = false">{{ $t('common.cancel') }}</el-button>
            </div>
        </el-form>
    </el-drawer>
</template>

<script setup lang="ts">
import {computed, defineEmits, defineProps, onMounted, ref, watch} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Search} from '@element-plus/icons-vue'
import {useInfluencerStore} from '@/store/useInfluencerStore'
import {useI18n} from 'vue-i18n'

const STORAGE_KEY = 'metrics_password_verified'
const PASSWORD = '1234'

const props = defineProps({
    modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const influencerStore = useInfluencerStore()
const visible = ref(props.modelValue)
const loading = ref(false)
const searchTags = ref<string[]>([])
const confirmedTags = ref<string[]>([])
const editDrawerVisible = ref(false)
const passwordDialogVisible = ref(false)
const addDrawerVisible = ref(false)
const editForm = ref({
    id: '',
    品牌: '',
    项目: '',
    产品: ''
})
const passwordForm = ref({
    password: ''
})
const addForm = ref({
    品牌: '',
    项目: '',
    产品: ''
})

const { t } = useI18n()

// 监听visible变化
watch(() => props.modelValue, (val) => {
    visible.value = val
})

watch(visible, (val) => {
    emit('update:modelValue', val)
    if (val) {
        loadMetrics()
    }
})

// 加载指标数据
const loadMetrics = async () => {
    try {
        loading.value = true
        await influencerStore.getProjectDefinitions()
        console.log(influencerStore.projectDefinitionsNoFomat)
    } catch (error) {
        console.error('Failed to load metrics:', error)
        ElMessage.error(t('metrics.loadFailed'))
    } finally {
        loading.value = false
    }
}

// 更新过滤后的数据
const updateFilteredMetrics = (tags: string[]) => {
    if (!tags.length) {
        return influencerStore.projectDefinitionsNoFomat
    }
    return influencerStore.projectDefinitionsNoFomat.filter(item => {
        return tags.every(tag => {
            const lowercaseTag = tag.toLowerCase()
            return (
                item.品牌?.toLowerCase().includes(lowercaseTag) ||
                item.项目?.toLowerCase().includes(lowercaseTag) ||
                item.产品?.toLowerCase().includes(lowercaseTag)
            )
        })
    })
}

// 处理搜索变化
const handleSearchChange = () => {
    confirmedTags.value = [...searchTags.value]
}

// 过滤后的指标数据
const filteredMetrics = computed(() => {
    if (!confirmedTags.value.length) {
        return influencerStore.projectDefinitionsNoFomat
    }
    return updateFilteredMetrics(confirmedTags.value)
})

// 组件卸载时清除防抖函数
onMounted(() => {
    // 检查本地存储中的验证状态是否过期（可选：设置24小时过期）
    const lastVerifiedTime = localStorage.getItem(STORAGE_KEY + '_time')
    if (lastVerifiedTime) {
        const now = new Date().getTime()
        const expired = now - parseInt(lastVerifiedTime) > 24 * 60 * 60 * 1000 // 24小时过期
        if (expired) {
            localStorage.removeItem(STORAGE_KEY)
            localStorage.removeItem(STORAGE_KEY + '_time')
        }
    }

    return () => {
        if (debouncedSearch.value) {
            debouncedSearch.value.cancel()
        }
    }
})

// 处理编辑
const handleEdit = (row: any) => {
    editForm.value = { ...row }
    editDrawerVisible.value = true
}

// 处理删除
const handleDelete = async (row: any) => {
    try {
        await ElMessageBox.confirm(
            t('metrics.confirmDelete'),
            t('influencer.delete'),
            {
                confirmButtonText: t('common.submit'),
                cancelButtonText: t('common.cancel'),
                type: 'warning',
            }
        )

        loading.value = true
        await influencerStore.deleteProjectDefinition(row.id)
        ElMessage.success(t('metrics.deleteSuccess'))
        await loadMetrics()
    } catch (error) {
        if (error !== 'cancel') {
            console.error('Failed to delete metric:', error)
            ElMessage.error(t('metrics.deleteFailed'))
        }
    } finally {
        loading.value = false
    }
}

// 提交编辑
const submitEdit = async () => {
    try {
        loading.value = true
        await influencerStore.updateProjectDefinition(editForm.value)
        ElMessage.success(t('metrics.updateSuccess'))
        editDrawerVisible.value = false
        await loadMetrics()
    } catch (error) {
        console.error('Failed to update metric:', error)
        ElMessage.error(t('metrics.updateFailed'))
    } finally {
        loading.value = false
    }
}

// 显示密码验证对话框
const showAddDialog = () => {
    // 检查本地存储中的验证状态
    const isVerified = localStorage.getItem(STORAGE_KEY) === 'true'
    if (isVerified) {
        addDrawerVisible.value = true
        addForm.value = {
            品牌: '',
            项目: '',
            产品: ''
        }
    } else {
        passwordDialogVisible.value = true
        passwordForm.value.password = ''
    }
}

// 验证密码
const verifyPassword = () => {
    if (passwordForm.value.password === PASSWORD) {
        // 保存验证状态到本地存储
        localStorage.setItem(STORAGE_KEY, 'true')
        // 保存验证时间
        localStorage.setItem(STORAGE_KEY + '_time', new Date().getTime().toString())
        passwordDialogVisible.value = false
        addDrawerVisible.value = true
        addForm.value = {
            品牌: '',
            项目: '',
            产品: ''
        }
    } else {
        ElMessage.error(t('metrics.wrongPassword'))
    }
}

// 提交新增
const submitAdd = async () => {
    try {
        loading.value = true
        await influencerStore.addProjectDefinition(addForm.value)
        ElMessage.success(t('metrics.addSuccess'))
        addDrawerVisible.value = false
        await loadMetrics()
    } catch (error) {
        console.error('Failed to add metric:', error)
        ElMessage.error(t('metrics.addFailed'))
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.metrics-container {
    padding: 20px;
}

.search-area {
    margin-bottom: 20px;
}

.search-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.search-input {
    width: 100%;
}

.search-input :deep(.el-select__tags) {
    flex-wrap: wrap;
    max-height: 80px;
    overflow-y: auto;
}

.search-input :deep(.el-select__input) {
    margin: 0;
}

.edit-form {
    padding: 20px;
}

.form-actions {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

:deep(.el-dialog__body) {
    padding: 0;
}

/* 暗黑模式适配 */
html.dark {
    .metrics-container {
        background-color: var(--el-bg-color);
    }
}
</style>