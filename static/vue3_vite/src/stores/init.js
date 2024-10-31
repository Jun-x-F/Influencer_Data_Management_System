import {defineStore} from "pinia";
import {ref} from "vue";
import IndexedDBHelper from "@/stores/innodb_tools"; // 导入路径根据您的项目结构调整

const index_url = "http://172.16.11.245:5000";
// 初始化数据表要求
const dbName = "videoDatabase";
const dbVersion = 5;
const storeSchemas = {
  // 红人表
  influencerTable: {
    keyPath: "id",
    autoIncrement: false,
    indexes: ["id"],
  },
  // 视频表
  videoTable: {
    keyPath: "id",
    autoIncrement: false,
    indexes: ["id"],
  },
  // 指标参数
  parametricIndicators: {
    keyPath: "id",
    autoIncrement: false,
    indexes: ["id"],
  },
  // 负责人
  manager: {
    keyPath: "负责人",
    autoIncrement: false,
    indexes: ["负责人"],
  },
  // 物流
  logistics: {
    keyPath: "id",
    autoIncrement: true,
    indexes: ["id"],
  },
};
const dbHelper = new IndexedDBHelper(dbName, dbVersion, storeSchemas);

export const useDbStore = defineStore("db", () => {
  return {
    dbHelper,
  };
});

export const initVideoData = defineStore("initVideoData", () => {
  // 状态变量
  const videos = ref([]);
  const parametricIndicators = ref([]);
  const managers = ref([]);
  const influencers = ref([]);
  const logistics = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // // 通用的获取和缓存数据函数
  // const fetchAndCache = async (endpoint, storeName, _method='GET') => {
  //     try {
  //         const response = await fetch(endpoint, { method: _method });
  //         if (!response.ok) {
  //             throw new Error(`请求失败: ${response.status}`);
  //         }
  //         const data = await response.json();
  //         await dbHelper.clearStore(storeName);
  //         await dbHelper.addOrUpdateDataBatch(storeName, data);
  //         return data;
  //     } catch (err) {
  //         console.error(`获取和缓存 ${storeName} 数据时出错:`, err);
  //         throw err;
  //     }
  // };

  // 通用的获取和缓存数据函数
  const fetchAndCache = async (
    endpoint,
    storeName,
    method = "GET",
    body = null
  ) => {
    try {
      // 构建请求选项
      const options = {
        method,
        headers: {
          // 默认添加 Accept 头，期望接收 JSON 数据
          Accept: "application/json",
        },
      };

      // 如果请求方法是 POST 或 PUT，并且有请求体
      if ((method === "POST" || method === "PUT") && body) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
      }

      // 发起请求
      const response = await fetch(endpoint, options);

      // 检查响应状态
      if (!response.ok) {
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
      }

      // 解析 JSON 数据
      const data = await response.json();

      // 清空并更新 IndexedDB 存储
      await dbHelper.clearStore(storeName);
      await dbHelper.addOrUpdateDataBatch(storeName, data);

      return data;
    } catch (err) {
      console.error(`获取和缓存 ${storeName} 数据时出错:`, err);
      throw err;
    }
  };

  const fetchData = async (endpoint, method = "GET", body = null) => {
    try {
      // 构建请求选项
      const options = {
        method,
        headers: {
          // 默认添加 Accept 头，期望接收 JSON 数据
          Accept: "application/json",
        },
      };

      // 如果请求方法是 POST 或 PUT，并且有请求体
      if ((method === "POST" || method === "PUT") && body) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
      }

      // 发起请求
      const send_url = index_url + endpoint;
      const response = await fetch(send_url, options);

      // 检查响应状态
      if (!response.ok) {
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
      }

      // 解析 JSON 数据
      const data = await response.json();

      return data;
    } catch (err) {
      console.error(`获取数据时出错:`, err);
      throw err;
    }
  };

  // 初始化数据库并加载所有数据
  const initialize = async () => {
    loading.value = true;
    error.value = null;

    try {
      await dbHelper.openDatabase();

      // 定义所有需要初始化的数据
      const initialDataRequests = [
        {
          endpoint: index_url + "/video/get_video_data",
          storeName: "videoTable",
          stateVar: videos,
        },
        {
          endpoint: index_url + "/video/get_metrics_all",
          storeName: "parametricIndicators",
          stateVar: parametricIndicators,
        },
        {
          endpoint: index_url + "/video/get_manager_all",
          storeName: "manager",
          stateVar: managers,
        },
        {
          endpoint: index_url + "/video/get_logistics_all",
          storeName: "logistics",
          stateVar: logistics,
        },
        {
          endpoint: index_url + "/video/api/user/get_data",
          storeName: "influencerTable",
          stateVar: influencers,
        },
      ];

      // 逐个请求并缓存数据
      for (const {
        endpoint,
        storeName,
        stateVar,
        _method,
      } of initialDataRequests) {
        const data = await fetchAndCache(endpoint, storeName, _method);
        stateVar.value = data;
      }
    } catch (err) {
      console.error("初始化视频数据时出错:", err);
      error.value = "初始化数据失败";
    } finally {
      loading.value = false;
    }
  };

  // 更新视频表
  const updateVideoTable = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchAndCache(
        index_url + "/video/get_video_data",
        "videoTable"
      );
      videos.value = data;
    } catch (err) {
      error.value = "更新视频表失败";
    } finally {
      loading.value = false;
    }
  };

  // 更新项目指标
  const updateProjectMetrics = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchAndCache(
        index_url + "/video/get_metrics_all",
        "parametricIndicators"
      );
      parametricIndicators.value = data;
    } catch (err) {
      error.value = "更新项目指标失败";
    } finally {
      loading.value = false;
    }
  };

  // 更新项目负责人
  const updateProjectManager = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchAndCache(
        index_url + "/video/get_manager_all",
        "manager"
      );
      managers.value = data;
    } catch (err) {
      error.value = "更新项目负责人失败";
    } finally {
      loading.value = false;
    }
  };

  // 更新物流信息失败
  const updatelogistics = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchAndCache(
        index_url + "/video/get_logistics_all",
        "logistics"
      );
      logistics.value = data;
    } catch (err) {
      error.value = "更新物流信息失败";
    } finally {
      loading.value = false;
    }
  };

  // 更新物流信息失败
  const updateInfluencerTable = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchAndCache(
        index_url + "/video/api/user/get_data",
        "influencerTable"
      );
      logistics.value = data;
    } catch (err) {
      error.value = "更新红人信息失败";
    } finally {
      loading.value = false;
    }
  };

  return {
    // 状态
    videos,
    parametricIndicators,
    managers,
    influencers,
    logistics,
    loading,
    error,

    // 动作
    initialize,
    updateVideoTable,
    updateProjectMetrics,
    updateProjectManager,
    updatelogistics,
    fetchAndCache,
    fetchData,
    updateInfluencerTable,
  };
});
