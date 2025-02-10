<template>
    <el-drawer v-model="drawerVisible" :title="t('video.addVideo')" :size="800" :destroy-on-close="true" direction="rtl"
        @close="handleClose" class="custom-drawer">
        <template #header>
            <div class="drawer-header">
                <h3>{{ t('video.addVideo') }}</h3>
                <div class="header-actions">
                    <el-popover placement="bottom" :width="300" trigger="click" popper-class="guide-popover">
                        <template #reference>
                            <el-button type="primary" text>
                                <el-icon>
                                    <QuestionFilled />
                                </el-icon>
                                {{ t('common.guide') }}
                            </el-button>
                        </template>
                        <div class="guide-content">
                            <h4>{{ t('guide.title') }}</h4>
                            <ol class="guide-steps">
                                <li>{{ t('guide.step1') }}</li>
                                <li>{{ t('guide.step2') }}</li>
                                <li>{{ t('guide.step3') }}</li>
                            </ol>
                        </div>
                    </el-popover>
                </div>
            </div>
        </template>

        <div class="add-video-form">
            <el-form ref="formRef" :model="formData" label-width="120px" :rules="rules">
                <!-- 红人名称 -->
                <el-form-item :label="t('video.influencerName')" prop="红人名称" class="slide-in">
                    <el-autocomplete v-model="formData.红人名称" :fetch-suggestions="handleInfluencerSearch"
                        :placeholder="t('video.influencerName')" :trigger-on-focus="true" clearable class="wide-select"
                        @select="(item) => formData.红人名称 = item.value">
                        <template #default="{ item }">
                            <div class="suggestion-item">
                                {{ item.value }}
                            </div>
                        </template>
                    </el-autocomplete>
                </el-form-item>

                <!-- 负责人 -->
                <el-form-item :label="t('video.responsible')" prop="负责人" class="slide-in">
                    <div class="manager-select">
                        <el-select v-model="formData.负责人" :placeholder="t('video.selectResponsible')"
                            style="width: 300px">
                            <el-option v-for="manager in influencerStore.managerList" :key="manager" :label="manager"
                                :value="manager" />
                        </el-select>
                        <el-button type="primary" @click="showAddManager">
                            {{ t('video.addManager') }}
                        </el-button>
                    </div>
                </el-form-item>

                <!-- 使用新的负责人添加组件 -->
                <add-manager v-model="addManagerVisible" @success="handleAddManagerSuccess" />

                <!-- 产品信息 -->
                <el-form-item :label="t('video.product')" prop="products" class="slide-in full-width">
                    <el-cascader v-model="selectedProducts" :options="productOptions" :props="{
                        multiple: true,
                        checkStrictly: false,
                        label: 'label',
                        value: 'value',
                        children: 'children'
                    }" :show-all-levels="true" collapse-tags collapse-tags-tooltip clearable filterable
                        :loading="loading" :placeholder="t('video.selectProduct')" @change="handleProductChange">
                        <template #default="{ node, data }">
                            <span>{{ data.label }}</span>
                            <span v-if="data.count" style="margin-left: 4px">({{ data.count }})</span>
                        </template>
                    </el-cascader>
                </el-form-item>

                <!-- 视频链接 -->
                <el-form-item :label="t('video.videoLink')" prop="视频链接">
                    <el-input v-model="formData.视频链接" :placeholder="t('video.videoLinkPlaceholder')"
                        @input="handleVideoLinkChange" :validate-event="false" />
                </el-form-item>

                <!-- 合作进度 -->
                <el-form-item :label="t('video.cooperationStatus')" prop="合作进度" class="slide-in full-width">
                    <el-select v-model="formData.合作进度" class="wide-select">
                        <el-option :label="t('video.cooperationFinished')" value="合作完成">
                            <el-icon class="status-icon">
                                <CircleCheckFilled />
                            </el-icon>
                            {{ t('video.cooperationFinished') }}
                        </el-option>
                        <el-option :label="t('video.cooperationInProgress')" value="进行中">
                            <el-icon class="status-icon">
                                <Loading />
                            </el-icon>
                            {{ t('video.cooperationInProgress') }}
                        </el-option>
                        <el-option :label="t('video.cooperationCancelled')" value="合作取消">
                            <el-icon class="status-icon">
                                <CircleCloseFilled />
                            </el-icon>
                            {{ t('video.cooperationCancelled') }}
                        </el-option>
                    </el-select>
                    <div class="form-item-extra" role="note">{{ t('video.cooperationDefaultStatus') }}</div>
                </el-form-item>

                <!-- 币种和花费放在一起 -->
                <div class="form-row">
                    <!-- 币种 -->
                    <el-form-item :label="t('video.currency')" prop="币种" class="slide-in half-width">
                        <el-select v-model="formData.币种" placeholder="请选择币种" class="wide-select"
                            :popper-class="isDark ? 'dark-select' : ''">
                            <el-option label="USD - 美元" value="USD">
                                <span class="currency-option">
                                    <span class="currency-symbol">$</span>
                                    <span>USD - 美元</span>
                                </span>
                            </el-option>
                            <el-option label="CNY - 人民币" value="CNY">
                                <span class="currency-option">
                                    <span class="currency-symbol">¥</span>
                                    <span>CNY - 人民币</span>
                                </span>
                            </el-option>
                            <el-option label="EUR - 欧元" value="EUR">
                                <span class="currency-option">
                                    <span class="currency-symbol">€</span>
                                    <span>EUR - 欧元</span>
                                </span>
                            </el-option>
                            <el-option label="GBP - 英镑" value="GBP">
                                <span class="currency-option">
                                    <span class="currency-symbol">£</span>
                                    <span>GBP - 英镑</span>
                                </span>
                            </el-option>
                            <el-option label="JPY - 日元" value="JPY">
                                <span class="currency-option">
                                    <span class="currency-symbol">¥</span>
                                    <span>JPY - 日元</span>
                                </span>
                            </el-option>
                            <el-option label="AUD - 澳元" value="AUD">
                                <span class="currency-option">
                                    <span class="currency-symbol">A$</span>
                                    <span>AUD - 澳元</span>
                                </span>
                            </el-option>
                            <el-option label="CAD - 加元" value="CAD">
                                <span class="currency-option">
                                    <span class="currency-symbol">C$</span>
                                    <span>CAD - 加元</span>
                                </span>
                            </el-option>
                            <el-option label="CHF - 瑞士法郎" value="CHF">
                                <span class="currency-option">
                                    <span class="currency-symbol">Fr</span>
                                    <span>CHF - 瑞士法郎</span>
                                </span>
                            </el-option>
                            <el-option label="HKD - 港币" value="HKD">
                                <span class="currency-option">
                                    <span class="currency-symbol">HK$</span>
                                    <span>HKD - 港币</span>
                                </span>
                            </el-option>
                            <el-option label="NZD - 新西兰元" value="NZD">
                                <span class="currency-option">
                                    <span class="currency-symbol">NZ$</span>
                                    <span>NZD - 新西兰元</span>
                                </span>
                            </el-option>
                            <el-option label="SGD - 新加坡元" value="SGD">
                                <span class="currency-option">
                                    <span class="currency-symbol">S$</span>
                                    <span>SGD - 新加坡元</span>
                                </span>
                            </el-option>
                            <el-option label="KRW - 韩元" value="KRW">
                                <span class="currency-option">
                                    <span class="currency-symbol">₩</span>
                                    <span>KRW - 韩元</span>
                                </span>
                            </el-option>
                        </el-select>
                    </el-form-item>

                    <!-- 花费 -->
                    <el-form-item :label="t('video.cost')" prop="花费" class="slide-in half-width">
                        <el-input-number v-model="formData.花费" :min="0" :precision="2" :step="100" :controls="false"
                            placeholder="请输入花费金额" class="custom-number-input" />
                    </el-form-item>
                </div>

                <!-- 预估上线时间和观看量放在一起 -->
                <div class="form-row">
                    <!-- 预估上线时间 -->
                    <el-form-item :label="t('video.estimatedOnlineTime')" prop="预估上线时间" class="slide-in half-width">
                        <el-date-picker v-model="formData.预估上线时间" type="datetime"
                            :placeholder="t('video.estimatedOnlineTime')" class="wide-select" />
                    </el-form-item>

                    <!-- 预估观看量 -->
                    <el-form-item :label="t('video.estimatedViews')" prop="预估观看量" class="slide-in half-width">
                        <el-input-number v-model="formData.预估观看量" :min="0" :step="1000"
                            :placeholder="t('video.estimatedViews')" class="wide-select" />
                    </el-form-item>
                </div>

                <!-- 物流链接 -->
                <el-form-item :label="t('video.logisticsLink')" prop="物流链接" class="slide-in">
                    <el-input v-model="formData.物流链接" :placeholder="t('video.logisticsLink')"
                        @input="handleLogisticsLinkChange" />
                </el-form-item>

                <!-- 物流进度 -->
                <el-form-item :label="t('video.logisticsStatus')" prop="物流进度" class="slide-in full-width">
                    <el-select v-model="formData.物流进度" class="wide-select" :disabled="isLogisticsStatusDisabled">
                        <el-option :label="t('video.logisticsReceived')" value="成功签收">
                            <el-icon class="status-icon">
                                <CircleCheckFilled />
                            </el-icon>
                            {{ t('video.logisticsReceived') }}
                        </el-option>
                        <el-option :label="t('video.logisticsWaiting')" value="等待获取物流状态">
                            <el-icon class="status-icon">
                                <Loading />
                            </el-icon>
                            {{ t('video.logisticsWaiting') }}
                        </el-option>
                    </el-select>
                    <div class="form-item-extra" role="note">{{ t('video.defaultStatus') }}</div>
                </el-form-item>
            </el-form>
        </div>

        <template #footer>
            <div class="drawer-footer">
                <div class="footer-tips">
                    <el-alert :title="t('guide.tips')" type="info" :closable="false" show-icon />
                </div>
                <div class="footer-buttons">
                    <el-button type="primary" @click="submitForm(formRef)" :loading="submitting">
                        <el-icon>
                            <Check />
                        </el-icon>
                        {{ t('common.submit') }}
                    </el-button>
                    <el-button @click="resetForm()" class="reset-btn">
                        <el-icon>
                            <Refresh />
                        </el-icon>
                        {{ t('common.reset') }}
                    </el-button>
                </div>
            </div>
        </template>
    </el-drawer>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, reactive, ref} from 'vue'
