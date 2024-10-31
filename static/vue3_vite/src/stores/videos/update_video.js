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
    let res = [];

    await dbHelper.openDatabase();
    const videoTable = await dbHelper.getAllData("videoTable");
    // 遍历 videoTable 中的每一行
    videoTable.forEach((row) => {
      // 检查当前行的 parentId 是否与 queryId.value 匹配
      if (row["parentId"] === queryId.value) {
        // 将其他字段添加到 returnRes 对象中
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

        // 将 "品牌"、"项目" 和 "产品" 的值拼接成一个数组，并添加到 res 数组中
        res.push([row["品牌"], row["项目"], row["产品"]]);
      }
    });

    // 将 res 数组赋值给 returnRes 的 "产品" 字段
    returnRes["产品"] = res;

    // 返回最终结果对象
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
    const videoTable = await dbHelper.getAllData("videoTable");
    const logistics = await dbHelper.getAllData("logistics");
    const influencerTable = await dbHelper.getAllData("influencerTable");
    const logisticsMap = new Map(
      logistics.map((info) => [info.订单号, info.物流状态_中文])
    );
    const influencerMap = new Map(
      influencerTable.map((info) => [info.红人名称, info])
    );

    videoTable.forEach((row) => {
      if (row.物流单号) {
        const trackingNumbersByParam = extractTrackingNumbersByParam(
          row.物流单号
        );
        let stat = "";
        trackingNumbersByParam.forEach((number) => {
          const logisticsStatus = logisticsMap.get(number);
          if (logisticsStatus) {
            stat += `${number}: ${logisticsStatus}\n`;
          }
        });
        row.物流进度 = stat;
      }
      if (row.红人全称) {
        const influencerInfo = influencerMap.get(row.红人全称);
        if (influencerInfo) {
          row.平台 = influencerInfo.平台;
          row["主页视频"] = influencerInfo.红人主页地址;
        }
      }
    });

    return videoTable;
  };

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
