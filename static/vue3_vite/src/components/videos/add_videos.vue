<template>
  <div>
    <div class="addVideoDiv">
      <el-affix target=".addVideoDiv" :offset="20">
        <el-button type="warning" @click="drawer = true">新增视频</el-button>
      </el-affix>
    </div>
    <el-drawer v-model="drawer" title="新增任务" :with-header="false" size="60%" @close="handleClose">
      <el-form ref="ruleFormRef" :model="form" label-width="auto" size="large" label-position="left" :inline="true"
        :rules="rules">
        <el-form-item label="品牌-项目-产品" prop="selectedProduct">
          <CascaderSelector v-loading="loading" v-model="form.selectedProduct" :placeholder="'请输入产品'"
            :options="updateVideo.productHierarchicalData" :cascaderProps="cascaderProps"
            :dynamicMarginTop="dynamicMarginTop" tagsWith="440px" />
        </el-form-item>
        <el-form-item label="红人名称:" prop="selectInfluencer">
          <CustomInput v-model="form.selectInfluencer" label="" :placeholder="'请输入红人名称'" type="text"
            :wrapperClass="validationStatus.videocost" />
        </el-form-item>
        <el-form-item label="负责人:" prop="selectManager">
          <AutocompleteInput v-model="form.selectManager" :placeholder="'请选择一个负责人'" :dataList="updateVideo.videoManager"
            @select="handleItemSelect" :wrapperClass="validationStatus.selectManager" />
        </el-form-item>
        <el-form-item label="币种:" prop="videocurrency">
          <!-- <label for="videocurrency" :class="{ 'invalid-label': validationStatus.videocurrency }">币种:</label> -->
          <select id="videocurrency" class="videocurrency" v-model="form.videocurrency" style="width: 220px;">

            <option value="">选择币种</option>
            <option value="USD">USD - 美元</option>
            <option value="EUR">EUR - 欧元</option>
            <option value="CNY">CNY - 人民币</option>
            <option value="JPY">JPY - 日元</option>
            <option value="GBP">GBP - 英镑</option>
            <option value="AUD">AUD - 澳元</option>
            <option value="CAD">CAD - 加元</option>
          </select>
        </el-form-item>
        <el-form-item label="花费:" prop="videocost">
          <CustomInput v-model="form.videocost" :placeholder="'请输入花费'" type="number"
            :wrapperClass="validationStatus.videocost" />
        </el-form-item>

        <el-form-item label="合作进度:" prop="videoProgress">
          <AutocompleteInput v-model="form.videoProgress" :placeholder="'请输入合作进度'" :dataList="videoProgressList"
            @select="handleItemSelect" :wrapperClass="validationStatus.videoProgress" />
        </el-form-item>
        <el-form-item label="视频链接:" prop="videoLinks">
          <CustomInput v-model="form.videoLinks" :placeholder="'请输入视频链接'" :wrapperClass="validationStatus.videoLinks" />
        </el-form-item>
        <el-form-item label="物流链接:" prop="videoLogisticsNumber">
          <CustomInput v-model="form.videoLogisticsNumber" :placeholder="'请输入物流链接'"
            :wrapperClass="validationStatus.videoLogisticsNumber" />
        </el-form-item>
        <el-form-item label="预估上线时间:" prop="videoestimatedLaunchDate">
          <CustomInput v-model="form.videoestimatedLaunchDate" :placeholder="'预估上线时间'" type="date"
            :wrapperClass="validationStatus.videoestimatedLaunchDate" />
        </el-form-item>
        <el-form-item label="预估观看量:" prop="videoestimatedViews">
          <CustomInput v-model="form.videoestimatedViews" :placeholder="'预估观看量'" type="number"
            :wrapperClass="validationStatus.videoestimatedViews" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)">创建</el-button>
          <el-button type="danger" @click="resetForm(ruleFormRef)">重置</el-button>
        </el-form-item>
      </el-form>
    </el-drawer>
    <AlterMessage :loading="loading" v-model:modelValue="isDialogVisible" title="提交视频" :errorMessage="errorMessage"
      width="500px" />
  </div>
</template>
<script setup>
import {onMounted, reactive, ref} from 'vue';
import CascaderSelector from '@/components/tables_element/CascaderSelector.vue';
import {initVideoData} from '@/stores/init.js';
import {updateVideoData} from '@/stores/videos/update_video.js';
import {useUserStore} from '@/stores/userInfo.js';
import AutocompleteInput from '@/components/tables_element/AutocompleteInput.vue';
import CustomInput from '@/components/tables_element/CustomInput.vue';
import AlterMessage from '@/components/tables_element/AlterMessage.vue';
import {useNotice} from '@/stores/notice.js';

const notice = useNotice();
const updateVideo = updateVideoData();
const useUser = useUserStore();
const initVideo = initVideoData();

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
const ruleFormRef = ref();
const isDialogVisible = ref(false);
const isClick = ref(false);
const errorMessage = ref('');
const loading = ref(false);
const dynamicMarginTop = ref('-6%');
const title = ref();
const cascaderProps = {
  multiple: true,
  emitPath: true,
};
let videoProgressList = ['进行中', '合作完成', '合作失败'];


const form = reactive({
  selectedProduct: [],
  selectInfluencer: '',
  selectManager: '',
  videocurrency: '',
  videocost: '',
  videoProgress: '',
  videoLinks: '',
  videoLogisticsNumber: '',
  videoestimatedLaunchDate: '',
  videoestimatedViews: '',
});

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
// import { addVideoData } from '@/stores/videos/add_video';
// import { initVideoData } from '@/stores/init';
const drawer = ref(false);

