/**
 * @file 全局类型定义
 * @description 定义系统中使用的所有通用接口和类型
 */

// 基础响应接口
export interface BaseResponse<T = any> {
    code: number;
    message: string;
    data: T;
}

// 分页请求参数接口
export interface PaginationParams {
    page: number;
    pageSize: number;
}

// 分页响应接口
export interface PaginationResponse<T> {
    total: number;
    items: T[];
}

// 红人信息接口
export interface InfluencerData {
    id: number;
    红人名称: string;
    红人全称?: string;
    红人头像地址?: string;
    平台: string;
    粉丝数量: number;
    平均播放量: number;
    平均点赞数量: number;
    平均评论数量: number;
    平均参与率: number;
    地区?: string;
    地址?: string;
    联系方式?: string;
    标签?: string;
    评级?: string;
}

// 视频信息接口
export interface VideoData {
    id: number;
    parentId: number;
    红人名称?: string;
    红人全称?: string;
    品牌?: string;
    项目?: string;
    产品?: string;
    平台?: string;
    类型?: string;
    发布时间?: string;
    物流进度?: string;
    合作进度?: string;
    视频链接?: string;
    物流单号?: string;
    花费?: number;
    币种?: string;
    预估观看量?: number;
    预估上线时间?: string;
}

// 产品选项接口
export interface ProductOption {
    label: string;
    value: string;
    children?: ProductOption[];
    count?: number;
    leaf?: boolean;
}

// 平台类型映射
export interface PlatformType {
    [key: string]: string;
}

// 状态类型
export type LoadingStatus = 'idle' | 'loading' | 'success' | 'error';

// 搜索状态接口
export interface SearchState {
    keywords: string[];
    currentData: any[];
    scrollPosition: number;
    searchTags: string[];
} 