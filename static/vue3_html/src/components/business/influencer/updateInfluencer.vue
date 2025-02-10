<template>
    <el-drawer v-model="visible" :title="$t('influencer.updateInfo')" direction="rtl" size="30%"
        :before-close="handleClose" :destroy-on-close="true" class="update-drawer">
        <div class="drawer-content">
            <div class="user-info-header">
                <el-descriptions :column="1" border>
                    <el-descriptions-item :label="$t('influencer.platform')">
                        {{ rowData.平台 }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="$t('influencer.userId')">
                        {{ rowData.id }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="$t('influencer.name')">
                        {{ rowData.红人名称 }}
                    </el-descriptions-item>
                </el-descriptions>
            </div>

            <el-form ref="formRef" :model="form" label-width="120px" class="update-form" :hide-required-asterisk="false"
                status-icon @submit.prevent>
                <div class="form-header">
                    <el-alert :title="$t('influencer.updateTips')" type="info" :closable="false" show-icon
                        class="update-alert" />
                </div>

                <el-form-item :label="$t('influencer.address')" prop="address" class="slide-in">
                    <el-input v-model="form.address" type="textarea" :rows="3"
                        :placeholder="$t('influencer.addressPlaceholder')" resize="none" />
                </el-form-item>

                <el-form-item :label="$t('influencer.contact')" prop="contacts" class="slide-in">
                    <div class="contacts-container">
                        <template v-for="(contact, index) in form.contacts" :key="index">
                            <el-tooltip :content="contact" placement="top" :effect="'dark'"
                                :popper-class="[isDark ? 'dark-tooltip' : 'light-tooltip']" :show-after="100"
                                :hide-after="0" :enterable="false">
                                <el-tag class="contact-tag" closable :disable-transitions="false"
                                    @close.stop="handleContactRemove(contact)">
                                    <span class="contact-content">
                                        <template v-if="isDiscordLink(contact)">
                                            <DiscordIcon class="contact_logo" :size="40" />
                                        </template>
                                        <template v-else-if="isEmailLink(contact)">
                                            <EmailIcon class="contact_logo" />
                                        </template>
                                        <template v-else>
                                            <WechatIcon class="contact_logo" :size="40"
                                                v-if="validatePhoneNumber(contact)" />
                                        </template>
                                        <el-icon>
                                            <QuestionFilled />
                                        </el-icon>
                                    </span>
                                </el-tag>
                            </el-tooltip>
                        </template>

                        <el-input v-if="contactInputVisible" ref="contactInputRef" v-model="contactInputValue"
                            class="contact-input" size="small" @keyup.enter.prevent="handleContactConfirm"
                            @blur="handleContactConfirm" />
                        <el-button v-else class="button-new-contact" size="small" @click.prevent="showContactInput">
                            + {{ $t('influencer.newContact') }}
                        </el-button>
                    </div>
                </el-form-item>

                <el-form-item :label="$t('influencer.tags')" prop="tags" class="slide-in">
                    <div class="tags-container">
                        <el-select v-model="form.tags" multiple filterable allow-create default-first-option
                            :placeholder="$t('influencer.newTag')" class="tag-select" @change="handleTagChange"
                            @visible-change="handleTagDropdownToggle">
                            <el-option v-for="tag in tagOptions" :key="tag" :label="tag" :value="tag" />
                        </el-select>
                    </div>
                </el-form-item>

                <div class="form-actions slide-in">
                    <el-button type="primary" @click.prevent="submitForm" :loading="props.loading"
                        :disabled="props.loading" class="submit-btn">
                        <el-icon>
                            <Check />
                        </el-icon>
                        {{ $t('common.submit') }}
                    </el-button>
                    <el-button @click.prevent="resetForm" :disabled="props.loading" class="reset-btn">
                        <el-icon>
                            <RefreshRight />
                        </el-icon>
                        {{ $t('common.reset') }}
                    </el-button>
                </div>
            </el-form>
        </div>
    </el-drawer>
</template>

<script setup lang="ts">
import {computed, defineEmits, defineProps, nextTick, ref, watch} from 'vue'
import type {FormInstance} from 'element-plus'
import {ElMessage} from 'element-plus'
import {Check, QuestionFilled, RefreshRight} from '@element-plus/icons-vue'
import {useDark} from '@vueuse/core'
import {parsePhoneNumberFromString} from 'libphonenumber-js'
import {useInfluencerStore} from '@/store/useInfluencerStore'
import {debounce} from 'lodash-es'
import EmailIcon from '@/components/common/icons/EmailIcon.vue'
import WechatIcon from '@/components/common/icons/WechatIcon.vue'
import DiscordIcon from '@/components/common/icons/DiscordIcon.vue'

interface InputRef {
    input: HTMLInputElement;
    focus: () => void;
}

const props = defineProps({
    modelValue: Boolean,
    rowData: {
        type: Object,
        required: true
    },
    loading: {
        type: Boolean,
        default: false
    }
})
const emit = defineEmits(['update:modelValue', 'submit'])

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
    visible.value = val
})
watch(visible, (val) => {
    emit('update:modelValue', val)
})

