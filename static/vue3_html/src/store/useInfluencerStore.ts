import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRequestStore } from '@/config/request'

// 定义类型
interface TrackingStatus {
    number: string;
    status: string;
}

interface TaskDetail {
    id: string;
    url: string;
    status: string;
    createTime: string;
    updateTime: string;
    info: string;
    type: string;
    format: string;
}

interface TaskStats {
    total: number;
    created: number;
    processing: number;
    finish: number;
    error: number;
    taskDetails: {
        created: TaskDetail[];
        processing: TaskDetail[];
        finish: TaskDetail[];
        error: TaskDetail[];
    };
}

export const useInfluencerStore = defineStore('influencer', () => {
    // 状态
    const influencerList = ref<any[]>([])
    const isInfluencerLoading = ref(false)
    const videoList = ref<any[]>([])
    const projectDefinitions = ref<any[]>([])
    const projectDefinitionsNoFomat = ref<any[]>([])
    const managerList = ref<any[]>([])
    const isVideoLoading = ref(false)
    const error = ref(null)
    const taskStats = ref<TaskStats>({
        total: 0,
        created: 0,
        processing: 0,
        finish: 0,
        error: 0,
        taskDetails: {
            created: [],
            processing: [],
            finish: [],
            error: []
        }
    })
    const tagsList = ref<string[]>([])

    // 添加物流状态缓存
    const trackingCache = ref(new Map<string, any>())

    // 获取request store实例
    const requestStore = useRequestStore()

    // 添加永久缓存存储
    const TRACKING_CACHE_KEY = 'tracking_cache_permanent';


    // 获取KOL列表
    const getInfluencerList = async () => {
        try {
            isInfluencerLoading.value = true
            const response = await requestStore.get('/api/influencerSystem/get_influencer_list')
            influencerList.value = response.data.data
        } catch (err) {
            console.error('Failed to fetch influencer list:', err)
        } finally {
            isInfluencerLoading.value = false
        }
    }

    // 添加重置方法
    const resetVideoList = async () => {
        videoList.value = []
        isVideoLoading.value = false
    }

    const queryTrackingStatus = async (trackingNumbers: any) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/query_tracking', {
                tracking_numbers: trackingNumbers
            });
            return response.data.data
        } catch (error) {
            console.error('Failed to query tracking status:', error);
            return null;
        }
    };

    // 修改获取视频列表方法
    const getVideoList = async () => {
        try {
            isVideoLoading.value = true;
            const response = await requestStore.get('/api/influencerSystem/get_video_list');

            videoList.value = response.data.data;
        } catch (err) {
            console.error('Failed to fetch video list:', err);
        } finally {
            isVideoLoading.value = false;
        }
    };

    // 格式化任务信息
    const formatTaskInfo = (task: TaskDetail) => {
        switch (task.status) {
            case 'created':
                return `新建任务: ${task.url}`;
            case 'processing':
                return `处理中: ${task.url}`;
            case 'finish':
                return `完成: ${task.url} - ${task.info || ''}`;
            case 'error':
                return `错误: ${task.url} - ${task.info || ''}`;
            default:
                return task.url;
        }
    }

    const toDate = async () => {
        return new Date().toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }).replace(/\//g, '-')
    }

    // 提交红人信息
    const addInfluencerList = async (influencerData: any[]) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/add_influencer', {
                'influencer_list': influencerData
            })

            if (response.result === true) {
                return "添加红人成功"
            }
            throw new Error(response.message || '添加红人失败')
        } catch (error) {
            console.error('Failed to add influencer list:', error)
            throw error
        }
    }

    // 获取任务统计
    const findInfluencerList = async () => {
        try {
            const userId = localStorage.getItem('userId');
            if (!userId) {
                throw new Error('User ID not found');
            }

            const response = await requestStore.get('/redisApi/get/' + userId);
            let taskList = [];
            if (response.value) {
                taskList = JSON.parse(response.value);
            }

            const statusCounts = {
                created: 0,
                processing: 0,
                finish: 0,
                error: 0
            };

            const taskDetails: {
                created: TaskDetail[];
                processing: TaskDetail[];
                finish: TaskDetail[];
                error: TaskDetail[];
            } = {
                created: [],
                processing: [],
                finish: [],
                error: []
            };

            const statusMapping: { [key: number]: 'created' | 'processing' | 'finish' | 'error' } = {
                0: 'created',
                1: 'processing',
                2: 'finish',
                [-1]: 'error'
            };

            taskList.forEach((task: any) => {
                const mappedStatus = statusMapping[task.任务执行状态] || 'error';

                if (mappedStatus in statusCounts) {
                    statusCounts[mappedStatus]++;
                    taskDetails[mappedStatus].push({
                        id: task.id,
                        url: task.任务链接,
                        status: mappedStatus,
                        createTime: task.任务生成时间,
                        updateTime: task.任务更新时间,
                        info: task.任务状态描述,
                        type: task.任务类型,
                        format: `${task.任务类型}: ${task.任务链接} - ${task.任务状态描述}`
                    });
                }
            });

            taskStats.value = {
                total: taskList.length,
                ...statusCounts,
                taskDetails
            };

            return taskStats.value;
        } catch (err) {
            console.error('Failed to get task counts:', err);
            throw err;
        }
    }

    // 开始定期更新
    const POLL_INTERVAL = 60000; // 一分钟 = 60000毫秒
    let pollTimer: number | null = null;
    const startPolling = () => {
        // 立即执行一次
        findInfluencerList();

        // 设置定期执行
        pollTimer = setInterval(() => {
            findInfluencerList();
        }, POLL_INTERVAL); // 每35秒更新一次
    }

    // 停止定期更新
    const stopPolling = () => {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    const updateInfluencerInfo = async (data: any) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/update_influencer_info', data);
            return response;
        } catch (err) {
            console.error('Failed to update influencer info:', err);
            throw err;
        }
    }

    const deleteInfluencerInfo = async (data: any) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/delete_influencer', data);
            return response;
        } catch (err) {
            console.error('Failed to delete influencer info:', err);
            throw err;
        }
    }

    // 修改 transformProductData 方法
    const transformProductData = (data: any[]) => {
        const brandMap = new Map();

        data.forEach(item => {
            const brand = item.品牌;
            const project = item.项目;
            const product = item.产品;

            if (!brandMap.has(brand)) {
                brandMap.set(brand, new Map());
            }
            const projectMap = brandMap.get(brand);

            if (!projectMap.has(project)) {
                projectMap.set(project, []);
            }
            projectMap.get(project).push({
                label: product,
                value: product
            });
        });

        const result = [];
        for (const [brand, projectMap] of brandMap.entries()) {
            const children = [];
            for (const [project, products] of projectMap.entries()) {
                children.push({
                    label: project,
                    value: project,
                    children: products
                });
            }
            result.push({
                label: brand,
                value: brand,
                children: children
            });
        }
        return result;
    };

    // 修改获取项目定义方法
    const getProjectDefinitions = async () => {
        try {
            const response = await requestStore.get('/api/influencerSystem/get_project_definitions');
            projectDefinitions.value = await transformProductData(response.data.data);
            projectDefinitionsNoFomat.value = response.data.data;
        } catch (err) {
            console.error('Failed to get influencer info:', err);
            throw err;
        }
    };

    // 修改查询项目定义方法
    const queryProjectDefinitions = async () => {
        try {
            const response = await requestStore.get('/api/influencerSystem/query_project_definitions');
            projectDefinitions.value = await transformProductData(response.data.data);
            projectDefinitionsNoFomat.value = response.data.data;
            return response.data.data;
        } catch (err) {
            console.error('Failed to query project definitions:', err);
            throw err;
        }
    };

    // 获取所有标签列表
    const getAllTags = async () => {
        try {
            const response = await requestStore.get('/api/influencerSystem/get_all_tags')
            if (response.result === true) {
                tagsList.value = response.data.data || []
                return tagsList.value
            }
            throw new Error(response.message || '获取标签列表失败')
        } catch (error) {
            console.error('Failed to fetch tags list:', error)
            throw error
        }
    }

    // 修改更新视频信息方法
    const updateVideoInfo = async (data: any) => {
        try {
            isVideoLoading.value = true

            const response = await requestStore.post('/api/influencerSystem/update_video_info', data)
            return response
        } catch (err) {
            console.error('Failed to update video info:', err)
            throw err
        } finally {
            isVideoLoading.value = false
        }
    }

    const deleteVideo = async (parentId: number) => {
        try {
            isVideoLoading.value = true
            const response = await requestStore.post('/api/influencerSystem/delete_video_info', {
                'parentId': parentId
            })
            return response
        } catch (err) {
            console.error('Failed to delete video info:', err)
            throw err
        } finally {
            isVideoLoading.value = false
        }
    }

    // 获取管理员列表
    const getManagerList = async () => {
        try {
            const response = await requestStore.get('/api/influencerSystem/get_manager_list')
            managerList.value = response.data.data
        } catch (err) {
            console.error('Failed to fetch manager list:', err)
            throw err
        }
    }

    // 新增管理员
    const addManager = async (name: string) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/add_manager', {
                manager: name
            })
            if (response.result === true) {
                return "更新负责人成功"
            } else {
                throw new Error(response.data.message || '添加失败')
            }
        } catch (error) {
            console.error('添加管理员失败:', error)
            throw error
        }
    }

    // 添加视频
    const addVideo = async (data: any) => {
        try {
            console.log("添加视频数据为 ", data)
            const response = await requestStore.post('/api/influencerSystem/add_video', data)

            if (response.result === true) {
                return "success video"
            }
            throw new Error(response.message || '添加失败')
        } catch (error: any) {
            console.error('添加视频失败:', error)
            throw error
        }
    }

    // 更新指标定义
    const updateProjectDefinition = async (data: any) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/update_project_definition', { 'data': data });
            if (response.result === true) {
                return "更新指标成功";
            }
            throw new Error(response.message || '更新失败');
        } catch (error) {
            console.error('Failed to update project definition:', error);
            throw error;
        }
    }

    // 删除指标定义
    const deleteProjectDefinition = async (id: number) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/delete_project_definition', { 'id': id });
            if (response.result === true) {
                return "删除指标成功";
            }
            throw new Error(response.message || '删除失败');
        } catch (error) {
            console.error('Failed to delete project definition:', error);
            throw error;
        }
    }

    // 新增指标定义
    const addProjectDefinition = async (data: any) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/add_project_definition', { 'data': data });
            if (response.result === true) {
                return "新增指标成功";
            }
            throw new Error(response.message || '新增失败');
        } catch (error) {
            console.error('Failed to add project definition:', error);
            throw error;
        }
    }

    return {
        influencerList,
        isInfluencerLoading,
        error,
        taskStats,
        isVideoLoading,
        videoList,
        projectDefinitions,
        managerList,
        tagsList,
        projectDefinitionsNoFomat,
        getAllTags,
        getInfluencerList,
        addInfluencerList,
        findInfluencerList,
        startPolling,
        stopPolling,
        updateInfluencerInfo,
        deleteInfluencerInfo,
        getVideoList,
        resetVideoList,
        getProjectDefinitions,
        queryProjectDefinitions,
        updateVideoInfo,
        deleteVideo,
        getManagerList,
        addManager,
        addVideo,
        queryTrackingStatus,
        trackingCache,
        updateProjectDefinition,
        deleteProjectDefinition,
        addProjectDefinition,
        transformProductData,
    }
})