import {useInfluencerStore} from '@/store/useInfluencerStore'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'
import {useI18n} from 'vue-i18n'
import {useDark} from '@vueuse/core'
import {Check, CircleCheckFilled, CircleCloseFilled, Loading, QuestionFilled, Refresh} from '@element-plus/icons-vue'
import {debounce} from 'lodash-es'
import AddManager from '@/components/business/manager/addManager.vue'

const { t } = useI18n()
const influencerStore = useInfluencerStore()
const isDark = useDark()

// 定义接口
interface InfluencerOption {
    value: string;
}

// Props 类型定义
const props = defineProps<{
    modelValue: boolean;
}>()

// 定义 emits
const emit = defineEmits(['update:modelValue', 'close', 'update-success'])

// 抽屉显示状态
const drawerVisible = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
})

// 处理关闭事件
const handleClose = async () => {
    try {
        drawerVisible.value = false
        emit('close')
        emit('update-success')
        resetForm()
        cleanupResources()
    } catch (error) {
        console.error('Error in handleClose:', error)
        ElMessage.error('关闭抽屉时发生错误')
    }
}

const formRef = ref<FormInstance>()
const formData = reactive({
    红人名称: '',
    负责人: '',
    币种: '',
    花费: null,
    物流链接: '',
    视频链接: '',
    预估上线时间: '',
    预估观看量: null,
    合作进度: '进行中',  // 默认为进行中
    物流进度: '成功签收'  // 默认为成功签收
})

