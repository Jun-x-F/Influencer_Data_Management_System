// src/stores/useUserStore.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { v4 as uuidv4 } from 'uuid';

export const useUserStore = defineStore('userStore', () => {
  // 存储用户 UUID
  const userUUID = ref(null);

  // 初始化 UUID
  const initializeUUID = () => {
    const storedUUID = localStorage.getItem('userUUID');
    if (storedUUID) {
      userUUID.value = storedUUID;
    } else {
      const newUUID = uuidv4();
      userUUID.value = newUUID;
      localStorage.setItem('userUUID', newUUID);
    }
  };

  // 调用初始化函数
  initializeUUID();

  return {
    userUUID,
  };
});
