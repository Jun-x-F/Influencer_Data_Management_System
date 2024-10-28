<template>
  <div class="form-column">
    <el-table v-loading="loading" :data="tableData" :default-sort="{ prop: 'parentId', order: 'descending' }"
      :span-method="spanMethod" :fit="true" stripe max-height="500px" border style="width: 100%; margin-top: 20px">
      <el-table-column v-for="column in columns" :key="column.prop" :prop="column.prop" :label="column.label"
        :width="column.width" :sortable="column.sortable" :filters="column.filters" :filter-method="column.filterMethod"
        :filtered-value="column.filteredValue">
        <!-- Custom Cell Content -->
        <template v-if="column.isLink" #default="scope">
          <a v-if="column.prop === '视频链接' && isValidURL(scope.row[column.prop])" :href="scope.row[column.prop]"
            target="_blank" rel="noopener noreferrer">
            视频链接
          </a>
          <a v-else-if="column.prop === '红人名称' && isValidURL(scope.row['视频链接'])" :href="scope.row['视频链接']"
            target="_blank" rel="noopener noreferrer">
            {{ scope.row[column.prop] }}
          </a>
          <a v-else-if="column.prop === '物流进度' && isValidURL(scope.row['物流单号'])" :href="scope.row['物流单号']"
            target="_blank" rel="noopener noreferrer">
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
  filterMethod?: Function;
  filteredValue?: any[];
  isLink?: boolean;
  merge?: boolean;
}

const tableData = ref<any[]>([]);
const updateVideo = updateVideoData();
const mergeTable = useMergeTableData();

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
  { prop: "负责人", label: "负责人", width: "auto", merge: true },
  { prop: "平台", label: "平台", width: "100px", merge: true },
  { prop: "品牌", label: "品牌", width: "150px", merge: true },
  { prop: "项目", label: "项目", width: "150px", merge: true },
  { prop: "产品", label: "产品", width: "150px", merge: true },
  { prop: "播放量", label: "播放量", width: "auto", merge: true },
  { prop: "参与率", label: "参与率", width: "auto", merge: true },
  { prop: "点赞数", label: "点赞数", width: "auto", merge: true },
  { prop: "评论数", label: "评论数", width: "auto", merge: true },
  { prop: "类型", label: "类型", width: "auto", merge: true },
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
  () => notice.choseParentId, async (newData, oldValue) => {
    if (newData !== oldValue) {
      console.log("notice.choseParentId", notice.choseParentId)
      tableData.value = tableData.value.filter(data => data.parentId === notice.choseParentId);
      console.log("notice.choseParentId val", tableData.value);
      mergeData.value = await mergeTable.processMerge(mergeColumns, tableData.value, "parentId");
    }
  }
);

watch(
  () => notice.choseProduct, async (newData, oldValue) => {
    if (newData !== oldValue && notice.choseParentId === null) {
      console.log("notice.choseProduct", notice.choseProduct)
      tableData.value = tableData.value.filter(data => notice.choseProduct.includes(data.产品));
      console.log("notice.choseProduct val", tableData.value);
      mergeData.value = await mergeTable.processMerge(mergeColumns, tableData.value, "parentId");
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
  loading.value = true
  try {
    // Fetch table data
    const data = await updateVideo.gotTableData();
    // Sort data by parentId descending
    tableData.value = data.sort((a, b) => b.parentId - a.parentId);
    // Process merge data if necessary
    mergeData.value = await mergeTable.processMerge(mergeColumns, tableData.value, "parentId");
  } catch (error) {
    console.error("Error fetching table data:", error);
  }
  loading.value = false
};


onMounted(async () => {
  await fetchData();
});
// Define spanMethod for cell merging
const spanMethod = ({ row, column, rowIndex, columnIndex }: any) => {
  const colName = column.property
  const colData = mergeData.value[colName][rowIndex]
  try {
    if (rowIndex === colData['rowIndex']) {
      return {
        // 跨度
        rowspan: colData['rowspan'],
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
  return {
    rowspan: 1,
    colspan: 1,
  }
};
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