// 验证URL的函数
const validateUrl = (rule: any, value: string, callback: any) => {
    // 如果为空，直接通过验证
    if (!value) {
        callback()
        return
    }

    try {
        const url = new URL(value)
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
            callback(new Error(t('video.invalidVideoLink')))
            return
        }

        const excludedSubstrings = [
            '/reel/', '/video/', '/watch/',
            '/video?', '/watch?', '/reel?',
            '/p/', '/p?', '/shorts/', '/shorts?'
        ]

        // 获取完整的URL路径（包括pathname和search）
        const fullPath = url.pathname + url.search

        // 检查是否包含任何一个有效的视频路径
        const isValidVideoUrl = excludedSubstrings.some(substr => {
            // 移除查询参数中的问号进行比较
            const cleanSubstr = substr.replace('?', '')
            return fullPath.includes(cleanSubstr)
        })

        if (!isValidVideoUrl) {
            ElMessage({
                message: t('video.invalidVideoFormat'),
                type: 'error',
                duration: 5000,
                showClose: true
            })
            callback(new Error(t('video.invalidVideoFormat')))
            return
        }

        callback()
    } catch (err) {
        callback(new Error(t('video.invalidVideoLink')))
    }
}

// 定义表单校验规则
const rules = reactive<FormRules>({
    红人名称: [{ required: true, message: t('video.influencerName'), trigger: 'blur' }],
    负责人: [{ required: true, message: t('video.responsible'), trigger: 'blur' }],
    视频链接: [{ validator: validateUrl, trigger: ['blur', 'submit'] }]
})

// 产品相关
const loading = ref(false)
const productOptions = ref([])
const selectedProducts = ref([])

