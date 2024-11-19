<template>
  <div class="form-column">
    <h2>项目与视频板块</h2>
    <form id="videoForm" autocomplete="off">
      <div id="linkFieldsContainer">
        <div class="linkFields">
          <div class="form-row">
            <AutocompleteInput v-model="selectedValue" :placeholder="'请输入视频唯一ID'"
              :dataList="updateVideo.videoUniqueIdList" label="唯一Id" required @select="handleItemSelect"
              :wrapperClass="validationStatus.selectedValue" ref="tips1" />
            <!-- <Multiselect /> -->
            <CascaderSelector v-model="selectedProduct" :placeholder="'请输入产品'"
              :options="updateVideo.productHierarchicalData" :cascaderProps="cascaderProps" label="品牌-项目-产品"
              :wrapperClass="validationStatus.selectedProduct" @select="handleItemSelect"
              :dynamicMarginTop="dynamicMarginTop" tagsWith="415px" required ref="tips2" />
            <AutocompleteInput v-model="selectManager" :placeholder="'请选择一个负责人'" :dataList="updateVideo.videoManager"
              label="负责人:" required @select="handleItemSelect" :wrapperClass="validationStatus.selectManager" />
            <AutocompleteInput v-model="selectInfluencer" :placeholder="'选择或输入红人名称'"
              :dataList="updateVideo.videoInfluencerNameList" label="红人名称:" required @select="handleItemSelect"
              :wrapperClass="validationStatus.selectInfluencer" />
          </div>

          <div class="form-row">
            <CustomInput v-model="videoLinks" label="视频链接:" :placeholder="'请输入视频链接'"
              :wrapperClass="validationStatus.videoLinks" ref="tips3" />
            <AutocompleteInput v-model="videoProgress" :placeholder="'请输入合作进度'" :dataList="videoProgressList"
              label="合作进度:" required @select="handleItemSelect" :wrapperClass="validationStatus.videoProgress" />
            <CustomInput v-model="videoLogisticsNumber" label="物流链接:" :placeholder="'请输入物流链接'"
              :wrapperClass="validationStatus.videoLogisticsNumber" ref="tips4" />
            <AutocompleteInput v-model="videoType" :placeholder="'请选择一个类型'" :dataList="updateVideo.videoType"
              label="类型:" @select="handleItemSelect" :wrapperClass="validationStatus.videoType" />
          </div>

          <div class="form-row">
            <CustomInput v-model="videocost" label="花费:" :placeholder="'请输入花费'" type="number"
              :wrapperClass="validationStatus.videocost" />
            <div>
              <label for="videocurrency" :class="{ 'invalid-label': validationStatus.videocurrency }">币种:</label>
              <select id="videocurrency" class="videocurrency" v-model="videocurrency">
                <option value="">选择币种</option>
                <option value="USD">USD - 美元</option>
                <option value="EUR">EUR - 欧元</option>
                <option value="CNY">CNY - 人民币</option>
                <option value="JPY">JPY - 日元</option>
                <option value="GBP">GBP - 英镑</option>
                <option value="AUD">AUD - 澳元</option>
                <option value="CAD">CAD - 加元</option>
              </select>
            </div>
            <CustomInput v-model="videoestimatedLaunchDate" label="预估上线时间:" :placeholder="'预估上线时间'" type="date"
              :wrapperClass="validationStatus.videoestimatedLaunchDate" />
            <CustomInput v-model="videoestimatedViews" label="预估观看量:" :placeholder="'预估观看量'" type="number"
              :wrapperClass="validationStatus.videoestimatedViews" />
          </div>
        </div>
      </div>

      <div style="position: relative; width: 100%">
        <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;margin-top: 10px;">
          <!-- <button type="submit" class="btn-primary">提交视频</button> -->
          <CascaderSubmit @update="updateData" ref="tips5" />
          <AlterMessage :loading="loading" v-model:modelValue="isDialogVisible" title="Tips"
            :errorMessage="errorMessage" width="500px" />

          <CascaderReset @reset="handleReset" ref="tips6" />
          <cascaderTimestamp ref="tips7" />
          <el-button type="info" @click="openTips = true" style="margin-left: 15px;">提示</el-button>
          <CascaderDelete @click="deleteData" ref="tips8" />

        </div>
      </div>
      <el-tour v-model="openTips">
        <el-tour-step :target="tips1?.$el" title="唯一Id">
          <span>
            1. 更新或者是删除数据的时候，必须要有它！！！
          </span><br />
          <span>
            2. 新增数据需要到新增板块！！！
          </span>
        </el-tour-step>
        <el-tour-step :target="tips2?.$el" title="品牌-项目-产品">
          <span>
            1. 支持多选
          </span><br />
          <span>
            2. 新增的时候可以直接添加
          </span><br />
          <span>
            3. 取消多余的产品的时候，直接在这里操作即可
          </span>
        </el-tour-step>
        <el-tour-step :target="tips3?.$el" title="视频链接" description="这里的视频链接有格式要求！相同的视频链接不会重复爬取，默认每2天自动更新数据" />
        <el-tour-step :target="tips4?.$el" title="物流链接" description="仅支持17track网站，每半天更新一次" />
        <el-tour-step :target="tips5?.$el" title="提交更新" description="更新数据" />
        <el-tour-step :target="tips6?.$el" title="重置" description="这里会重新加载所有数据，可以选择刷新页面，或者是点击这里" />
        <el-tour-step :target="tips7?.$el" title="查看任务情况"
          description="每个用户都会有默认的识别码，会绑定近6个小时的物流爬取情况和视频爬取情况，默认根据时间倒序排序" />
        <el-tour-step :target="tips8?.$el" title="删除" description="根据id进行删除" />
      </el-tour>

      <!-- 用于显示提交结果的元素 -->
      <!-- <div id="responseMessageVideo" class="response-message"> -->

      <!-- </div> -->
    </form>
  </div>
