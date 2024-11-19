<template>
    <div>
        <div class="addVideoDiv">
            <el-affix target=".addVideoDiv" :offset="20">
                <el-button type="success" @click="handleButtonClick" :disabled="isButtonDisabled">指标模块</el-button>
            </el-affix>
            <el-dialog v-model="checkPassword" width="500">
                <h1>进行权限校验</h1>
                <el-row justify="center">
                    <el-col :span="6" style="margin-left: -150px;"> <el-input v-model="inputPassword"
                            style="width: 300px;" type="password" placeholder="Please input password"
                            show-password /></el-col>

                </el-row>

                <template #footer>
                    <div class="dialog-footer">
                        <el-button>Cancel</el-button>
                        <el-button type="primary" @click="To2vCheck">
                            Confirm
                        </el-button>
                    </div>
                </template>
            </el-dialog>
        </div>

    </div>
    <el-drawer v-model="drawer" title="指标板块" :with-header="false" size="50%" @close="handleClose"
        :append-to-body="true">
        <div class="el_drawer">
            <el-form ref="ruleFormRef" :model="form" label-width="auto" size="large" label-position="left"
                :inline="true" :rules="rules">
                <el-form-item label="指标Id:" prop="id" ref="tips1">
                    <AutocompleteInput v-model="form.id" :placeholder="'指标ID'"
                        :dataList="updateVideo.parametricIndicatorsId" required />
                </el-form-item>
                <el-form-item label="品牌:" prop="brand" ref="tips2">
                    <AutocompleteInput v-model="form.brand" :placeholder="'品牌'" :dataList="updateVideo.videobrand" />
                </el-form-item>
                <el-form-item label="项目:" prop="project" ref="tips3">
                    <AutocompleteInput v-model="form.project" :placeholder="'项目'"
                        :dataList="updateVideo.videoProjectName" />
                </el-form-item>
                <el-form-item label="产品:" prop="product" ref="tips4">
                    <AutocompleteInput v-model="form.product" :placeholder="'产品'"
                        :dataList="updateVideo.productOptions" />
                </el-form-item>
                <el-form-item label="负责人:" prop="selectManager" ref="tips5">
                    <AutocompleteInput v-model="form.selectManager" :placeholder="'负责人（仅新增）'"
                        :dataList="updateVideo.videoManager" />
                </el-form-item>
                <el-form-item>
                    <div style="position: relative; width: 100%">
                        <div style="display: flex; justify-content: flex-start; margin-bottom: -15px;margin-top: 10px;">
                            <el-button type="primary" @click="submitForm(ruleFormRef)">创建</el-button>
                            <el-button type="warning" @click="resetForm(ruleFormRef)">重置</el-button>
                            <el-button type="danger" @click="resetForm(ruleFormRef)">删除</el-button>
                            <el-button type="info" @click="open = true" style="margin-right: 12px;">提示</el-button>
                            <add_videos />
                        </div>
                    </div>

                </el-form-item>
            </el-form>
            <el-tour v-model="open">
                <el-tour-step :target="tips1?.$el" title="指标Id">
                    <span>
                        1. 更新或者是删除品牌、项目、产品的时候，必须要有它！！！
                    </span><br />
                    <span>
                        2. 新增品牌、项目、产品的时候，必须把它置空！！！
                    </span>
                </el-tour-step>
                <el-tour-step :target="tips2?.$el" title="品牌" description="选择品牌，和项目、产品必须同时存在" />
                <el-tour-step :target="tips3?.$el" title="项目" description="选择项目，和品牌、产品必须同时存在" />
                <el-tour-step :target="tips4?.$el" title="产品" description="选择产品，和品牌、项目必须同时存在" />
                <el-tour-step :target="tips5?.$el" title="负责人">
                    <span>
                        1. 这里<b><u>不是指向品牌、项目、产品的负责人</u></b>！！！这里填写的负责人是提供更多的负责人可选项
                    </span><br />
                    <span>
                        2. 负责人和品牌、项目、产品是可以同时存在的！！！
                    </span>
                    <br />
                    <span>
                        3. 负责人的删除与修改，只能联系相关人员！！！
                    </span>
                </el-tour-step>
            </el-tour>
        </div>
        <el-divider></el-divider>
        <div>
            <el-table :data="viedoTable" style="width: 100%" :default-sort="{ prop: 'id', order: 'descending' }"
                :fit="true" stripe max-height="500px" border>
                <el-table-column prop="id" label="id" width="100px" :sortable="true" :merge="true" />
                <el-table-column prop="品牌" label="品牌" width="150px" />
                <el-table-column prop="项目" label="项目" width="auto" />
                <el-table-column prop="产品" label="产品" width="auto" />
            </el-table>
        </div>
        <AlterMessage :loading="loading" v-model:modelValue="isDialogVisible" title="提交指标" :errorMessage="errorMessage"
            width="500px" />
    </el-drawer>