const loading = ref(false)
const formRef = ref<FormInstance>()
const form = ref({
    address: props.rowData.address || '',
    contacts: props.rowData.contact ? props.rowData.contact.split(',') : [],
    tags: props.rowData.tags ? props.rowData.tags.split(',') : []
})

const handleClose = (done: () => void) => {
    try {
        visible.value = false
        if (typeof done === 'function') {
            done()
        }
    } catch (error) {
        console.error('Error in handleClose:', error)
        ElMessage.error('关闭抽屉时发生错误')
    }
}

const initForm = () => {
    try {
        form.value = {
            address: props.rowData.地址 || '',
            contacts: props.rowData.联系方式 ? props.rowData.联系方式.split(',').filter((item: string) => item.trim()) : [],
            tags: props.rowData.标签 ? props.rowData.标签.split(',').filter((item: string) => item.trim()) : []
        }
    } catch (error) {
        console.error('Error in initForm:', error)
        ElMessage.error('初始化表单数据失败')
    }
}

watch(visible, (val) => {
    if (val) {
        initForm()
    }
})

const submitForm = async (e: Event) => {
    e.preventDefault()

    if (!formRef.value) return

    try {
        await formRef.value.validate((valid: boolean) => {
            if (valid) {
                const submitData = {
                    id: props.rowData.id,
                    地址: form.value.address,
                    联系方式: form.value.contacts.join(','),
                    标签: form.value.tags.join(',')
                }
                emit('submit', submitData)
            }
        })
    } catch (error) {
        console.error('Validation failed:', error)
        ElMessage.error('表单验证失败')
    }
}

const resetForm = () => {
    if (!formRef.value) return
    formRef.value.resetFields()
    // 清空数组
    form.value.contacts = []
    form.value.tags = []
}

// 联系方式输入相关
const contactInputVisible = ref(false)
const contactInputValue = ref('')
const contactInputRef = ref<InputRef | null>(null)

// 标签输入相关
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref<InputRef | null>(null)

// 显示联系方式输入框
const showContactInput = () => {
    contactInputVisible.value = true
    nextTick(() => {
        if (contactInputRef.value?.input) {
            contactInputRef.value.input.focus()
        }
    })
}

// 显示标签输入框
const showTagInput = () => {
    tagInputVisible.value = true
    nextTick(() => {
        if (tagInputRef.value?.input) {
            tagInputRef.value.input.focus()
        }
    })
}

// 处理联系方式输入确认
const handleContactConfirm = (e: Event | undefined) => {
    try {
        if (e) {
            e.preventDefault()
        }

        const trimmedValue = contactInputValue.value?.trim()
        if (trimmedValue) {
            // 检查是否已存在相同的联系方式
            if (!form.value.contacts.includes(trimmedValue)) {
                form.value.contacts.push(trimmedValue)
            } else {
                ElMessage.warning('该联系方式已存在')
            }
        }
        contactInputVisible.value = false
        contactInputValue.value = ''
    } catch (error) {
        console.error('Error in handleContactConfirm:', error)
        ElMessage.error('添加联系方式失败')
    }
}

