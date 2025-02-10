<template>
    <el-drawer v-model="visible" :title="t('video.updateVideo')" :size="800" :destroy-on-close="true" direction="rtl"
        @close="handleClose" class="custom-drawer">
        <template #header>
            <div class="drawer-header">
                <h3>{{ t('video.updateVideo') }}</h3>
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
            <!-- 用户信息头部 -->
            <div class="user-info-header">
                <el-descriptions :column="1" border size="small">
                    <el-descriptions-item :label="t('video.platform')" label-class-name="label-bold">
                        <el-tag size="small" :type="getPlatformType(rowData.平台)">
                            <el-icon class="platform-icon">
                                <component :is="getPlatformIcon(rowData.平台)" />
                            </el-icon>
                            {{ rowData.平台 }}
                        </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('video.responsible')" label-class-name="label-bold">
                        {{ rowData.负责人 }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('video.name')" label-class-name="label-bold">
                        <span class="influencer-name">{{ rowData.红人名称 }}</span>
                    </el-descriptions-item>
                </el-descriptions>
            </div>

            <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="update-form">
                <!-- 视频链接 -->
                <el-form-item :label="t('video.videoLink')" prop="videoUrl" class="slide-in">
                    <el-input v-model="form.videoUrl" :placeholder="t('video.videoLinkPlaceholder')"
                        @input="handleVideoLinkChange" />
                </el-form-item>

                <!-- 合作进度 -->
                <el-form-item :label="t('video.cooperationStatus')" prop="cooperationStatus" class="slide-in">
                    <el-select v-model="form.cooperationStatus" class="wide-select">
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
                        <el-option :label="t('video.cooperationCancelled')" value="合作失败">
                            <el-icon class="status-icon">
                                <CircleCloseFilled />
                            </el-icon>
                            {{ t('video.cooperationCancelled') }}
                        </el-option>
                    </el-select>
                    <div class="form-item-extra" role="note">{{ t('video.cooperationDefaultStatus') }}</div>
                </el-form-item>

                <!-- 物流链接 -->
                <el-form-item :label="t('video.logisticsLink')" prop="trackingUrl" class="slide-in">
                    <el-input v-model="form.trackingUrl" :placeholder="t('video.logisticsLink')"
                        @input="handleLogisticsLinkChange" />
                </el-form-item>

                <!-- 物流进度 -->
                <el-form-item :label="t('video.logisticsStatus')" prop="logisticsStatus" class="slide-in">
                    <el-select v-model="form.logisticsStatus" class="wide-select" :disabled="isLogisticsStatusDisabled">
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

                <div class="form-row">
                    <!-- 币种 -->
                    <el-form-item :label="t('video.currency')" prop="currency" class="slide-in half-width">
                        <el-select v-model="form.currency" :placeholder="t('video.currency')" class="wide-select">
                            <el-option label="USD - 美元" value="USD">
                                <span class="currency-option">
                                    <span class="currency-symbol">$</span>
                                    <span>USD - 美元</span>
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
                            <el-option label="CNY - 人民币" value="CNY">
                                <span class="currency-option">
                                    <span class="currency-symbol">¥</span>
                                    <span>CNY - 人民币</span>
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
                    <el-form-item :label="t('video.cost')" prop="cost" class="slide-in half-width">
                        <el-input-number v-model="form.cost" :min="0" :precision="2" :step="100" :controls="false"
                            :placeholder="t('video.cost')" class="custom-number-input" />
                    </el-form-item>
                </div>

                <div class="form-row">
                    <!-- 预估上线时间 -->
                    <el-form-item :label="t('video.estimatedOnlineTime')" prop="estimatedOnlineDate"
                        class="slide-in half-width">
                        <el-date-picker v-model="form.estimatedOnlineDate" type="datetime"
                            :placeholder="t('video.estimatedOnlineTime')" class="wide-select" />
                    </el-form-item>

                    <!-- 预估观看量 -->
                    <el-form-item :label="t('video.estimatedViews')" prop="estimatedViews" class="slide-in half-width">
                        <el-input-number v-model="form.estimatedViews" :min="0" :step="1000"
                            :placeholder="t('video.estimatedViews')" class="wide-select" />
                    </el-form-item>
                </div>

                <!-- 产品信息 -->
                <el-form-item :label="t('video.product')" prop="products" class="slide-in">
                    <el-cascader v-model="selectedProducts" :options="productOptions" :props="{
                        multiple: true,
                        checkStrictly: false,
                        emitPath: true,
                        expandTrigger: 'hover',
                        children: 'children',
                        lazy: false,
                        leaf: 'leaf',
                        value: 'value',
                        label: 'label'
                    }" :show-all-levels="true" collapse-tags collapse-tags-tooltip clearable filterable
                        :loading="loading" :placeholder="t('video.selectProduct')" @change="handleProductChange">
                        <template #default="{ node, data }">
                            <span>{{ data.label }}</span>
                            <span v-if="data.count" style="margin-left: 4px">({{ data.count }})</span>
                        </template>
                    </el-cascader>
                </el-form-item>
            </el-form>
        </div>

        <template #footer>
            <div class="drawer-footer">
                <div class="footer-tips">
                    <el-alert :title="t('guide.tips')" type="info" :closable="false" show-icon />
                </div>
                <div class="footer-buttons">
                    <el-button type="primary" @click="submitForm" :loading="submitting">
                        <el-icon>
                            <Check />
                        </el-icon>
                        {{ t('common.submit') }}
                    </el-button>
                    <el-button @click="handleClose">
                        <el-icon>
                            <Close />
                        </el-icon>
                        {{ t('common.cancel') }}
                    </el-button>
                </div>
            </div>
        </template>
    </el-drawer>