</template>
<script setup>
import {onMounted, reactive, ref, watch} from 'vue';
import {initVideoData} from '@/stores/init.js';
import {updateVideoData} from '@/stores/videos/update_video.js';
import {useUserStore} from '@/stores/userInfo.js';
import AutocompleteInput from '@/components/tables_element/AutocompleteInput.vue';
import AlterMessage from '@/components/tables_element/AlterMessage.vue';
import {useNotice} from '@/stores/notice.js';
import add_videos from '@/components/videos/add_videos.vue';
import {ElNotification} from 'element-plus'
// 打开提示
const open = ref(false)
const tips1 = ref()
const tips2 = ref()
const tips3 = ref()
const tips4 = ref()
const tips5 = ref()


const notice = useNotice();
const updateVideo = updateVideoData();
const useUser = useUserStore();
const initVideo = initVideoData();
const errorMessage = ref();
const activeName = ref('1')
const ruleFormRef = ref();
const drawer = ref(false);
const isClick = ref(false);
const isDialogVisible = ref(false);
const inputPassword = ref();
const checkPassword = ref(false);
const loading = ref(false);
const isButtonDisabled = ref(false);
const viedoTable = ref();
const form = reactive({
    id: '',
    brand: '',
    project: '',
    product: '',
    selectManager: '',
});


const rules = reactive({
    // brand: [
    //     { required: true, message: '请选择品牌', trigger: 'change' },
    // ],
    // project: [
    //     { required: true, message: '请选择项目', trigger: 'change' },
    // ],
    // product: [
    //     { required: true, message: '请选择产品', trigger: 'change' },
    // ],
    // selectManager: [
    //     { required: true, message: '请选择负责人', trigger: 'change' },
    // ]
})

const handleButtonClick = () => {
    checkPassword.value = true;
    // drawer.value = true;
}

const To2vCheck = () => {
    if (inputPassword.value === "1234") {
        drawer.value = true;
        checkPassword.value = false;
    } else {
        ElNotification({
            title: 'Error',
            message: '请重试！！！',
            type: 'error'
        })
    }
}

