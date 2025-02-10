// 后端基础URL配置
export const BASE_URL = 'http://120.79.205.19:39090/';

// 获取或生成用户ID
export const getUserId = () => {
    let userId = localStorage.getItem('userId');
    if (!userId) {
        // 生成一个随机用户ID
        userId = 'user_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('userId', userId);
    }
    return userId;
};
