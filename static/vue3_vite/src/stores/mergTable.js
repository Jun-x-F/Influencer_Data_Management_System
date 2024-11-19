// src/stores/mergeTableData.js
import {defineStore} from "pinia";
import {ref} from "vue";

export const useMergeTableData = defineStore("mergeTableData", () => {
  const tableMapping = ref({});

  function groupByValue(mapping) {
    const valueToKeys = {};
    for (const [key, obj] of Object.entries(mapping)) {
      const val = obj.value;
      if (!valueToKeys[val]) {
        valueToKeys[val] = [];
      }
      valueToKeys[val].push(key);
    }
    return valueToKeys;
  }

  function findMinKey(keys, mapping) {
    return keys.reduce((minKey, currentKey) => {
      return mapping[currentKey].rowIndex < mapping[minKey].rowIndex
        ? currentKey
        : minKey;
    }, keys[0]);
  }

  function mergeGroups(mapping, valueToKeys) {
    const mergedGroups = [];

    for (const [value, keys] of Object.entries(valueToKeys)) {
      if (keys.length > 1) {
        const minKey = findMinKey(keys, mapping);
        const mergedRowIndexes = keys
          .filter((k) => k !== minKey)
          .map((k) => parseInt(k, 10));

        mergedGroups.push({
          baseRowIndex: parseInt(minKey, 10),
          mergedRowIndexes: mergedRowIndexes,
        });

        // 增加 `rowspan`
        mapping[minKey].rowspan += mergedRowIndexes.length;

        // 删除其他键
        for (const delKey of keys) {
          if (delKey !== minKey) {
            delete mapping[delKey];
          }
        }
      }
    }

    return mergedGroups;
  }

  /**
   * 按多个列对 tableData 进行排序
   * @param {Array} tableData - 表格数据数组
   * @param {Array} columns - 要排序的列名数组，按优先级从高到低排序
   */
  const sortTableDataByColumns = (tableData, columns) => {
    tableData.sort((a, b) => {
      for (const column of columns) {
        if (a[column] < b[column]) return 1;
        if (a[column] > b[column]) return -1;
      }
      return 0; // 所有列都相等
    });
  };

  /**
   * 处理需要合并的列
   * @param {Array} mergeColumns - 需要合并的列名数组
   * @param {Array} tableData - 表格数据数组
   * @param {String} mainKey - 主合并列名，例如 "parentId"
   * @returns {Object} - 合并后的列映射
   */
  const processMerge = function processMergeColumns(mergeColumns, tableData, mainKey) {
    console.log("tableData length", tableData.length);

    const mapping = {};
    const parentIdMergedGroups = [];
    const curLs = [];
    const positioning = {};

    // 初始化 -> 排序
    sortTableDataByColumns(tableData, mergeColumns)
    let sameMapping = [];
    let i = 0;

    while (i < tableData.length) {
      let minRowIndex = i;
      let maxRowIndex = i;
      const currentMainKey = tableData[i][mainKey];

      // 找到具有相同 mainKey 的最大行索引
      while (maxRowIndex + 1 < tableData.length && tableData[maxRowIndex + 1][mainKey] === currentMainKey) {
        maxRowIndex++;
      }

      // 保存当前分组的最小和最大行索引
      sameMapping.push({
        minRowIndex: minRowIndex,
        maxRowIndex: maxRowIndex
      });

      // 跳过已处理的行
      i = maxRowIndex + 1;
    }

    sameMapping.forEach((row) => {
      if (row.maxRowIndex === row.minRowIndex) {
        // 当只有一个行时，直接设置 rowspan 和 colspan 为 1
        mergeColumns.forEach((key) => {
          if (!mapping[key]) mapping[key] = {}; // 初始化 mapping[key]
          mapping[key][row.minRowIndex] = {
            rowspan: 1,
            colspan: 1
          };
        });
      } else {
        // 遍历每个需要合并的列
        mergeColumns.forEach((key) => {
          if (!mapping[key]) mapping[key] = {}; // 初始化 mapping[key]

          let i = row.minRowIndex;
          while (i < row.maxRowIndex) {
            const firstValue = tableData[i][key];
            let rowspan = 1;

            // 向下检查相同的值
            let j = i + 1;
            while (j < row.maxRowIndex && tableData[j][key] === firstValue) {
              rowspan++;
              j++;
            }

            // 设置 rowspan 和 colspan
            mapping[key][i] = {
              rowspan: rowspan,
              colspan: 1,
              value: firstValue
            };

            // 跳过已处理的行
            i = j;
          }
        });
      }
    });

    console.log("sameMapping", sameMapping);
    // 如果需要将结果赋值给外部的响应式对象，可以取消下面的注释
    // tableMapping.value = mapping;

    console.log("Final Mapping:", mapping);
    return mapping;
  };

  return {
    processMerge,
    tableMapping,
  };
});