const handleClose = (val) => {
    console.log("新增指标的draw 正在关闭")
    if (isClick.value === true) {
        notice.setIsUpdateData(true);
    }
    isClick.value = false

}
const submitForm = async (formEl) => {
    if (!formEl) return;
    await formEl.validate(async (valid, fields) => {
        loading.value = true;
        isDialogVisible.value = true;
        let message = "请填写数据进去！！！";
        console.log("id", form.id);
        console.log("brand", form.brand);
        console.log("project", form.project);

        if (form.id !== "") {
            const toRequestData = {
                "uid": useUser.userUUID,
                "data": {
                    "id": form.id,
                    "brand": form.brand,
                    "project": form.project,
                    "product": form.product,
                }
            };
            const fetchInfo = await initVideo.fetchData("/video/api/metrics/update_data", "POST", toRequestData);
            if (fetchInfo.success !== true) {
                message = form.brand + " " + form.project + " " + form.product + " 更新指标失败, 原因为 " + fetchInfo.message + " \n";
            } else {
                message = form.brand + " " + form.project + " " + form.product + " 更新指标成功\n";
                isClick.value = true;
            };

        } else if (form.product !== "" && form.brand !== "" && form.project !== "") {
            const toRequestData = {
                "uid": useUser.userUUID,
                "data": {
                    "brand": form.brand,
                    "project": form.project,
                    "product": form.product,
                }
            };
            const fetchInfo = await initVideo.fetchData("/video/api/metrics/add_data", "POST", toRequestData);
            if (fetchInfo.success !== true) {
                message = form.brand + " " + form.project + " " + form.product + " 新增指标失败, 原因为 " + fetchInfo.message + " \n";
            } else {
                message = form.brand + " " + form.project + " " + form.product + " 新增指标成功\n";
                isClick.value = true;
            };
        };

        if (form.selectManager !== "") {
            const toRequestData = {
                "uid": useUser.userUUID,
                "manager": form.selectManager
            };
            const fetchInfo = await initVideo.fetchData("/video/api/metrics/add_manger", "POST", toRequestData);
            if (fetchInfo.success !== true) {
                message = form.selectManager + " 新增负责人失败, 原因为 " + fetchInfo.message + " \n";
            } else {
                message = form.selectManager + " 新增负责人成功" + " \n";
                isClick.value = true;
            };
        };
        errorMessage.value = message;
        loading.value = false;
        await resetForm(formEl);
    })
};

const resetForm = async (formEl) => {
    if (!formEl) return;
    formEl.resetFields();
    await initVideo.initialize();
    await updateVideo.initializeDropdownsData();
    viedoTable.value = await updateVideo.gotMeirtcsData();
}

// id
watch(() => form.id, (newId) => {
    console.log(newId);
    viedoTable.value = viedoTable.value.filter(data => data.id === newId);
    viedoTable.value.forEach(data => {
        form.project = data.项目;
        form.brand = data.品牌;
        form.product = data.产品;
    });
});

// 品牌
watch(() => form.brand, (newBrand) => {
    console.log(newBrand);
    const project = new Set();
    const product = new Set();
    viedoTable.value = viedoTable.value.filter(data => data.品牌 === newBrand);
    viedoTable.value.forEach(data => {
        project.add(data.项目);
        product.add(data.产品);
    });
    updateVideo.videoProjectName = Array.from(project);
    updateVideo.productOptions = Array.from(product);
});


// 项目
watch(() => form.project, (newProject) => {
    console.log(newProject);
    viedoTable.value = viedoTable.value.filter(data => data.项目 === newProject);
    const brand = new Set();
    const product = new Set();
    viedoTable.value.forEach(data => {
        brand.add(data.品牌);
        product.add(data.产品);
    });
    updateVideo.videobrand = Array.from(brand);
    updateVideo.productOptions = Array.from(product);

});

// 产品
watch(() => form.product, (newProduct) => {
    console.log(newProduct);
    viedoTable.value = viedoTable.value.filter(data => data.产品 === newProduct);
    const brand = new Set();
    const project = new Set();
    viedoTable.value.forEach(data => {
        brand.add(data.品牌);
        project.add(data.项目);
    });
    updateVideo.videobrand = Array.from(brand);
    updateVideo.videoProjectName = Array.from(project);
});

// 初始化数据
onMounted(async () => {
    await updateVideo.initializeDropdownsData();
    viedoTable.value = await updateVideo.gotMeirtcsData();
    console.log(useUser.userUUID);
    console.log("viedoTable", viedoTable);
});
</script>
<style scoped>
.addVideoDiv {
    border-radius: 6px;
    /* background: var(--el-color-primary-light-9); */
}

::v-deep .el-form-item__content .el-row {
    width: 100%;
}
</style>