// 处理标签输入确认
const handleTagConfirm = (e: Event | undefined) => {
    try {
        if (e) {
            e.preventDefault()
        }

        if (tagInputValue.value && tagInputValue.value.trim()) {
            // 检查是否已存在相同的标签
            if (!form.value.tags.includes(tagInputValue.value.trim())) {
                form.value.tags.push(tagInputValue.value.trim())
            } else {
                ElMessage.warning('该标签已存在')
            }
        }
        tagInputVisible.value = false
        tagInputValue.value = ''
    } catch (error) {
        console.error('Error in handleTagConfirm:', error)
        ElMessage.error('添加标签失败')
    }
}

// 移除联系方式
const handleContactRemove = (contact: string) => {
    try {
        const index = form.value.contacts.indexOf(contact)
        if (index !== -1) {
            form.value.contacts.splice(index, 1)
        }
    } catch (error) {
        console.error('Error in handleContactRemove:', error)
        ElMessage.error('移除联系方式失败')
    }
}

// 移除标签
const handleTagRemove = (tag: string) => {
    try {
        const index = form.value.tags.indexOf(tag)
        if (index !== -1) {
            form.value.tags.splice(index, 1)
        }
    } catch (error) {
        console.error('Error in handleTagRemove:', error)
        ElMessage.error('移除标签失败')
    }
}

// 检测暗黑模式
const isDark = useDark()

// 修改验证方法，添加类型检查和空值处理
const isDiscordLink = (url: string | undefined): boolean => {
    if (!url) return false;
    return url.includes("discord.com");
};

const isEmailLink = (link: string | undefined): boolean => {
    if (!link) return false;
    return link.includes('@');
};

const validatePhoneNumber = (contact: string | undefined): boolean => {
    if (!contact) return false;
    // 移除所有非数字字符
    const cleanNumber = contact.replace(/[^\d]/g, '');
    // 尝试解析清理后的号码
    try {
        const parsedNumber = parsePhoneNumberFromString('+' + cleanNumber);
        return parsedNumber?.isValid() || false;
    } catch {
        return false;
    }
};

// 获取显示文本
const getDisplayText = computed(() => (contact: string) => {
    try {
        if (!contact) return ''
        if (contact.includes('@')) {
            return contact.split('@')[0] + '@...'
        }
        if (contact.length > 10) {
            return contact.substring(0, 10) + '...'
        }
        return contact
    } catch (error) {
        console.error('Error in getDisplayText:', error)
        return contact
    }
})

// 获取显示标签文本
const getDisplayTag = (tag: string) => {
    if (tag.length > 10) {
        return tag.substring(0, 10) + '...'
    }
    return tag
}

// 获取标签列表
const influencerStore = useInfluencerStore()
const tagOptions = ref<string[]>([])

// 初始化标签列表
const initTagOptions = async () => {
    try {
        tagOptions.value = await influencerStore.getAllTags()
    } catch (error) {
        console.error('Failed to fetch tags:', error)
        ElMessage.error('获取标签列表失败')
    }
}

// 在组件挂载时获取标签列表
watch(visible, async (val) => {
    if (val) {
        await initTagOptions()
        initForm()
    }
})

// 防抖处理标签输入
const handleTagInputChange = debounce((value: string) => {
    if (value && !tagOptions.value.includes(value)) {
        tagOptions.value.push(value)
    }
}, 300)

// 新增的 tag 处理逻辑
const handleTagChange = (value: string[]) => {
    form.value.tags = value
}

const handleTagDropdownToggle = (visible: boolean) => {
    if (!visible) {
        tagInputVisible.value = false
    }
}
</script>

<style scoped>
.update-drawer :deep(.el-drawer__body) {
    padding: 0;
    height: 100%;
    overflow: hidden;
}

.update-drawer .drawer-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: auto;
    padding: 20px;
}

.update-drawer .user-info-header {
    flex-shrink: 0;
    margin-bottom: 20px;
}

.update-drawer .user-info-header :deep(.el-descriptions) {
    margin-bottom: 20px;
}

.update-drawer .user-info-header :deep(.el-descriptions__cell) {
    padding: 8px 12px;
}

