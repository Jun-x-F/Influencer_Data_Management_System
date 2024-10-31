<template>
  <div class="form-column">
    <el-table v-loading="loading" :data="tableFilterData" :default-sort="{ prop: 'parentId', order: 'descending' }"
      :span-method="spanMethod" :fit="true" stripe max-height="500px" border style="width: 100%; margin-top: 20px">
      <el-table-column v-for="column in columns" :key="column.prop" :prop="column.prop" :label="column.label"
        :width="column.width" :sortable="column.sortable" :filters="column.filters" :filter-method="column.filterMethod"
        :filtered-value="column.filteredValue">
        <!-- Custom Cell Content -->
        <template v-if="column.isLink" #default="scope">
          <a v-if="column.prop === '红人名称' && isValidURL(scope.row['主页视频'])" :href="scope.row['主页视频']" target="_blank"
            rel="noopener noreferrer">
            {{ scope.row[column.prop] }}
          </a>
          <a v-else-if="column.prop === '物流进度' && isValidURL(scope.row['物流单号'])" :href="scope.row['物流单号']"
            target="_blank" rel="noopener noreferrer">
            {{ scope.row[column.prop] }}
          </a>
          <a v-else-if="column.prop === '类型' && isValidURL(scope.row['视频链接'])" :href="scope.row['视频链接']" target="_blank"
            rel="noopener noreferrer">
            {{ scope.row[column.prop] }}
          </a>
          <!-- <span>{{ scope.row[column.prop] }}</span> -->
        </template>
        <!-- Default Cell Content -->
        <template v-else #default="scope">
          {{ scope.row[column.prop] }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref, watch} from "vue";
import {updateVideoData} from "@/stores/videos/update_video.js";
import {useMergeTableData} from "@/stores/mergTable.js";
import {useNotice} from '@/stores/notice.js';


// 定义 emit 方法
const notice = useNotice();
const loading = ref(false)


interface Column {
  prop: string;
  label: string;
  width: string;
  sortable?: boolean;
  filters?: any[];
  filterMethod?: (value: any, row: any, column: Column) => boolean;
  filteredValue?: any[];
  isLink?: boolean;
  merge?: boolean;
}

const tableData = ref<any[]>([]);
const updateVideo = updateVideoData();
const mergeTable = useMergeTableData();
const tableFilterData = ref();
const userFilter = ref([]);
let curList = [];
// Define fixed column configurations
const fixedColumns: Column[] = [
  {
    prop: "parentId",
    label: "唯一ID",
    width: "100px",
    sortable: true,
    merge: true,
  },
  {
    prop: "红人名称",
    label: "红人名称",
    width: "150px",
    isLink: true,
    merge: true,
  },
  {
    prop: "负责人",
    label: "负责人",
    width: "auto",
    merge: true,

  },
  { prop: "平台", label: "平台", width: "100px", merge: true },
  { prop: "品牌", label: "品牌", width: "150px", merge: true },
  { prop: "项目", label: "项目", width: "150px", merge: true },
  { prop: "产品", label: "产品", width: "150px", merge: true },
  { prop: "类型", label: "上线内容", width: "100px", merge: true, isLink: true, },
  { prop: "合作进度", label: "合作进度", width: "100px", merge: true },
  { prop: "播放量", label: "播放量", width: "auto", merge: true },

  { prop: "点赞数", label: "点赞数", width: "auto", merge: true },
  { prop: "评论数", label: "评论数", width: "auto", merge: true },
  { prop: "参与率", label: "参与率", width: "auto", merge: true },

  { prop: "物流进度", label: "物流进度", width: "230px", merge: true, isLink: true, },
  { prop: "花费", label: "花费", width: "auto", merge: true },
  { prop: "预估上线时间", label: "预估上线时间", width: "auto", merge: true },
  { prop: "预估观看量", label: "预估观看量", width: "auto", merge: true },
];

// Combine fixed columns (extend with dynamic columns if needed)
const columns = computed(() => [...fixedColumns]);

// Validate URL
const isValidURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Define columns to merge
const mergeColumns = fixedColumns
  .filter((col) => col.merge)
  .map((col) => col.prop);

// Reactive object to store merge data
const mergeData = ref<Record<string, any>>({});



// 监听 props.updateData 的变化
watch(
  () => notice.isResetData, async (newData) => {
    if (newData === true) {
      await fetchData();
      notice.setIsResetData(false);
    }
  }
);

