<template>
  <div>
    <div class="addVideoDiv">
      <el-affix target=".addVideoDiv" :offset="20">
        <el-button type="warning" @click="drawer = true">新增视频</el-button>
      </el-affix>
    </div>
    <el-drawer v-model="drawer" title="新增任务" :with-header="false" size="60%" @close="handleClose" :append-to-body="true"
      :destroy-on-close="true">
      <AlterMessage :loading="loading" v-model:modelValue="isDialogVisible" title="提交视频" :errorMessage="errorMessage"
        width="500px" />
      <el-form ref="ruleFormRef" :model="form" label-width="auto" size="large" label-position="left" :inline="true"
        :rules="rules">
        <el-form-item label="品牌-项目-产品" prop="selectedProduct">
          <CascaderSelector v-loading="loading" v-model="form.selectedProduct" :placeholder="'请输入产品'"
            :options="updateVideo.productHierarchicalData" :cascaderProps="cascaderProps"
            :dynamicMarginTop="dynamicMarginTop" tagsWith="440px" required />
        </el-form-item>
        <el-form-item label="红人名称:" prop="selectInfluencer">
          <AutocompleteInput v-model="form.selectInfluencer" :placeholder="'选择或输入红人名称'"
            :dataList="updateVideo.influencerTableName" />
        </el-form-item>
        <el-form-item label="负责人:" prop="selectManager">
          <AutocompleteInput v-model="form.selectManager" :placeholder="'请选择一个负责人'" :dataList="updateVideo.videoManager"
            @select="handleItemSelect" />
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
          <CustomInput v-model="form.videocost" :placeholder="'请输入花费'" type="number" />
        </el-form-item>

        <!-- <el-form-item label="合作进度:" prop="videoProgress">
          <AutocompleteInput v-model="form.videoProgress" :placeholder="'请输入合作进度'" :dataList="videoProgressList"
            @select="handleItemSelect" />
        </el-form-item> -->
        <el-form-item label="视频链接:" prop="videoLinks">
          <CustomInput v-model="form.videoLinks" :placeholder="'请输入视频链接'" />
        </el-form-item>
        <el-form-item label="物流链接:" prop="videoLogisticsNumber">
          <CustomInput v-model="form.videoLogisticsNumber" :placeholder="'请输入物流链接'" />
        </el-form-item>
        <el-form-item label="预估上线时间:" prop="videoestimatedLaunchDate">
          <CustomInput v-model="form.videoestimatedLaunchDate" :placeholder="'预估上线时间'" type="date" />
        </el-form-item>
        <el-form-item label="预估观看量:" prop="videoestimatedViews">
          <CustomInput v-model="form.videoestimatedViews" :placeholder="'预估观看量'" type="number" />
        </el-form-item>
        <el-form-item>
          <div style="position: relative; width: 100%">
            <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;margin-top: 10px;">
              <el-button type="primary" @click="submitForm(ruleFormRef)">创建</el-button>
              <el-button type="danger" @click="resetForm(ruleFormRef)" style="margin-right: 15px;">重置</el-button>
              <addMertics />

            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-drawer>

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
import addMertics from '@/components/videos/addMertics.vue';

const notice = useNotice();
const updateVideo = updateVideoData();
const useUser = useUserStore();
const initVideo = initVideoData();

const ruleFormRef = ref();
const isDialogVisible = ref(false);
const isClick = ref(false);
const errorMessage = ref('');
const loading = ref(false);
const dynamicMarginTop = ref('-6%');
const title = ref();
const drawer = ref(false);
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
  // videoProgress: '',
  videoLinks: '',
  videoLogisticsNumber: '',
  videoestimatedLaunchDate: '',
  videoestimatedViews: '',
});



const rules = reactive({
  selectedProduct: [
    { required: true, message: '请选择品牌-项目-产品', trigger: 'change' },
  ],
  selectManager: [
    { required: true, message: '请选择一个负责人', trigger: 'change' },
  ],
  // videoProgress: [
  //   { required: true, message: '请选择合作进度', trigger: 'change' },
  // ],
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
        obj["head"] = form.selectManager;
        obj["full_name"] = form.selectInfluencer;
        obj["video_url"] = form.videoLinks;
        obj["currency"] = form.videocurrency;
        obj["trackingNumber"] = form.videoLogisticsNumber;
        obj["cost"] = form.videocost;
        obj["estimatedGoLiveTime"] = form.videoestimatedLaunchDate;
        obj["estimatedViews"] = form.videoestimatedViews;
        // obj["progressCooperation"] = form.videoProgress;
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
      isClick.value = true;
    } else {
      console.log('error submit!', fields)
      errorMessage.value = "提交失败, 请检查相关数据是否填写成功 -> " + fields
    }
    loading.value = false;
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

// 处理选择的项
const handleItemSelect = (item) => {
  console.log('用户选择了：', item);
};

// 初始化数据
onMounted(async () => {
  await updateVideo.initializeDropdownsData();
  console.log("add_videos的onMounted", updateVideo.productHierarchicalData)
  console.log(useUser.userUUID);
});
</script>
<style scoped>
.addVideoDiv {
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