.update-drawer .update-form {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.update-drawer .update-form .form-header {
    flex-shrink: 0;
}

.update-drawer .update-form .el-form-item {
    margin-bottom: 20px;
}

.update-drawer .update-form .el-form-item :deep(.el-input__wrapper) {
    padding: 0;
}

.update-drawer .update-form .el-form-item :deep(.el-textarea__inner) {
    min-height: 80px;
}

.update-drawer .update-form .form-actions {
    margin-top: auto;
    display: flex;
    gap: 12px;
}

.update-drawer .update-form .form-actions .el-button {
    flex: 1;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: start;
    width: 100%;
    padding: 12px;
    background-color: var(--el-fill-color-blank);
    border-radius: 8px;
    min-height: 36px;
}

.tag-input {
    width: 100px;
    margin-left: 8px;
    vertical-align: bottom;
}

.button-new-tag {
    margin-left: 8px;
    height: 32px;
    padding-top: 0;
    padding-bottom: 0;
}

/* .contact-tag,
.tag-item {
    margin-bottom: 8px;
} */

.contacts-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: start;
    width: 100%;
    padding: 12px;
    background-color: var(--el-fill-color-blank);
    border-radius: 8px;
    min-height: 36px;
}

.contact-tag {
    display: inline-flex;
    align-items: center;
    padding: 0 28px 0 12px;
    height: 32px;
    position: relative;
    box-sizing: border-box;
    max-width: 150px;
    min-width: 100px;
}

.contact-tag:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.contact-content {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    max-width: 100%;
}

.platform-icon {
    font-size: 16px;
    flex-shrink: 0;
}

.contact-tag :deep(.el-tag__content) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.contact-tag :deep(.el-tag__close) {
    position: absolute;
    right: 8px;
    transition: all 0.3s ease;
}

.contact-tag :deep(.el-tag__close:hover) {
    background-color: var(--el-color-danger);
    color: white;
    transform: rotate(90deg);
}

/* 暗黑模式适配 */
:deep(.dark-tooltip) {
    background-color: var(--el-color-black) !important;
    color: var(--el-color-white) !important;
}

:deep(.dark) .contact-tag {
    background-color: var(--el-color-primary-dark-9);
    border-color: var(--el-color-primary-dark-5);
    color: var(--el-text-color-primary);
}

/* 输入框样式优化 */
.contact-input {
    width: 200px;
    margin: 0;
    transition: all 0.3s ease;
}

.button-new-contact {
    padding: 0 16px;
    margin: 0;
    border-style: dashed;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 32px;
    min-width: 100px;
    transition: all 0.3s ease;
}

.button-new-contact:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 添加标签动画 */
.contact-tag-enter-active,
.contact-tag-leave-active {
    transition: all 0.3s ease;
}

.contact-tag-enter-from,
.contact-tag-leave-to {
    opacity: 0;
    transform: translateY(20px);
}

@media (prefers-color-scheme: dark) {
    .contacts-container {
        background-color: var(--el-bg-color-overlay);
    }
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
    /* 添加一些阴影使其在亮色模式下更容易识别 */
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) !important;
}

/* 确保 Tooltip 箭头颜色匹配 */
:deep(.light-tooltip[data-popper-placement^='top']) .el-popper__arrow::before {
    background-color: var(--el-bg-color) !important;
    border-color: var(--el-border-color-light) !important;
}

.contact_logo {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    object-fit: contain;
}

.tag-content {
    flex: 1;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 4px;
}

/* 添加loading状态的过渡效果 */
.el-button {
    transition: all 0.3s ease;
}

.el-button:disabled {
    cursor: not-allowed;
    opacity: 0.7;
}

/* 优化 Tooltip 的显示 */
:deep(.el-tooltip__trigger) {
    display: inline-flex;
    max-width: 100%;
}

:deep(.el-tooltip__trigger:focus-visible) {
    outline: none;
}

.tag-text {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: left;
}

.tag-select {
    width: 100%;
}

.tag-select :deep(.el-select__tags) {
    flex-wrap: wrap;
    max-height: 80px;
    overflow-y: auto;
}

.tag-select :deep(.el-select__input) {
    min-width: 80px;
}
</style>
