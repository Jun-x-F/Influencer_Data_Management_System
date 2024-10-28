// useConfirmDialog.ts
import { defineStore } from "pinia";
import { ref } from "vue";

export const useNotice = defineStore("useNotice", () => {
  const isUpdateData = ref();
  const isResetData = ref();
  const choseProduct = ref();
  const choseParentId = ref();

  const setIsResetData = function (value) {
    isResetData.value = value;
    if (value === true) {
      choseProduct.value = null;
      choseParentId.value = null;
    }
  };

  const setIsUpdateData = function (value) {
    isUpdateData.value = value;
  };
  const setProductData = function (value) {
    console.log("setProductData", value);
    choseProduct.value = value;
  };
  const setParentIdData = function (value) {
    choseParentId.value = value;
  };

  return {
    isUpdateData,
    choseProduct,
    choseParentId,
    isResetData,

    setIsResetData,
    setIsUpdateData,
    setProductData,
    setParentIdData,
  };
});