</template>
<script setup>

import {defineEmits, onMounted, reactive, ref, watch} from 'vue';
import {updateVideoData} from '@/stores/videos/update_video.js';
import {useUserStore} from '@/stores/userInfo.js';
import AutocompleteInput from '@/components/tables_element/AutocompleteInput.vue';
import CascaderSelector from '@/components/tables_element/CascaderSelector.vue';
import CustomInput from '@/components/tables_element/CustomInput.vue';
import CascaderReset from '@/components/tables_element/CascaderReset.vue';
import CascaderSubmit from '@/components/tables_element/CascaderSubmit.vue';
import CascaderDelete from '@/components/tables_element/CascaderDelete.vue';
import AlterMessage from '@/components/tables_element/AlterMessage.vue';
import cascaderTimestamp from '@/components/tables_element/cascaderTimestamp.vue';
import {initVideoData} from '@/stores/init.js';
import {useNotice} from '@/stores/notice.js';

const updateVideo = updateVideoData();
// 自动化装载用户id
const useUser = useUserStore();
const initVideo = initVideoData();
const notice = useNotice();

let debounceTimeout = null;
const videoProgress = ref('');
const videoType = ref('');
const videocurrency = ref('');
const selectedItem = ref('');
const selectedValue = ref('');
const selectedProduct = ref([]);
const selectManager = ref('');
const selectInfluencer = ref('');
const videoLinks = ref('');
const videoLogisticsNumber = ref('');
const videocost = ref('');
const videoestimatedViews = ref('');
const videoestimatedLaunchDate = ref('');
const isDialogVisible = ref(false);
const isClickId = ref(false);
const errorMessage = ref('');
const loading = ref(false);
const openTips = ref(false);
const tips1 = ref()
const tips2 = ref()
const tips3 = ref()
const tips4 = ref()
const tips5 = ref()
const tips6 = ref()
const tips7 = ref()
const tips8 = ref()
const closeInit = ref(false);
const dynamicMarginTop = ref('-10%');
// 定义验证状态对象
const validationStatus = reactive({
  videoProgress: false,
  videoType: false,
  videocurrency: false,
  selectedItem: false,
  selectedValue: false,
  selectedProduct: false,
  selectManager: false,
  selectInfluencer: false,
  videoLinks: false,
  videoLogisticsNumber: false,
  videocost: false,
  videoestimatedViews: false,
  videoestimatedLaunchDate: false,
});

const cascaderProps = {
  multiple: true,
  emitPath: true,
};
let videoProgressList = ['进行中', '合作完成', '合作失败'];