</template>

<script setup lang="ts">
import {computed, nextTick, onBeforeUnmount, onMounted, reactive, ref} from 'vue'
import {useInfluencerStore} from '@/store/useInfluencerStore'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'
import {useI18n} from 'vue-i18n'
import {useDark} from '@vueuse/core'
import {
  Check,
  CircleCheckFilled,
  CircleCloseFilled,
  Close,
  Loading,
  Message,
  Platform,
  QuestionFilled,
  VideoPlay
} from '@element-plus/icons-vue'

const { t } = useI18n()
const influencerStore = useInfluencerStore()
const isDark = useDark()

// 添加类型定义
interface Product {
    品牌: string;
    项目: string;
    产品: string;
}

interface VideoData {
    id?: number;
    products?: Product[];
    品牌?: string;
    项目?: string;
    产品?: string;
    [key: string]: any;
}

// 添加类型定义
interface ProductOption {
    label: string;
    value: string;
    children?: ProductOption[];
    count?: number;
    leaf?: boolean;
}

// Props 类型定义
const props = defineProps<{
    modelValue: boolean;
    rowData: VideoData;
}>()

// 定义 emits
const emit = defineEmits(['update:modelValue', 'close', 'update-success'])

// 抽屉显示状态
const visible = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
})

// 提交状态
const submitting = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
    videoUrl: props.rowData.视频链接 || '',
    cooperationStatus: props.rowData.合作进度 || '进行中',
    trackingUrl: props.rowData.物流单号 || '',
    logisticsStatus: props.rowData.物流进度 || '成功签收',
    cost: Number(props.rowData.花费) || null,
    currency: props.rowData.币种 || 'USD',
    estimatedViews: props.rowData.预估观看量 || null,
    estimatedOnlineDate: props.rowData.预估上线时间 || '',
    parentId: props.rowData.parentId
})

// 验证规则
const rules = reactive<FormRules>({
    videoUrl: [
        {
            validator: (rule, value, callback) => {
                // 当合作状态不是"合作失败"时，视频链接必填
                if (form.cooperationStatus !== '合作失败' && (!value || value.trim() === '')) {
                    const errorMessage = t('video.videoLinkRequired') || '视频链接不能为空';
                    callback(new Error(errorMessage));
                } else {
                    callback();
                }
            },
            trigger: 'blur'
        }
    ],
    cooperationStatus: [
        { required: true, message: t('video.cooperationStatus'), trigger: 'change' }
    ],
    logisticsStatus: [
        { required: true, message: t('video.logisticsStatus'), trigger: 'change' }
    ]
})

