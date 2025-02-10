import {defineStore} from 'pinia'
import {ref} from 'vue'
import {useRequestStore} from '@/config/request'

export const useInfluencerStore = defineStore('influencer', () => {
    // 状态
    const influencerList = ref([])
    const isInfluencerLoading = ref(false)
    const videoList = ref([])
    const projectDefinitions = ref([])
    const projectDefinitionsNoFomat = ref([])
    const managerList = ref([])  // 添加管理员列表状态
    const isVideoLoading = ref(false)
    const error = ref(null)
    const taskStats = ref({
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
    const tagsList = ref<string[]>([]) // 添加标签列表状态

    // 添加物流状态缓存
    const trackingCache = ref(new Map<string, any>())

    // 获取request store实例
    const requestStore = useRequestStore()

    // 添加永久缓存存储
    const TRACKING_CACHE_KEY = 'tracking_cache_permanent'

    // 初始化时从 localStorage 加载永久缓存
    const loadPermanentCache = () => {
        try {
            const savedCache = localStorage.getItem(TRACKING_CACHE_KEY)
            if (savedCache) {
                const parsedCache = JSON.parse(savedCache)
                for (const [key, value] of Object.entries(parsedCache)) {
                    trackingCache.value.set(key, value)
                }
            }
        } catch (error) {
            console.error('Failed to load permanent tracking cache:', error)
        }
    }

    // 保存永久缓存到 localStorage
    const savePermanentCache = (cacheKey: string, data: any) => {
        try {
            const savedCache = localStorage.getItem(TRACKING_CACHE_KEY)
            const cacheData = savedCache ? JSON.parse(savedCache) : {}
            cacheData[cacheKey] = data
            localStorage.setItem(TRACKING_CACHE_KEY, JSON.stringify(cacheData))
        } catch (error) {
            console.error('Failed to save permanent tracking cache:', error)
        }
    }

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

    // 解析物流单号
    const parseTrackingNumbers = (trackingUrl: string): string[] => {
        try {
            const url = new URL(trackingUrl)
            const nums = url.hash.split('nums=')[1]
            if (!nums) return []
            return nums.split(',').map(num => num.trim())
        } catch {
            return []
        }
    }

    // 定义物流状态接口
    interface TrackingStatus {
        number: string;
        status: string;
    }

    interface TrackingResponse {
        data: TrackingStatus[];
    }

    // 修改查询物流状态方法
    const queryTrackingStatus = async (trackingUrl: string) => {
        try {
            if (!trackingUrl || !trackingUrl.includes('17track.net')) {
                return null
            }

            const trackingNumbers = parseTrackingNumbers(trackingUrl)
            if (trackingNumbers.length === 0) {
                return null
            }

            // 检查缓存
            const cacheKey = trackingNumbers.sort().join(',')
            if (trackingCache.value.has(cacheKey)) {
                const cachedData = trackingCache.value.get(cacheKey)
                // 如果是所有单号都成功签收，直接返回缓存数据
                if (cachedData.data.every((status: TrackingStatus) => status.status === '成功签收')) {
                    return cachedData.data
                }
                // 非成功签收状态检查缓存时间
                if (Date.now() - cachedData.timestamp < 3600000) {
                    return cachedData.data
                }
            }

            // 发送请求到后端
            const response = await requestStore.post<TrackingResponse>('/api/influencerSystem/query_tracking', {
                tracking_numbers: trackingNumbers
            })

            if (response.result === true && response.data?.data) {
                const trackingData = {
                    data: response.data.data,
                    timestamp: Date.now()
                }

                // 如果所有物流状态都是成功签收，则永久缓存
                if (response.data.data.every(status => status.status === '成功签收')) {
                    savePermanentCache(cacheKey, trackingData)
                }

                // 更新内存缓存
                trackingCache.value.set(cacheKey, trackingData)
                return response.data.data
            }
            return null
        } catch (error) {
            console.error('Failed to query tracking status:', error)
            return null
        }
    }

    // 格式化物流状态显示
    const formatTrackingStatus = (statuses: TrackingStatus[] | null): string => {
        if (!statuses || statuses.length === 0) return '成功签收'

        // 按物流单号排序
        const sortedStatuses = [...statuses].sort((a, b) => a.number.localeCompare(b.number))

        return sortedStatuses.map(status =>
            `${status.number}: ${status.status}`
        ).join('\n')
    }

    // 修改获取视频列表方法
    const getVideoList = async () => {
        try {
            isVideoLoading.value = true
            const response = await requestStore.get('/api/influencerSystem/get_video_list')

            // 处理每个视频的物流状态
            const videos = response.data.data
            const trackingPromises = videos.map(async (video: any) => {
                if (video.物流单号) {
                    const trackingStatus = await queryTrackingStatus(video.物流单号)
                    video.物流进度 = formatTrackingStatus(trackingStatus)
                } else {
                    video.物流进度 = '成功签收'
                }
                return video
            })

            // 并行处理所有物流状态查询
            videoList.value = await Promise.all(trackingPromises)
        } catch (err) {
            console.error('Failed to fetch video list:', err)
        } finally {
            isVideoLoading.value = false
        }
    }

    // 格式化任务信息
    const formatTaskInfo = (task: any) => {
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
            // 获取用户id
            const userId = localStorage.getItem('userId');
            if (!userId) {
                throw new Error('User ID not found');
            }

            const response = await requestStore.get('/redisApi/get/' + userId);
            let taskList = [];
            if (response.value) {
                taskList = JSON.parse(response.value);
            }

            // 根据status统计数量和分类任务
            const statusCounts = {
                created: 0,
                processing: 0,
                finish: 0,
                error: 0
            };

            const taskDetails = {
                created: [],
                processing: [],
                finish: [],
                error: []
            };

            // 状态映射
            const statusMapping = {
                0: 'created',     // PENDING -> created (待执行)
                1: 'processing',  // RUNNING -> processing (正在执行)
                2: 'finish',      // COMPLETED -> finish (完成任务)
                [-1]: 'error'     // FAILED -> error (任务执行失败/重复提交任务)
            };

            // 遍历任务列表统计各状态数量并分类
            taskList.forEach(task => {
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

            // 更新状态
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

    async function transformProductData(data) {
        // 用 Map 分组（第一层：品牌；第二层：项目）
        const brandMap = new Map()

        data.forEach(item => {
            const brand = item.品牌
            const project = item.项目
            const product = item.产品

            // 如果 Map 中还没有该品牌，则先添加
            if (!brandMap.has(brand)) {
                brandMap.set(brand, new Map())
            }
            const projectMap = brandMap.get(brand)

            // 如果 Map 中还没有该项目，则先添加
            if (!projectMap.has(project)) {
                projectMap.set(project, [])
            }
            // 将产品加入到对应项目的数组中
            projectMap.get(project).push({
                label: product,
                value: product
            })
        })

        // 转换 Map 为 cascader 组件需要的数组格式
        const result = []
        for (const [brand, projectMap] of brandMap.entries()) {
            const children = []
            for (const [project, products] of projectMap.entries()) {
                children.push({
                    label: project,
                    value: project,
                    children: products
                })
            }
            result.push({
                label: brand,
                value: brand,
                children: children
            })
        }
        return result
    }


    const getProjectDefinitions = async () => {
        try {
            const response = await requestStore.get('/api/influencerSystem/get_project_definitions');
            projectDefinitions.value = await transformProductData(response.data.data)
            projectDefinitionsNoFomat.value = response.data.data
        } catch (err) {
            console.error('Failed to get influencer info:', err);
            throw err;
        }
    }

    // 修改更新视频信息方法
    const updateVideoInfo = async (data: any) => {
        try {
            isVideoLoading.value = true

            // 处理物流状态
            if (data.物流单号) {
                const trackingStatus = await queryTrackingStatus(data.物流单号)
                data.物流进度 = formatTrackingStatus(trackingStatus)
            } else {
                data.物流进度 = '成功签收'
            }

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
            const response = await requestStore.post('/api/influencerSystem/update_project_definition', { 'data': data })
            if (response.result === true) {
                return "更新指标成功"
            }
            throw new Error(response.message || '更新失败')
        } catch (error) {
            console.error('Failed to update project definition:', error)
            throw error
        }
    }

    // 删除指标定义
    const deleteProjectDefinition = async (id: number) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/delete_project_definition', { 'id': id })
            if (response.result === true) {
                return "删除指标成功"
            }
            throw new Error(response.message || '删除失败')
        } catch (error) {
            console.error('Failed to delete project definition:', error)
            throw error
        }
    }

    // 新增指标定义
    const addProjectDefinition = async (data: any) => {
        try {
            const response = await requestStore.post('/api/influencerSystem/add_project_definition', { 'data': data })
            if (response.result === true) {
                return "新增指标成功"
            }
            throw new Error(response.message || '新增失败')
        } catch (error) {
            console.error('Failed to add project definition:', error)
            throw error
        }
    }

    // 查询指标定义列表
    const queryProjectDefinitions = async () => {
        try {
            const response = await requestStore.get('/api/influencerSystem/query_project_definitions')
            projectDefinitions.value = await transformProductData(response.data.data)
            projectDefinitionsNoFomat.value = response.data.data
            return response.data.data
        } catch (err) {
            console.error('Failed to query project definitions:', err)
            throw err
        }
    }

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

    // 在 store 初始化时加载永久缓存
    loadPermanentCache()

    return {
        influencerList,
        isInfluencerLoading,
        error,
        taskStats,
        isVideoLoading,
        videoList,
        projectDefinitions,
        managerList,  // 导出管理员列表
        tagsList,  // 导出标签列表
        projectDefinitionsNoFomat,
        getAllTags,  // 导出获取标签方法
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
        queryProjectDefinitions,  // 导出新方法
        updateVideoInfo,
        deleteVideo,
        getManagerList,  // 导出获取管理员列表方法
        addManager,
        addVideo,
        queryTrackingStatus,
        trackingCache,
        loadPermanentCache,  // 如果需要在其他地方重新加载缓存
        formatTrackingStatus,  // 导出格式化方法以供组件使用
        updateProjectDefinition,
        deleteProjectDefinition,
        addProjectDefinition,  // 导出新增的方法
        transformProductData,
        
    }
})
