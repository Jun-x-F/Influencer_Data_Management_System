/**
 * @file 视频管理状态管理
 * @description 管理视频相关的状态和操作
 */

import {defineStore} from 'pinia';
import type {BaseResponse, LoadingStatus, VideoData} from '../types';
import {ElMessage} from 'element-plus';
import axios from 'axios';

interface VideoState {
    videoList: VideoData[];
    isVideoLoading: boolean;
    loadingStatus: LoadingStatus;
}

export const useVideoStore = defineStore('video', {
    state: (): VideoState => ({
        videoList: [],
        isVideoLoading: false,
        loadingStatus: 'idle'
    }),

    getters: {
        /**
         * 获取视频列表
         */
        getVideos: (state) => state.videoList,

        /**
         * 获取加载状态
         */
        getLoadingStatus: (state) => state.loadingStatus
    },

    actions: {
        /**
         * 获取视频列表
         */
        async getVideoList() {
            this.isVideoLoading = true;
            this.loadingStatus = 'loading';
            try {
                const response = await axios.get<BaseResponse<VideoData[]>>('/api/video/list');
                if (response.data.code === 200) {
                    this.videoList = response.data.data;
                    this.loadingStatus = 'success';
                } else {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                this.loadingStatus = 'error';
                ElMessage.error('获取视频列表失败：' + error.message);
                throw error;
            } finally {
                this.isVideoLoading = false;
            }
        },

        /**
         * 更新视频信息
         * @param data 视频信息
         */
        async updateVideo(data: Partial<VideoData>) {
            try {
                const response = await axios.post<BaseResponse>('/api/video/update', data);
                if (response.data.code !== 200) {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                ElMessage.error('更新视频信息失败：' + error.message);
                throw error;
            }
        },

        /**
         * 删除视频
         * @param parentId 父级ID
         */
        async deleteVideo(parentId: number) {
            try {
                const response = await axios.post<BaseResponse>('/api/video/delete', { parentId });
                if (response.data.code !== 200) {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                ElMessage.error('删除视频失败：' + error.message);
                throw error;
            }
        },

        /**
         * 添加视频
         * @param data 视频信息
         */
        async addVideo(data: Partial<VideoData>) {
            try {
                const response = await axios.post<BaseResponse>('/api/video/add', data);
                if (response.data.code !== 200) {
                    throw new Error(response.data.message);
                }
            } catch (error: any) {
                ElMessage.error('添加视频失败：' + error.message);
                throw error;
            }
        }
    }
}); 