// 产品选择相关
const productOptions = ref<ProductOption[]>([])
const selectedProducts = ref<[string, string, string][]>([])

// 添加搜索匹配用的标准化函数
const normalizeForSearch = (str: string): string => {
    return str
        .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '') // 只保留字母、数字和中文字符
        .toLowerCase() // 转换为小写
        .trim(); // 移除首尾空格
}

// 修改初始化数据的逻辑
onMounted(async () => {
    try {
        loading.value = true
        await Promise.all([
            influencerStore.getProjectDefinitions(),
            influencerStore.getManagerList()
        ])
        nextTick(() => {
            productOptions.value = influencerStore.projectDefinitions;

            // 初始化已选产品
            if (props.rowData) {
                // 处理产品数据可能是数组的情况
                const products = Array.isArray(props.rowData.products) ? props.rowData.products : [];

                if (products.length > 0) {
                    // 如果有products数组，直接使用它
                    selectedProducts.value = products.map(product => [
                        product.品牌,
                        product.项目,
                        product.产品
                    ]);
                } else if (props.rowData.产品 && props.rowData.项目 && props.rowData.品牌) {
                    // 兼容旧的单个产品格式
                    selectedProducts.value = [[
                        props.rowData.品牌,
                        props.rowData.项目,
                        props.rowData.产品
                    ]];
                }

                // 添加日志输出
                console.log('初始化选中的产品:', selectedProducts.value);
                console.log('产品选项数据:', productOptions.value);

                // 使用标准化字符串进行验证
                selectedProducts.value.forEach(product => {
                    console.log('验证产品路径:', product);
                    let found = false;
                    const [brand, project, item] = product;

                    const brandOption = productOptions.value.find((opt: ProductOption) =>
                        normalizeForSearch(opt.value) === normalizeForSearch(brand)
                    );

                    if (brandOption && brandOption.children) {
                        const projectOption = brandOption.children.find((opt: ProductOption) =>
                            normalizeForSearch(opt.value) === normalizeForSearch(project)
                        );

                        if (projectOption && projectOption.children) {
                            const itemOption = projectOption.children.find((opt: ProductOption) =>
                                normalizeForSearch(opt.value) === normalizeForSearch(item)
                            );
                            found = !!itemOption;

                            // 如果找到匹配，使用原始值（保留特殊字符）
                            if (found && itemOption) {
                                selectedProducts.value = [[
                                    brandOption.value,
                                    projectOption.value,
                                    itemOption.value
                                ]];
                            }
                        }
                    }

                    if (!found) {
                        // 如果没有找到完全匹配，尝试模糊匹配
                        console.log('尝试模糊匹配...');

                        // 遍历所有选项进行模糊匹配
                        productOptions.value.forEach((brandOpt: ProductOption) => {
                            if (brandOpt.children) {
                                brandOpt.children.forEach((projectOpt: ProductOption) => {
                                    if (projectOpt.children) {
                                        projectOpt.children.forEach((itemOpt: ProductOption) => {
                                            if (normalizeForSearch(itemOpt.value) === normalizeForSearch(item)) {
                                                console.log('找到模糊匹配:', {
                                                    brand: brandOpt.value,
                                                    project: projectOpt.value,
                                                    item: itemOpt.value
                                                });
                                                // 更新选中值为找到的完整路径（使用原始值）
                                                selectedProducts.value = [[
                                                    brandOpt.value,
                                                    projectOpt.value,
                                                    itemOpt.value
                                                ]];
                                                found = true;
                                            }
                                        });
                                    }
                                });
                            }
                        });
                    }

                    console.log('产品路径是否存在:', found);
                });
            }
        })
    } catch (error) {
        console.error('初始化数据失败:', error)
        ElMessage.error(t('message.loadFailed'))
    } finally {
        loading.value = false
    }
})

// 修改产品选择变化处理函数
const handleProductChange = (value: [string, string, string][]) => {
    selectedProducts.value = value;
    console.log('选中的产品变化:', selectedProducts.value);
}

// 监听视频链接变化
const handleVideoLinkChange = (value: string) => {
    if (value && form.cooperationStatus === '进行中') {
        form.cooperationStatus = '合作完成'
    }
}

