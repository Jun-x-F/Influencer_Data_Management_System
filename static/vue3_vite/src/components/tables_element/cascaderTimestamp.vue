<template>
    <div>
        <!-- 消息徽章与按钮 -->
        <el-button type="primary" class="view-button" @click="drawer = true">
            查看任务执行情况
        </el-button>

        <!-- 任务执行情况抽屉 -->
        <el-drawer v-model="drawer" v-loading="loading" title="任务执行情况" :with-header="false" size="60%">
            <!-- 条件渲染：当消息列表为空时显示 <el-empty>，否则显示 <el-timeline> -->
            <div v-if="useMessage.messageList.length === 0" class="empty-container">
                <el-empty description="暂无数据" />
            </div>
            <div v-else class="timeline-container">
                <el-timeline class="timeline">
                    <el-timeline-item v-for="(message, index) in useMessage.messageList" :key="index" center
                        placement="top" :icon="getMessageIcon(message.status)" :color="getMessageColor(message.status)"
                        :timestamp="message.timestamp">
                        <el-card>
                            <h4>日志
                                <el-tag :type="getTagType(message.status)">
                                    {{ getTagLabel(message.status) }}
                                </el-tag>
                            </h4>

                            <p>{{ message.message }}</p>
                        </el-card>


                    </el-timeline-item>

                </el-timeline>
            </div>
        </el-drawer>
    </div>
</template>

<script lang="ts" setup>
import {onMounted, ref, watch} from 'vue';
import {useMessageInfo} from '@/stores/message.js';
// 导入 Element Plus 图标组件
import {ArrowUp, Check, Close} from '@element-plus/icons-vue';
// 定义响应式状态
const drawer = ref(false);
const useMessage = useMessageInfo();
const loading = ref(false);
// 监听抽屉状态，当抽屉打开时获取消息
watch(drawer, async (val) => {
    if (val) {
        loading.value = true;
        await useMessage.getMessage();
        console.log('messageList', useMessage.messageList);
        loading.value = false;
    }
});

// 在组件挂载时获取初始数据
onMounted(async () => {
    await useMessage.getMessage();
});

// 方法：根据状态获取颜色
const getMessageColor = (status: string): string => {
    return status === 'error' ? 'red' : 'green';
};

// 方法：根据状态获取标签类型
const getTagType = (status: string): string => {
    return status === 'error' ? 'danger' : 'success';
};

// 方法：根据状态获取标签文本
const getTagLabel = (status: string): string => {
    return status === 'error' ? 'Error' : 'Success';
};

// 方法：根据状态获取图标组件
const getMessageIcon = (status: string) => {
    if (status === 'error') return Close;
    if (status === 'finish' || status === 'success') return Check;
    return ArrowUp; // 其他状态显示向上箭头
};

// 方法：根据状态获取图标的 CSS 类（可选，用于调整图标样式）
const getIconClass = (status: string): string => {
    return status === 'error' ? 'icon-error' :
        (status === 'finish' || status === 'success') ? 'icon-success' :
            'icon-other';
};

</script>

<style scoped>
.notice-container {
    display: flex;
    align-items: center;
    padding: 20px;
}

.badge-item {
    position: relative;
}

.view-button {
    margin-left: 16px;
}

.timeline-container {
    max-width: 600px;
    margin: 20px auto;
}

.empty-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    /* 根据需要调整高度 */
}

.timeline {
    width: 100%;
}

/* 图标样式调整 */
.icon-error {
    color: red;
    font-size: 20px;
}

.icon-success {
    color: green;
    font-size: 20px;
}

.icon-other {
    color: #409EFF;
    /* Element Plus 默认蓝色 */
    font-size: 20px;
}
</style>