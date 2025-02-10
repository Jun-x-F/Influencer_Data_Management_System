/**
 * @file 通用工具函数
 * @description 提供系统中常用的工具函数
 */

import {parsePhoneNumberFromString} from 'libphonenumber-js';

/**
 * 格式化日期时间
 * @param dateTimeStr 日期时间字符串
 * @returns 格式化后的日期时间字符串
 */
export const formatDateTime = (dateTimeStr: string): string => {
    if (!dateTimeStr) return '';
    try {
        const date = new Date(dateTimeStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    } catch {
        return dateTimeStr;
    }
};

/**
 * 获取相对时间描述
 * @param dateTimeStr 日期时间字符串
 * @returns 相对时间描述
 */
export const getTimeAgo = (dateTimeStr: string): string => {
    if (!dateTimeStr) return '';
    try {
        const date = new Date(dateTimeStr);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        if (days > 0) {
            return `在${days}天${hours}小时前发布`;
        } else if (hours > 0) {
            return `在${hours}小时${minutes}分钟前发布`;
        } else if (minutes > 0) {
            return `在${minutes}分钟前发布`;
        } else {
            return '在刚刚发布';
        }
    } catch {
        return '';
    }
};

/**
 * 验证电话号码
 * @param contact 联系方式字符串
 * @returns 是否为有效的电话号码
 */
export const validatePhoneNumber = (contact: string): boolean => {
    const cleanNumber = contact.replace(/[^\d]/g, '');
    try {
        const parsedNumber = parsePhoneNumberFromString('+' + cleanNumber);
        return parsedNumber?.isValid() || false;
    } catch {
        return false;
    }
};

/**
 * 验证URL
 * @param url URL字符串
 * @returns 是否为有效的URL
 */
export const isValidURL = (url: string): boolean => {
    if (!url) return false;
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
};

/**
 * 标准化字符串（用于搜索匹配）
 * @param str 输入字符串
 * @returns 标准化后的字符串
 */
export const normalizeForSearch = (str: string): string => {
    return str
        .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '') // 只保留字母、数字和中文字符
        .toLowerCase() // 转换为小写
        .trim(); // 移除首尾空格
};

/**
 * 获取平台标签类型
 * @param platform 平台名称
 * @returns 对应的标签类型
 */
export const getPlatformTagType = (platform: string): string => {
    const typeMap: { [key: string]: string } = {
        'youtube': 'danger',
        'instagram': 'warning',
        'tiktok': 'success',
        'x': 'info',
        'facebook': 'primary',
        'twitch': 'purple',
        'linkedin': 'info',
    };
    return typeMap[platform?.toLowerCase()] || 'info';
};

/**
 * 获取平台图标
 * @param platform 平台名称
 * @returns 对应的图标
 */
export const getPlatformIcon = (platform: string): string => {
    const iconMap: { [key: string]: string } = {
        'youtube': '📺',
        'instagram': '📷',
        'tiktok': '🎵',
        'x': '🐦',
        'facebook': '👥',
        'twitch': '🎮',
        'linkedin': '💼',
    };
    return iconMap[platform?.toLowerCase()] || '🌐';
}; 