// 红人名称搜索相关
const influencerOptions = computed((): InfluencerOption[] => {
    const nameSet = new Set<string>()
    const options: InfluencerOption[] = []

    influencerStore.videoList.forEach((item: { 红人名称?: string; 红人全称?: string }) => {
        const name = item.红人名称 || item.红人全称
        if (name && !nameSet.has(name)) {
            nameSet.add(name)
            options.push({ value: name })
        }
    })
    return options
})

const filteredInfluencers = ref<InfluencerOption[]>([])

// 使用防抖处理搜索
const handleInfluencerSearch = debounce((query: string, cb: (arg: InfluencerOption[]) => void) => {
    if (query) {
        const results = influencerOptions.value
            .filter(item => item.value.toLowerCase().includes(query.toLowerCase()))
        cb(results)
    } else {
        cb([])
    }
}, 300)

// 初始化数据
onMounted(async () => {
    try {
        loading.value = true
        await Promise.all([
            influencerStore.getProjectDefinitions(),
            influencerStore.getManagerList(),
            influencerStore.getVideoList()
        ])
        productOptions.value = influencerStore.projectDefinitions
    } catch (error) {
        console.error('初始化数据失败:', error)
        ElMessage.error('加载数据失败')
    } finally {
        loading.value = false
    }
})

// 处理产品选择变化
const handleProductChange = (value) => {
    selectedProducts.value = value
}

// 监听视频链接变化
const handleVideoLinkChange = (value: string) => {
    if (value && formData.合作进度 === '进行中') {
        formData.合作进度 = '合作完成'
    }
}

// 验证17track链接
const validate17TrackUrl = (value: string): boolean => {
    return value.includes('17track.net');
}

// 监听物流链接变化
const handleLogisticsLinkChange = (value: string) => {
    if (value && !validate17TrackUrl(value)) {
        ElMessage.warning(t('video.invalidLogisticsLink'));
        formData.物流链接 = '';
        return;
    }
    formData.物流进度 = value ? '等待获取物流状态' : '成功签收';
}

// 计算属性：控制物流进度是否禁用
const isLogisticsStatusDisabled = computed(() => {
    return !formData.物流链接
})

// 提交状态
const submitting = ref(false)

// 修改提交表单函数
const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate(async (valid, fields) => {
        if (valid) {
            try {
                submitting.value = true
                const formattedData = {
                    ...formData,
                    products: selectedProducts.value.map(path => ({
                        品牌: path[0],
                        项目: path[1],
                        产品: path[2]
                    }))
                }
                await influencerStore.addVideo(formattedData)
                ElMessage.success(t('message.addSuccess'))
                handleClose()
            } catch (error: any) {
                ElMessage.error(t('message.addFailed') + ': ' + error.message)
            } finally {
                submitting.value = false
            }
        }
    })
}

const resetForm = () => {
    if (!formRef.value) return
    formRef.value.resetFields()
    selectedProducts.value = []
}

// 清理资源
const cleanupResources = () => {
    // 重置表单数据
    formData.红人名称 = ''
    formData.负责人 = ''
    formData.币种 = ''
    formData.花费 = null
    formData.物流链接 = ''
    formData.视频链接 = ''
    formData.预估上线时间 = ''
    formData.预估观看量 = null
    formData.合作进度 = '进行中'
    formData.物流进度 = '成功签收'
    // 只清理选中的产品，不清理产品选项
    selectedProducts.value = []
}

// 组件卸载时清理
onBeforeUnmount(() => {
    cleanupResources()
})

// 负责人添加相关
const addManagerVisible = ref(false)

const showAddManager = () => {
    addManagerVisible.value = true
}

const handleAddManagerSuccess = async () => {
    await influencerStore.getManagerList()
}
</script>

<style scoped>
.custom-drawer {
    --el-drawer-padding-primary: 0;
}

.drawer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    border-bottom: 1px solid var(--el-border-color-light);
    background-color: var(--el-bg-color);
}

.drawer-header h3 {
    margin: 0;
    font-size: 16px;
    color: var(--el-text-color-primary);
}

.header-actions {
    display: flex;
    gap: 12px;
}

.add-video-form {
    padding: 16px 20px;
    height: auto;
    min-height: calc(100% - 120px);
}

.drawer-footer {
    padding: 12px 20px;
    border-top: 1px solid var(--el-border-color-light);
    background-color: var(--el-bg-color);
    position: sticky;
    bottom: 0;
    z-index: 1;
}

.footer-tips {
    margin-bottom: 12px;
}

.footer-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.guide-content {
    padding: 12px;
}

