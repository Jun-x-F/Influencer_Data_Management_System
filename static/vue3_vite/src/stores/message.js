import { defineStore } from "pinia";
import { ref } from "vue";
import {initVideoData} from "@/stores/init.js";
import {useUserStore} from "@/stores/userInfo.js";


export const useMessageInfo = defineStore("messageData", () => {
  const messageList = ref([]);
  const status = ref();
  const noticeUser = ref(false)
  const initVideo = initVideoData();
  const useUser = useUserStore();


  function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
  
    const year = date.getFullYear();
  
    // 月份从0开始，需要加1
    const month = String(date.getMonth() + 1).padStart(2, '0');
  
    const day = String(date.getDate()).padStart(2, '0');
  
    const hours = String(date.getHours()).padStart(2, '0');
  
    const minutes = String(date.getMinutes()).padStart(2, '0');
  
    const seconds = String(date.getSeconds()).padStart(2, '0');
  
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
  
    const setNotice = function setNoticeFunction(value){
        noticeUser.value = value
    }

  const getMessage = async function fetchMessageInfo() {
        const body = {
            "uid": useUser.userUUID
        };
        const fetchInfo = await initVideo.fetchData("/notice/api/video_message","POST", body);
        // {'message': 'test', 'status': 'create', 'timestamp': 1729762496}
        console.log(fetchInfo)
        if (fetchInfo.message === null){
            return;
        }

        fetchInfo.message.sort((a, b) => b.timestamp - a.timestamp);

        fetchInfo.message.forEach(element => {
            element["timestamp"] = formatTimestamp(element["timestamp"]*1000);
        });
        
        console.log(fetchInfo.message)
        status.value = fetchInfo.status;
        messageList.value = fetchInfo.message;
  }

  return {
    messageList,
    noticeUser,
    status,

    getMessage,
    setNotice
  }
});