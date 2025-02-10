/**
 * @file 红人管理状态管理
 * @description 管理红人相关的状态和操作
 */

import {defineStore} from 'pinia';
import type {BaseResponse, InfluencerData, LoadingStatus} from '../types';
import {ElMessage} from 'element-plus';
import axios from 'axios';

interface InfluencerState {
    influencerList: InfluencerData[];
    isLoading: boolean;
    loadingStatus: LoadingStatus;
    projectDefinitions: any[]; // 项目定义列表
    managerList: string[]; // 管理员列表
}

export const useInfluencerStore = defineStore('influencer', {
    state: (): InfluencerState => ({
        influencerList: [],
        isLoading: false,
        loadingStatus: 'idle',
        projectDefinitions: [],
        managerList: []
    }),

    getters: {
        /**
         * 获取红人列表
         */
        getInfluencers: (state) => state.influencerList,

        /**
         * 获取加载状态
         */
        getLoadingStatus: (state) => state.loadingStatus,

        /**
         * 获取项目定义列表
         */
        getProjectDefinitions: (state) => state.projectDefinitions,

        /**
         * 获取管理员列表
         */
        getManagerList: (state) => state.managerList
    },

    actions: {
        /**
         * 获取红人列表
         */
        async getInfluencerList() {
            this.isLoading = true;
            this.loadingStatus = 'loading';
            try {
                const response = await axios.get<BaseResponse<InfluencerData[]>>('/api/influencer/list');
                if (response.data.code === 200) {
                    this.influencerList = response.data.data;
                    this.loadingStatus = 'success';
                } else {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                this.loadingStatus = 'error';
                ElMessage.error('获取红人列表失败：' + error.message);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        /**
         * 更新红人信息
         * @param data 红人信息
         */
        async updateInfluencerInfo(data: Partial<InfluencerData>) {
            try {
                const response = await axios.post<BaseResponse>('/api/influencer/update', data);
                if (response.data.code !== 200) {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                ElMessage.error('更新红人信息失败：' + error.message);
                throw error;
            }
        },

        /**
         * 删除红人信息
         * @param params 删除参数
         */
        async deleteInfluencerInfo(params: { id: number }) {
            try {
                const response = await axios.post<BaseResponse>('/api/influencer/delete', params);
                if (response.data.code !== 200) {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                ElMessage.error('删除红人信息失败：' + error.message);
                throw error;
            }
        },

        /**
         * 获取项目定义列表
         */
        async getProjectDefinitions() {
            try {
                const response = await axios.get<BaseResponse>('/api/project/definitions');
                if (response.data.code === 200) {
                    this.projectDefinitions = response.data.data;
                } else {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                ElMessage.error('获取项目定义失败：' + error.message);
                throw error;
            }
        },

        /**
         * 获取管理员列表
         */
        async getManagerList() {
            try {
                const response = await axios.get<BaseResponse<string[]>>('/api/manager/list');
                if (response.data.code === 200) {
                    this.managerList = response.data.data;
                } else {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                ElMessage.error('获取管理员列表失败：' + error.message);
                throw error;
            }
        }
    }
}); 