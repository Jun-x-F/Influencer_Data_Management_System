// useConfirmDialog.ts
import {defineStore} from "pinia";
import {ref} from "vue";

export const useNotice = defineStore("useNotice", () => {
  const isUpdateData = ref();
  const isUpdateInfluencer = ref();
  const isResetData = ref();
  const choseProduct = ref();
  const choseManager = ref();
  const choseParentId = ref();
  const withToAddData = ref("60%");
  const withToAddMetric = ref("60%");

  const setIsResetData = function (value) {
    isResetData.value = value;
    if (value === true) {
      choseProduct.value = null;
      choseParentId.value = null;
    }
  };

  const setWithToData = function (value) {
    withToAddData.value = value;
  };
  const setWithToMetric = function (value) {
    withToAddMetric.value = value;
  };

  const setIsUpdateData = function (value) {
    isUpdateData.value = value;
  };

  const setIsUpdateInfluencerData = function (value) {
    isUpdateInfluencer.value = value;
  };

  const setManagerData = function (value) {
    console.log("choseManager", value);
    choseManager.value = value;
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
    withToAddData,
    withToAddMetric,
    choseManager,
    isUpdateInfluencer,

    setIsResetData,
    setIsUpdateData,
    setProductData,
    setParentIdData,
    setWithToData,
    setWithToMetric,
    setManagerData,
    setIsUpdateInfluencerData,
  };
});
