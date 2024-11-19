import {defineStore} from "pinia";
import {ref} from "vue";
import {useDbStore} from "@/stores/init";
import {initVideoData} from "@/stores/init.js";

export const updateVideoData = defineStore("updateVideoData", () => {
  const initVideo = initVideoData();
  const dbHelper = useDbStore().dbHelper;
  const videobrand = ref([]);
  const videoProjectName = ref([]);
  const productOptions = ref([]);
  const videoUniqueIdList = ref([]);
  const videoInfluencerNameList = ref([]);
  const videoManager = ref([]);
  const videoType = ref([]);
  const productHierarchicalData = ref([]);
  const parentAndChildrenMapping = ref({});
  const parametricIndicatorsId = ref();
  const influencerTableName = ref();

  /**
   * 初始化下拉框的数据
   * */
  const initializeDropdownsData = async function initializeDropdowns() {
    try {
      await dbHelper.openDatabase();
      // 获取 parametricIndicators 表的数据
      const parametricIndicators = await dbHelper.getAllData(
        "parametricIndicators"
      );
      const influencerTable = await dbHelper.getAllData("influencerTable");
      const videoTable = await dbHelper.getAllData("videoTable");
      // 提取唯一的品牌、项目和产品
      const uniqueBrands = new Set();
      const uniqueProjects = new Set();
      const uniqueProducts = new Set();
      const uniqueUniqueIds = new Set();
      const uniqueInfluencerNames = new Set();
      const uniqueVideoManager = new Set();
      const uniqueType = new Set();
      const uniqueParametricIndicatorsId = new Set();
      const uniqueInfluencerTableName = new Set();
      // 初始化层级结构和品牌映射
      const hierarchicalData = [];

      parametricIndicators.forEach((row) => {
        if (row["id"]) {
          uniqueParametricIndicatorsId.add(row["id"]);
        }
        if (row["品牌"]) {
          uniqueBrands.add(row["品牌"]);
        }
        if (row["项目"]) {
          uniqueProjects.add(row["项目"]);
        }
        if (row["产品"]) {
          uniqueProducts.add(row["产品"]);
        }
      });

      const brandMap = new Map();
      const parentAndChildrenMap = new Map();

      parametricIndicators.forEach((row) => {
        const brand = row["品牌"];
        const project = row["项目"];
        const product = row["产品"];

        if (!brand) return; // 如果没有品牌信息，则跳过

        // 如果list里面存在有某个指定的值，说明重复
        const xx = hierarchicalData.some(
          (curBrand) => curBrand.value === brand
        );
        // 处理品牌
        if (!brandMap.has(brand) && !xx) {
          const brandObj = { value: brand, label: brand, children: [] };
          brandMap.set(brand, brandObj);
          hierarchicalData.push(brandObj);
        }

        const brandObj = brandMap.get(brand);

        if (project) {
          // 使用一个内部的 Map 来存储项目，避免品牌下重复项目
          if (!brandObj.projectMap) {
            brandObj.projectMap = new Map();
          }

          if (!brandObj.projectMap.has(project)) {
            const projectObj = { value: project, label: project, children: [] };
            brandObj.children.push(projectObj);
            brandObj.projectMap.set(project, projectObj);
          }

          const projectObj = brandObj.projectMap.get(project);

          if (product) {
            // 检查产品是否已存在于项目下
            const productExists = projectObj.children.some(
              (p) => p.value === product
            );
            if (!productExists) {
              projectObj.children.push({ value: product, label: product });
            }
          }
        }
      });

      // 移除临时的 projectMap 属性
      hierarchicalData.forEach((brand) => {
        delete brand.projectMap;
      });
      influencerTable.sort((a, b) => b.id - a.id);
      influencerTable.forEach((row) => {
        if (row["红人全名"]) {
          uniqueInfluencerTableName.add(row["红人全名"]);
        }
      });

      videoTable.forEach((row) => {
        if (row["parentId"]) {
          const parentId = row["parentId"];
          // 拼接 "品牌"、"项目" 和 "产品" 的值，并去掉所有空格
          const concatenated = row["品牌"] + row["项目"] + row["产品"];
          const sanitized = concatenated.replace(/\s+/g, "");
          const obj = {};
          obj[sanitized] = row["id"];

          if (!parentAndChildrenMap[parentId]) {
            parentAndChildrenMap[parentId] = [];
          }
          parentAndChildrenMap[parentId].push(obj);

          uniqueUniqueIds.add(row["parentId"]);
        }
        if (row["红人名称"]) {
          uniqueInfluencerNames.add(row["红人名称"]);
          // uniqueInfluencerTableName.add(row["红人名称"]);
        }
        if (row["负责人"]) {
          uniqueVideoManager.add(row["负责人"]);
        }
        if (row["类型"]) {
          uniqueType.add(row["类型"]);
        }
      });

      let uniqueUniqueIdsSort = Array.from(uniqueUniqueIds).sort(
        (a, b) => b - a
      );

      let uniqueParametricIndicatorsIdSort = Array.from(
        uniqueParametricIndicatorsId
      ).sort((a, b) => b - a);

      videobrand.value = Array.from(uniqueBrands);
      videoProjectName.value = Array.from(uniqueProjects);
      productOptions.value = Array.from(uniqueProducts);
      videoUniqueIdList.value = uniqueUniqueIdsSort;
      videoInfluencerNameList.value = Array.from(uniqueInfluencerNames);
      videoManager.value = Array.from(uniqueVideoManager);
      videoType.value = Array.from(uniqueType);
      influencerTableName.value = Array.from(uniqueInfluencerTableName);
      parametricIndicatorsId.value = uniqueParametricIndicatorsIdSort;
      productHierarchicalData.value = hierarchicalData;
      parentAndChildrenMapping.value = parentAndChildrenMap;
    } catch (error) {
      console.error("初始化下拉列表时出错：", error);
    }
  };

  const selectDataById = async function selectDataByIdFunction(queryId) {
    let returnRes = {};
    const key = queryId.value === undefined ? queryId : queryId.value;
    await dbHelper.openDatabase();
    const videoTable = await dbHelper.getAllData("videoTable");

    for (let row of videoTable) {
      if (row["parentId"] === Number.parseInt(key)) {
        returnRes["parentId"] = row["parentId"];
        returnRes["合作进度"] = row["合作进度"];
        returnRes["类型"] = row["类型"];
        returnRes["币种"] = row["币种"];
        returnRes["负责人"] = row["负责人"];
        returnRes["红人名称"] = row["红人名称"];
        returnRes["视频链接"] = row["视频链接"];
        returnRes["物流单号"] = row["物流单号"];
        returnRes["花费"] = row["花费"];
        returnRes["预估观看量"] = row["预估观看量"];
        returnRes["产品"] = [row["品牌"], row["项目"], row["产品"]];
        // 找到第一个匹配的结果后立即返回
        return returnRes;
      }
    }

    // 如果没有找到匹配结果，返回空对象或其他默认值
    return returnRes;
  };

  function extractTrackingNumbersByParam(url) {
    // 去除 URL 中的所有空格
    const cleanedUrl = url.replace(/\s+/g, "");
    const regex = /nums=([A-Z0-9,]+)/;
    const match = cleanedUrl.match(regex);
    if (match && match[1]) {
      return match[1].split(",");
    }
    return [];
  }

  const gotTableData = async function tableDatas() {
    await dbHelper.openDatabase();
    await initVideo.initialize();

    // 并行获取数据，提高效率
    const [videoTable, logistics, influencerTable] = await Promise.all([
      dbHelper.getAllData("videoTable"),
      dbHelper.getAllData("logistics"),
      dbHelper.getAllData("influencerTable"),
    ]);

    // 创建物流状态映射表：订单号 -> 物流状态
    const logisticsMap = new Map(
      logistics.map((info) => [info.订单号, info.物流状态_中文])
    );

    // 创建红人信息映射表和平台-红人主页映射表
    const influencerMap = new Map(); // 红人名称/全名 -> 红人信息
    const platformNameToHomepageMap = new Map(); // 平台:红人名称/全名 -> 红人主页地址

    influencerTable.forEach((info) => {
      const platform = info["平台"].toLowerCase();
      const names = [info.红人全名, info.红人名称]
        .filter(Boolean)
        .map((name) => name.toLowerCase());

      names.forEach((nameKey) => {
        // 将红人名称和全名映射到红人信息
        influencerMap.set(nameKey, info);

        // 构建平台和红人名称的组合键，映射到红人主页地址
        const platformMapKey = `${platform}:${nameKey}`;
        platformNameToHomepageMap.set(platformMapKey, info.红人主页地址);
      });
    });

    // 处理视频表数据
    videoTable.forEach((row) => {
      // 处理物流进度
      if (row.物流单号) {
        const trackingNumbers = extractTrackingNumbersByParam(row.物流单号);
        const statuses = trackingNumbers
          .map((number) => {
            const status = logisticsMap.get(number);
            return status ? `${number}: ${status}` : null;
          })
          .filter(Boolean)
          .join("\n");
        row.物流进度 = statuses;
      }
      if (row.参与率){
        row.参与率 = row.参与率.toLocaleString('zh-CN', {
          style: 'percent',
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
      }
      // 处理红人信息
      if (row.红人名称 || row.红人全称) {
        const nameKeys = [
          row.红人名称 ? row.红人名称.toLowerCase() : null,
          row.红人全称 ? row.红人全称.toLowerCase() : null,
        ].filter(Boolean);

        // 查找红人信息，优先使用红人名称
        let influencerInfo = null;
        for (const nameKey of nameKeys) {
          influencerInfo = influencerMap.get(nameKey);
          if (influencerInfo) {
            break;
          }
        }

        if (influencerInfo) {
          // 确定平台
          let platform = row["平台"]
            ? row["平台"].toLowerCase()
            : influencerInfo["平台"].toLowerCase();

          if (!platform && influencerInfo.红人主页地址) {
            platform = findPlatform(influencerInfo.红人主页地址);
            row["平台"] = platform;
          }

          // 获取红人主页视频链接
          let homepage = null;
          for (const nameKey of nameKeys) {
            const platformMapKey = `${platform}:${nameKey}`;
            homepage = platformNameToHomepageMap.get(platformMapKey);
            if (homepage) {
              break;
            }
          }

          // 设置主页视频链接
          row["主页视频"] = homepage || influencerInfo.红人主页地址;
          // 如果平台信息缺失，尝试从主页地址中提取
          if (!row["平台"] && influencerInfo.红人主页地址) {
            row["平台"] = findPlatform(influencerInfo.红人主页地址);
          }
        }
      }
    });

    return videoTable;
  };

  function findPlatform(link) {
    if (link.includes("instagram")) {
      return "instagram";
    } else if (link.includes("youtube")) {
      return "youtube";
    } else if (link.includes("tiktok")) {
      return "tiktok";
    } else if (link.includes("x.com")) {
      return "x";
    } else {
      return "未定义判断";
    }
  }

  const gotMeirtcsData = async function gotMeirtcsDataFunction() {
    await dbHelper.openDatabase();
    const parametricIndicators = await dbHelper.getAllData(
      "parametricIndicators"
    );
    return parametricIndicators;
  };

  // 需要的子字符串列表
  const excludedSubstrings = [
    "/reel/",
    "/video/",
    "/watch/",
    "/video?",
    "/watch?",
    "/reel?",
    "/p/",
    "/p?",
    "/shorts/",
    "/shorts?",
    "/status/",
    "https://youtu.be/",
  ];

  const checkLink = function checkLinkFunction(link) {
    const isValidUrl =
      /^(https?:\/\/)?([\w-]+\.)+[\w-]+(\/[\w-./?%&=]*)?$/.test(link);

    const containsExcluded = excludedSubstrings.some((substring) =>
      link.includes(substring)
    );
    console.log("isValidUrl", isValidUrl, "containsExcluded", containsExcluded);
    return isValidUrl || containsExcluded;
  };

  const checkLogisticsNumber = function checkLogisticsNumberFunction(number) {
    const pattern = /https:\/\/t\.17track\.net\/zh-cn#nums=/;
    const isLogisticsNumber = pattern.test(number);
    return isLogisticsNumber;
  };

  return {
    videobrand,
    videoProjectName,
    productOptions,
    videoUniqueIdList,
    videoInfluencerNameList,
    videoManager,
    videoType,
    productHierarchicalData,
    parentAndChildrenMapping,
    parametricIndicatorsId,
    influencerTableName,

    initializeDropdownsData,
    selectDataById,
    gotTableData,
    checkLink,
    checkLogisticsNumber,
    gotMeirtcsData,
  };
});