const rules = reactive({
  selectedProduct: [
    { required: true, message: '请选择品牌-项目-产品', trigger: 'change' },
  ],
  selectManager: [
    { required: true, message: '请选择一个负责人', trigger: 'change' },
  ],
  videoProgress: [
    { required: true, message: '请选择合作进度', trigger: 'change' },
  ],
  videoLogisticsNumber: [
    { validator: validateLogisticsLink, trigger: 'blur' },
  ],
  videoLinks: [
    { validator: validateVideoLink, trigger: 'blur' },
  ]
  ,
  videocost: [
    { validator: validateNumericOrEmpty, trigger: 'blur' },
  ]
  ,
  videoestimatedViews: [
    { validator: validateNumericOrEmpty, trigger: 'blur' },
  ]
})

// 校验物流链接
function validateLogisticsLink(rule, value, callback) {
  if (!value) {
    return callback(); // 允许为空，如果需要必填请修改
  }
  const pattern = /^https:\/\/t\.17track\.net\/zh-cn#nums=/;
  if (pattern.test(value)) {
    callback();
  } else {
    callback(new Error('物流链接必须以 https://t.17track.net/zh-cn#nums= 开头'));
  }
}

// 校验数字或为空
function validateNumericOrEmpty(rule, value, callback) {
  if (value === '' || value === null || value === undefined) {
    return callback();
  }
  if (!isNaN(value)) {
    return callback();
  }
  callback(new Error('请输入有效的数字'));
}

// 需要的子字符串列表
const excludedSubstrings = [
  '/reel/', '/video/', '/watch/',
  '/video?', '/watch?', '/reel?',
  '/p/', '/p?', '/shorts/', '/shorts?', '/status/', "https://youtu.be/"
];

// /video/check_url_existing

// 校验视频链接（预留方法）
async function validateVideoLink(rule, value, callback) {
  // 预留的自定义验证逻辑
  // 例如，你可以调用另一个方法或进行特定的验证
  // 目前暂时通过验证
  if (!value) {
    return callback(); // 允许为空，如果需要必填请修改
  }
  if (!excludedSubstrings.some(substring => value.includes(substring))) {
    callback(new Error('这个不是视频链接'));
  }
  const toRequestData = {
    "url": value
  }
  const fetchInfo = await initVideo.fetchData("/video/check_url_existing", "POST", toRequestData);
  if (fetchInfo.isSame === true) {
    callback(new Error('该视频链接已经存在'));
  }
  callback();
}


const submitForm = async (formEl) => {
  if (!formEl) return
  await formEl.validate(async (valid, fields) => {
    loading.value = true;
    isDialogVisible.value = true;
    // 通过校验之后....
    if (valid) {

      const data = [];
      form.selectedProduct.forEach((row) => {
        const obj = {}
        obj["brand"] = row[0]
        obj["project"] = row[1]
        obj["product"] = row[2]
        obj["head"] = selectManager.value;
        obj["full_name"] = selectInfluencer.value;
        obj["video_url"] = videoLinks.value;
        obj["currency"] = videocurrency.value;
        obj["trackingNumber"] = videoLogisticsNumber.value;
        obj["cost"] = videocost.value;
        obj["estimatedGoLiveTime"] = videoestimatedLaunchDate.value;
        obj["estimatedViews"] = videoestimatedViews.value;
        obj["progressCooperation"] = videoProgress.value;
        data.push(obj);
      });
      console.log('submit!', data);
      const toRequestData = {
        "uid": useUser.userUUID,
        "data": data
      }
      const fetchInfo = await initVideo.fetchData("/video/api/add_data", "POST", toRequestData);
      if (fetchInfo.success !== true) {
        errorMessage.value = fetchInfo.message
      } else {
        errorMessage.value = "成功"
      }
      loading.value = false;
      isClick.value = true;
      notice.setIsUpdateData(true);
    } else {
      console.log('error submit!', fields)
      errorMessage.value = "提交失败, 请检查相关数据是否填写成功 -> " + fields
    }
  })
}

const resetForm = (formEl) => {
  if (!formEl) return
  formEl.resetFields()
}

const handleClose = (val) => {
  console.log("正在关闭")
  if (isClick.value === true) {
    notice.setIsUpdateData(true);
  }
  isClick.value = false

}

// 重置表单
const onReset = async () => {
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
  // 重置表单字段
  Object.assign(form, {
    selectedProduct: [],
    selectInfluencer: '',
    selectManager: '',
    videocurrency: '',
    videocost: '',
    videoProgress: '',
    videoLinks: '',
    videoLogisticsNumber: '',
    videoestimatedLaunchDate: '',
    videoestimatedViews: '',
  });
  await updateVideo.initializeDropdownsData();
};
// 处理选择的项
const handleItemSelect = (item) => {
  console.log('用户选择了：', item);
};
// 初始化数据
onMounted(async () => {
  await updateVideo.initializeDropdownsData();
  console.log(useUser.userUUID);
});
</script>
<style scoped>
.addVideoDiv {
  text-align: right;
  border-radius: 6px;
  /* background: var(--el-color-primary-light-9); */
}

.el-drawer {
  border-radius: 10px;
}

.el-form {
  margin-top: 10%;
  margin-left: 5%;
}

.el-form-item__content {
  width: 50%;
}

.large_item {
  width: 50%;
}
</style>