.guide-content h4 {
    margin: 0 0 12px 0;
    color: var(--el-color-primary);
}

.guide-steps {
    margin: 0;
    padding-left: 20px;
}

.guide-steps li {
    margin-bottom: 8px;
    color: var(--el-text-color-regular);
    line-height: 1.5;
}

.guide-steps li:last-child {
    margin-bottom: 0;
}

:deep(.el-form-item) {
    margin-bottom: 16px;
}

:deep(.wide-select) {
    width: 100%;
}

/* 暗色模式适配 */
:deep(.dark) {

    .drawer-header,
    .drawer-footer {
        background-color: var(--el-bg-color-overlay);
    }
}

/* 动画效果 */
.slide-in {
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(20px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* 抽屉样式 */
:deep(.custom-drawer) {
    .el-drawer__header {
        margin-bottom: 0;
        padding: 16px 20px;
        border-bottom: 1px solid var(--el-border-color-lighter);
        background: var(--el-bg-color);
    }

    .el-drawer__body {
        padding: 0;
        overflow: auto;
    }
}

.add-video-form {
    padding: 20px;
    animation: fadeIn 0.3s ease-out;
}

/* 动画效果 */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.slide-in {
    animation: slideIn 0.3s ease-out;
    animation-fill-mode: both;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(20px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* 按钮样式 */
.form-buttons {
    margin-top: 30px;
    text-align: right;
}

.submit-btn,
.reset-btn {
    min-width: 100px;
    transition: all 0.3s ease;
}

.submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 表单项动画延迟 */
.el-form-item {
    animation-delay: calc(var(--el-transition-duration) * 0.1);
}

/* 暗黑模式适配 */
:deep(.dark) {
    .custom-drawer {
        .el-drawer__header {
            border-bottom-color: var(--el-border-color-darker);
            background: var(--el-bg-color-overlay);
        }
    }

    .submit-btn:hover {
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1);
    }
}

:deep(.el-form-item) {
    margin-bottom: 22px;
}

:deep(.el-cascader),
:deep(.el-date-picker),
:deep(.el-select),
:deep(.el-input-number) {
    width: 100%;
}

.form-row {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
}

.half-width {
    width: calc(50% - 8px);
}

.full-width {
    width: 100%;
}

:deep(.wide-select) {
    width: 100%;
}

:deep(.custom-number-input) {
    width: 100%;
}

:deep(.custom-number-input .el-input__inner) {
    text-align: left;
    padding-left: 12px;
}

.currency-option {
    display: flex;
    align-items: center;
    gap: 8px;
}

.currency-symbol {
    font-weight: bold;
    color: var(--el-color-primary);
}

/* 状态图标样式 */
.status-icon {
    margin-right: 8px;
    vertical-align: middle;
}

/* 选择器样式 */
:deep(.el-select-dropdown__item) {
    display: flex;
    align-items: center;
}

:deep(.el-select-dropdown__item.selected) {
    color: var(--el-color-primary);
}

/* 暗黑模式适配 */
html.dark {
    .add-video-form {
        background-color: var(--el-bg-color);
        color: var(--el-text-color-primary);
    }

    :deep(.el-input__inner),
    :deep(.el-textarea__inner) {
        background-color: var(--el-bg-color-overlay);
        border-color: var(--el-border-color-light);
        color: var(--el-text-color-primary);
    }

    :deep(.el-form-item__label) {
        color: var(--el-text-color-primary);
    }

    :deep(.dark-select) {
        background-color: var(--el-bg-color-overlay);
        border-color: var(--el-border-color-light);
    }
}

/* 状态备注样式 */
.form-item-extra {
    font-size: 11px;
    padding: 3px 8px;
    margin-top: 2px;
}

/* 暗黑模式适配 */
:deep(.dark) .form-item-extra {
    background-color: rgba(var(--el-color-warning-rgb), 0.15);
    border-left-color: var(--el-color-warning);
    text-decoration-color: var(--el-color-warning);
}

/* 调整表单项间距 */
:deep(.el-form-item__label) {
    padding-bottom: 4px;
    line-height: 1.4;
}

:deep(.el-form-item__content) {
    line-height: 1.4;
}

/* 优化输入框高度 */
:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
    --el-component-size: 32px;
}

/* 优化抽屉内容布局 */
:deep(.el-drawer__body) {
    padding: 0;
    display: flex;
    flex-direction: column;
}

.manager-select {
    display: flex;
    gap: 12px;
    align-items: center;
}

.manager-select .el-select {
    flex: 1;
}

.add-manager-btn {
    white-space: nowrap;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}
</style>
