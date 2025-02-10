# 创建新的负责人添加组件
<template>
    <el-dialog v-model="dialogVisible" :title="t('video.addManager')" width="400px" :close-on-click-modal="false">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="0">
            <el-form-item prop="name">
                <el-input v-model="form.name" :placeholder="t('video.selectResponsible')" />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="handleCancel">{{ t('common.cancel') }}</el-button>
                <el-button type="primary" @click="handleSubmit" :loading="submitting">
                    {{ t('common.submit') }}
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import {computed, reactive, ref} from 'vue'
import type {FormInstance} from 'element-plus'
import {ElMessage} from 'element-plus'
import {useI18n} from 'vue-i18n'
import {useInfluencerStore} from '@/store/useInfluencerStore'

const { t } = useI18n()
const influencerStore = useInfluencerStore()

// 定义props和emits
const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['update:modelValue', 'success'])

// 响应式数据
const dialogVisible = computed({
    get: () => props.modelValue,
    set: (value: boolean) => emit('update:modelValue', value)
})

const formRef = ref<FormInstance>()
const form = reactive({
    name: ''
})
const submitting = ref(false)

// 表单验证规则
const rules = {
    name: [
        { required: true, message: t('video.selectResponsible'), trigger: 'blur' },
        { pattern: /^\S+$/, message: t('video.invalidManagerName'), trigger: 'blur' }
    ]
}

// 提交处理
const handleSubmit = async () => {
    if (!formRef.value) return

    await formRef.value.validate()

    submitting.value = true
    try {
        await influencerStore.addManager(form.name)
        ElMessage.success(t('message.addManagerSuccess'))
        emit('success')
        handleCancel()
    } catch (error) {
        console.error(error)
        ElMessage.error(t('message.addManagerFailed'))
    } finally {
        submitting.value = false
    }
}

// 取消处理
const handleCancel = () => {
    dialogVisible.value = false
    form.name = ''
    formRef.value?.resetFields()
}
</script>

<style scoped>
.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

:deep(.el-dialog__body) {
    padding-top: 12px;
    padding-bottom: 12px;
}
</style>