// 处理选择的项
const handleItemSelect = async (item) => {
  console.log('用户选择了：', item);
  if (item.name === "唯一Id") {
    loading.value = true;
    // console.log("updateVideo.selectDataById(item.value)", item.value);
    // 判断状态是否改变
    const result = await updateVideo.selectDataById(item.value)
    if (result.parentId !== ""){
      notice.setParentIdData(result.parentId);
      selectedValue.value = result.parentId;
      videoProgress.value = result.合作进度;
      videoType.value = result.类型;
      videocurrency.value = result.币种;
      selectedProduct.value = result.产品;
      selectManager.value = result.负责人;
      selectInfluencer.value = result.红人名称;
      videoLinks.value = result.视频链接;
      videoLogisticsNumber.value = result.物流单号;
      videocost.value = result.花费;
      videoestimatedViews.value = result.预估观看量;
      videoestimatedLaunchDate.value = result.预估上线时间;
      await checkItemData();

      isClickId.value = true;
    }
    loading.value = false;
  }
};


// 定义 emit 方法
const emit = defineEmits(['change_Id', 'change_product', 'reset']);

watch(selectedValue, async (newValue) => {
  // console.log('用户输入selectedValue id的值发生了变化：', newValue);
  // const selectRes = updateVideo.selectDataById(newValue);
  // console.log('用户的值为', selectRes);
  // 清除之前的定时器
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }
  // 在这里执行您需要的逻辑，例如验证输入、发送请求等
  if (newValue === '' && notice.choseParentId !== null) {
    closeInit.value = true;
    await reset();
  } else {
    // 启动一个新的定时器，2 秒后执行
    debounceTimeout = setTimeout( async () => {
      await handleItemSelect({name:"唯一Id", value:newValue});
    }, 1000); // 2000 毫秒，即 2 秒
  }
});

watch(() => notice.isUpdateData, async (newValue, oldValue) => {
  // console.log("notice.isUpdateData", notice.isUpdateData);
  if (newValue === true) {
    await reset();
    await notice.setIsUpdateData(false);
  }
})

watch(selectManager, (newValue, oldValue) => {
  // console.log('selectManager', newValue);
  // 在这里执行您需要的逻辑，例如验证输入、发送请求等
  notice.setManagerData(newValue);
});

watch(selectedProduct, (newValue, oldValue) => {
  // console.log('selectedProduct', newValue);
  // 在这里执行您需要的逻辑，例如验证输入、发送请求等
  notice.setProductData(newValue);
});

const reset = async () => {
  videoProgress.value = '';
  videoType.value = '';
  videocurrency.value = '';
  selectedItem.value = '';
  selectedValue.value = '';
  selectedProduct.value = [];
  selectManager.value = '';
  selectInfluencer.value = '';
  videoLinks.value = '';
  videoLogisticsNumber.value = '';
  videocost.value = '';
  videoestimatedViews.value = '';
  videoestimatedLaunchDate.value = '';

  // 重新初始化状态
  Object.assign(validationStatus, {
    videoProgress: false,
    videoType: false,
    videocurrency: false,
    selectedItem: false,
    selectedValue: false,
    selectedProduct: false,
    selectManager: false,
    selectInfluencer: false,
    videoLinks: false,
    videoLogisticsNumber: false,
    videocost: false,
    videoestimatedViews: false,
    videoestimatedLaunchDate: false,
  });
  if (closeInit.value === false) {
    await initVideo.initialize();
  }
  await updateVideo.initializeDropdownsData();
  notice.setIsResetData(true);
  closeInit.value = false;

  console.log('已重置');
}

// 定义重置函数
async function handleReset() {
  await reset();
}

async function deleteData() {
  isDialogVisible.value = true;
  loading.value = true;
  // console.log("isClickId", isClickId);
  if (selectedValue.value === "" || isClickId.value === false) {
    errorMessage.value = "请选择已有的ID, 目前输入的唯一ID为 " + selectedValue.value;
    loading.value = false;
    return;
  }
  const toRequestData = {
    "uid": useUser.userUUID,
    "parentId": selectedValue.value
  }
  const fetchInfo = await initVideo.fetchData("/video/api/delete_data", "POST", toRequestData);
  if (fetchInfo.success !== true) {
    errorMessage.value = fetchInfo.message
  } else {
    errorMessage.value = "成功"
  }
  loading.value = false;
  await reset();
};