// 验证17track链接
const validate17TrackUrl = (value: string): boolean => {
    return value.includes('17track.net')
}

// 监听物流链接变化
const handleLogisticsLinkChange = (value: string) => {
    if (value && !validate17TrackUrl(value)) {
        ElMessage.warning(t('video.invalidLogisticsLink'))
        form.trackingUrl = ''
        return
    }
    form.logisticsStatus = value ? '等待获取物流状态' : '成功签收'
}

// 计算属性：控制物流进度是否禁用
const isLogisticsStatusDisabled = computed(() => {
    return !form.trackingUrl
})

// 获取平台标签类型
const getPlatformType = (platform: string | null | undefined) => {
    if (!platform) return 'info'

    const platformMap: Record<string, string> = {
        'tiktok': 'warning',
        'instagram': 'success',
        'youtube': 'danger',
        'facebook': 'primary',
        'x': 'info',
        'other': 'info'
    }
    return platformMap[platform.toLowerCase()] || 'info'
}

// 获取平台图标
const getPlatformIcon = (platform: string | null | undefined) => {
    if (!platform) return Platform

    const platformMap: Record<string, any> = {
        'tiktok': VideoPlay,
        'instagram': Message,
        'youtube': VideoPlay,
        'facebook': Message,
        'x': Message,
        'other': Platform
    }
    return platformMap[platform.toLowerCase()] || Platform
}

// 修改提交表单时的处理
const submitForm = async () => {
    if (!formRef.value) return

    try {
        submitting.value = true
        await formRef.value.validate()

        const formattedData = {
            ...form,
            products: selectedProducts.value.map(path => ({
                品牌: path[0],
                项目: path[1],
                产品: path[2]
            }))
        }

        await influencerStore.updateVideoInfo({
            id: props.rowData.id,
            ...formattedData
        })

        ElMessage.success(t('message.updateSuccess'))
        emit('update-success')
        handleClose()
    } catch (error: any) {
        console.error('更新失败:', error || t('video.videoLinkRequired'))
        ElMessage.error(t('message.updateFailed') + ': ' + (error.message || t('video.videoLinkRequired')))
    } finally {
        submitting.value = false
    }
}

// 处理关闭
const handleClose = () => {
    visible.value = false
    emit('close')
    formRef.value?.resetFields()
    selectedProducts.value = []
}

// 组件卸载时清理
onBeforeUnmount(() => {
    formRef.value?.resetFields()
    selectedProducts.value = []
})
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

/* 用户信息样式 */
.user-info-header {
    margin-bottom: 24px;
    border-radius: 8px;
    overflow: hidden;
}

.user-info-header :deep(.el-descriptions) {
    --el-descriptions-item-bordered-label-background: var(--el-fill-color-light);
}

.influencer-name {
    font-weight: 600;
    color: var(--el-color-primary);
}

/* 表单布局 */
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

/* 状态图标样式 */
.status-icon {
    margin-right: 8px;
    vertical-align: middle;
}

/* 状态备注样式 */
.form-item-extra {
    font-size: 11px;
    padding: 3px 8px;
    margin-top: 2px;
    background-color: rgba(var(--el-color-warning-rgb), 0.1);
    border-left: 3px solid var(--el-color-warning);
    border-radius: 4px;
    color: var(--el-text-color-regular);
    line-height: 1.4;
    white-space: pre-line;
}

/* 货币选项样式 */
.currency-option {
    display: flex;
    align-items: center;
    gap: 8px;
}

.currency-symbol {
    font-weight: bold;
    color: var(--el-color-primary);
}

/* 输入框样式优化 */
:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
    --el-component-size: 32px;
}

/* 表单项间距 */
:deep(.el-form-item__label) {
    padding-bottom: 4px;
    line-height: 1.4;
}

:deep(.el-form-item__content) {
    line-height: 1.4;
}

/* 平台图标样式 */
.platform-icon {
    margin-right: 4px;
    vertical-align: middle;
}

:deep(.el-tag .el-icon) {
    vertical-align: middle;
    margin-right: 4px;
}
</style>