watch(
  () => notice.choseParentId, async (newData) => {
    console.log("接收到的数据为", newData);
    if (newData) {
      console.log("notice.choseParentId", notice.choseParentId)
      tableFilterData.value = tableData.value.filter(data => {
        const parentIdstr = data.parentId.toString();
        console.log(parentIdstr.length, newData.length, parentIdstr === newData);
        if (parentIdstr.length < newData.length) {
          return false;
        } else if (parentIdstr.length === newData.length) {
          return parentIdstr === newData;
        } else {
          return parentIdstr.includes(newData);
        }
      });
      console.log("notice.choseParentId val", tableFilterData.value);
      mergeData.value = await mergeTable.processMerge(mergeColumns, tableFilterData.value, "parentId");
    }
  }
);

watch(() => notice.choseManager, async (newData) => {
  console.log(notice.choseManager === null && notice.choseManager === undefined, notice.choseManager);
  // 当 notice.choseParentId 为 null 时，继续执行
  if (notice.choseParentId !== null && notice.choseParentId !== undefined) return;
  if (notice.choseProduct !== null && notice.choseProduct !== undefined) return;
  // 提前退出条件，减少嵌套
  if (notice.choseManager === '') {
    tableFilterData.value = tableData.value;
  } else {
    console.log("notice.choseManager", notice.choseManager)
    tableFilterData.value = tableData.value.filter(data => data.负责人 === notice.choseManager);
    console.log("notice.choseManager val", tableFilterData.value);
  }

  mergeData.value = await mergeTable.processMerge(mergeColumns, tableFilterData.value, "parentId");
});

watch(
  () => notice.choseProduct,
  async (newData) => {
    // 提前退出条件，减少嵌套
    console.log(notice.choseParentId !== null, notice.choseParentId, newData.length);

    // 当 notice.choseParentId 为 null 时，继续执行
    if (notice.choseParentId !== null && notice.choseParentId !== undefined) return;

    console.log("notice.choseProduct", newData);

    if (newData.length === 0) {
      // 当 newData.length 为 0 时，将 tableData.value 赋值给 tableFilterData.value
      tableFilterData.value = tableData.value;
      console.log("No new data provided, using original dataset");
    } else {
      // 使用 Set 来优化检查
      const productSet = new Set(newData.map(row => row[2]));

      // 过滤操作
      tableFilterData.value = tableData.value.filter(data => productSet.has(data.产品));
      console.log("Filtered data", tableFilterData.value);
    }

    try {
      // 执行合并操作，并处理异步任务
      mergeData.value = await mergeTable.processMerge(mergeColumns, tableFilterData.value, "parentId");
      console.log("Merged data", mergeData.value);
    } catch (error) {
      console.error("Error processing merge:", error);
    }
  }
);



// // 使用 watch 同步 filterTableData 到 syncedRef
// watch(
//   filterTableData,
//   (newVal, oldValue) => {
//     if (newVal !== oldValue) {
//       tableData.value = newVal.sort((a, b) => b.parentId - a.parentId);
//       // Process merge data if necessary
//       mergeData.value = mergeTable.processMerge(mergeColumns, tableData.value, "parentId");
//     }
//   },
//   { immediate: true }
// );


// 定义一个函数来获取和更新数据
const fetchData = async () => {

  try {
    loading.value = true
    // Fetch table data
    const data = await updateVideo.gotTableData();

    // Sort data by parentId descending
    tableData.value = data.sort((a, b) => b.parentId - a.parentId);
    tableFilterData.value = tableData.value;
    // Process merge data if necessary
    mergeData.value = await mergeTable.processMerge(mergeColumns, tableFilterData.value, "parentId");
    loading.value = false;
  } catch (error) {
    console.error("Error fetching table data:", error);
  }

};


// Define spanMethod for cell merging
const spanMethod = ({ row, column, rowIndex, columnIndex }: any) => {
  const colName = column.property
  if (mergeData.value[colName] === undefined) {
    return {
      rowspan: 1,
      colspan: 1,
    }
  }
  if (mergeData.value[colName].length === 1) {
    return {
      rowspan: 1,
      colspan: 1,
    }
  }
  const colData = mergeData.value[colName][rowIndex]
  try {
    if (rowIndex === colData['rowIndex']) {
      return {
        // 跨度
        rowspan: colData['rowspan'],
        colspan: 1,
      }
    } else {
      return {
        rowspan: 1,
        colspan: 1,
      }
    }
  } catch (Error) {
    // 不存在的代表相同已经被过滤掉了
    return {
      rowspan: 0,
      colspan: 0,
    }
  }


};

onMounted(async () => {
  await fetchData();
});

</script>

<style scoped>
body {
  margin: 0;
}

.example-showcase .el-loading-mask {
  z-index: 9;
}

.form-column {
  padding: 20px;
}

.invalid-label {
  color: red;
}
</style>