// 更新数据
async function updateData() {
  isDialogVisible.value = true;
  loading.value = true;
  // console.log("isClickId", isClickId);
  if (selectedValue.value === "" || isClickId.value === false) {
    errorMessage.value = "请选择已有的ID, 目前输入的唯一ID为 " + selectedValue.value;
    loading.value = false;
    return;
  }
  // console.log("Update videoLinks.value", videoLinks.value);
  if (videoLinks.value !== "" && videoLinks.value !== null) {
    const res = updateVideo.checkLink(videoLinks.value);

    if (res === false) {
      errorMessage.value = videoLinks.value + " - 不是有效的视频链接";
      loading.value = false;
      return;
    }
  }

  if (videoLogisticsNumber.value !== "" && videoLogisticsNumber.value !== null) {

    const videoLogisticsNumberRes = updateVideo.checkLogisticsNumber(videoLogisticsNumber.value);
    if (videoLogisticsNumberRes === false) {
      errorMessage.value = videoLogisticsNumber.value + " - 这不是有效的物流链接";
      loading.value = false;
      return;
    }
  }

  const keys = ['brand', 'project', 'product'];

  const arrayOfObjects = [];
  selectedProduct.value.forEach(subArray => {
    const obj = {};
    const childrenList = updateVideo.parentAndChildrenMapping[selectedValue.value];

    const concatenated = subArray.join('').replace(/\s+/g, '');
    keys.forEach((key, index) => {
      obj[key] = subArray[index];

    });
    obj["id"] = null;
    childrenList.forEach(cur => {
      const findId = cur[concatenated];
      if (findId && findId !== "") {
        obj["id"] = findId;
      }
    });
    obj["parentId"] = selectedValue.value;
    obj["type"] = videoType.value;
    obj["head"] = selectManager.value;
    obj["full_name"] = selectInfluencer.value;
    obj["video_url"] = videoLinks.value;
    obj["currency"] = videocurrency.value;
    obj["trackingNumber"] = videoLogisticsNumber.value;
    obj["cost"] = videocost.value;
    obj["estimatedGoLiveTime"] = videoestimatedLaunchDate.value;
    obj["estimatedViews"] = videoestimatedViews.value;
    obj["progressCooperation"] = videoProgress.value;
    arrayOfObjects.push(obj);
  });


  const toRequestData = {
    "uid": useUser.userUUID,
    "data": arrayOfObjects,
    "parentId": selectedValue.value
  }

  // console.log("toRequestData", toRequestData);

  const fetchInfo = await initVideo.fetchData("/video/api/update_data", "POST", toRequestData);
  // console.log(fetchInfo);
  if (fetchInfo.success !== true) {
    errorMessage.value = fetchInfo.message
  } else {
    errorMessage.value = "成功"
  }
  loading.value = false;
  await reset();

};

const checkItemData = async () => {
  validationStatus.videoProgress = !videoProgress.value;
  validationStatus.videoType = !videoType.value;
  validationStatus.videocurrency = !videocurrency.value;
  validationStatus.selectedItem = !selectedItem.value;
  validationStatus.selectedValue = !selectedValue.value;
  validationStatus.selectedProduct = !selectedProduct.value || selectedProduct.value.length === 0;
  validationStatus.selectManager = !selectManager.value;
  validationStatus.selectInfluencer = !selectInfluencer.value;
  validationStatus.videoLinks = !videoLinks.value;
  validationStatus.videoLogisticsNumber = !videoLogisticsNumber.value;
  validationStatus.videocost = !videocost.value;
  validationStatus.videoestimatedViews = !videoestimatedViews.value;
  validationStatus.videoestimatedLaunchDate = !videoestimatedLaunchDate.value;
};

// 初始化数据
onMounted(async () => {
  await updateVideo.initializeDropdownsData();
  console.log(useUser.userUUID);
});
</script>
<style scoped>
body {
  margin: 0;
}

.example-showcase .el-loading-mask {
  z-index: 9;
}
</style>
