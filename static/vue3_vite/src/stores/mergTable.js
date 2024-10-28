// src/stores/mergeTableData.js
import { defineStore } from "pinia";
import { ref } from "vue";

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
      return mapping[currentKey].rowIndex < mapping[minKey].rowIndex ? currentKey : minKey;
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
   * 处理需要合并的列
   * @param {Array} mergeColumns - 需要合并的列名数组
   * @param {Array} tableData - 表格数据数组
   * @param {String} mainKey - 主合并列名，例如 "parentId"
   * @returns {Object} - 合并后的列映射
   */
  const processMerge = function processMergeColumns(mergeColumns, tableData, mainKey) {
    // 记录主Key合并时的 rowIndex 分组
    console.log("tableData",tableData);

    
    const parentIdMergedGroups = [];
    const mapping = {};

    mergeColumns.forEach((key) => {
      const obj = {};

      if (!obj[key]) {
        obj[key] = {};
      }

      const rowData = tableData;
      // 初始化 -> 根据 rowIndex 进行赋值
      rowData.forEach((row, rowIndex) => {
        const value = row[key];

        // 使用字符串形式的 rowIndex 作为键
        obj[key][rowIndex] = {
          rowspan: 1,
          rowIndex: rowIndex,
          value: value,
        };
      });

      // 将相同 value 进行合并
      if (key === mainKey) {
        const parentIdMapping = obj[key];
        const valueToKeys = groupByValue(parentIdMapping);
        const mergedGroups = mergeGroups(parentIdMapping, valueToKeys);
        parentIdMergedGroups.push(...mergedGroups);
        mapping[key] = parentIdMapping;
      } else {
        // 对于其他列，仅在主Key合并的 rowIndexes 中进行合并
        if (parentIdMergedGroups.length > 0) {
          const currentKeyMapping = obj[key];
          parentIdMergedGroups.forEach((group) => {
            const { baseRowIndex, mergedRowIndexes } = group;

            // 获取所有涉及的 rowIndexes
            const allRowIndexes = [baseRowIndex, ...mergedRowIndexes];

            // 收集这些 rowIndexes 的值
            const valueToKeys = {};
            allRowIndexes.forEach((rowIdx) => {
              const keyStr = rowIdx.toString();
              if (currentKeyMapping[keyStr]) {
                // 确保 key 存在
                const value = currentKeyMapping[keyStr].value;
                if (!valueToKeys[value]) {
                  valueToKeys[value] = [];
                }
                valueToKeys[value].push(keyStr);
              }
            });

            // 对每个 value 进行合并
            for (const [value, keys] of Object.entries(valueToKeys)) {
              if (keys.length > 1) {
                // 找到 rowIndex 最小的键
                let minKey = keys[0];
                for (let i = 1; i < keys.length; i++) {
                  if (
                    currentKeyMapping[keys[i]].rowIndex <
                    currentKeyMapping[minKey].rowIndex
                  ) {
                    minKey = keys[i];
                  }
                }

                // 增加 rowspan
                currentKeyMapping[minKey].rowspan += keys.length - 1;

                // 删除其他键
                for (const delKey of keys) {
                  if (delKey !== minKey) {
                    delete currentKeyMapping[delKey];
                  }
                }
              }
            }
          });

          mapping[key] = currentKeyMapping;
        }
      }

      // 可以选择是否将 obj[key] 赋值给 mapping[key]，根据需求决定
    });

    tableMapping.value = mapping;
    console.log("Final Mapping:", mapping);
    return mapping;
  };

  return {
    processMerge,
    tableMapping,
  };
});
