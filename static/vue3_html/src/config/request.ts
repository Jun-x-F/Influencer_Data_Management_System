import axios from 'axios'
import {defineStore} from 'pinia'
import {ref} from 'vue'
import CryptoJS from 'crypto-js'
import {BASE_URL} from './config'

export const useRequestStore = defineStore('request', () => {
    // 状态
    const publicKey = ref(localStorage.getItem('userId') ? localStorage.getItem('userId') : '')
    const userId = ref(localStorage.getItem('userId') ? localStorage.getItem('userId') : '')
    const isLoading = ref(false)
    const error = ref(null)

    // 密钥加密函数
    // 密钥加密函数
    const encryptPublicKey = (key: string): string => {
        try {
            // 固定的密钥和 IV（在生产环境中应该安全存储）
            const secretKey = '0123456789abcdef0123456789abcdef' // 32位密钥
            const iv = '0123456789abcdef' // 16位初始向量

            // 转换密钥和IV为WordArray
            const keyHex = CryptoJS.enc.Utf8.parse(secretKey)
            const ivHex = CryptoJS.enc.Utf8.parse(iv)

            // 加密
            const encrypted = CryptoJS.AES.encrypt(key, keyHex, {
                iv: ivHex,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            })

            // 返回 Base64 编码的密文
            return encrypted.toString()
        } catch (error) {
            console.error('Encryption failed:', error)
            return ''
        }
    }

    // 创建axios实例
    const service = axios.create({
        baseURL: `${BASE_URL}`, // 确保所有请求都以 /api 开头
        timeout: 15000,
    })

    // 请求拦截器
    service.interceptors.request.use(
        (config) => {
            isLoading.value = true
            error.value = null

            // 加密公钥
            const encryptedKey = publicKey.value ? encryptPublicKey(publicKey.value) : ''

            // 添加公共请求参数
            if (config.headers) {
                config.headers['X-User-Id'] = userId.value
                config.headers['X-Public-Key'] = encryptedKey
                config.headers['X-Request-Time'] = Date.now().toString() // 转换为字符串
                config.headers['Content-Type'] = 'application/json'
            }

            // 确保 URL 格式正确
            if (config.url && !config.url.startsWith('/')) {
                config.url = `/${config.url}`
            }

            return config
        },
        (err) => {
            isLoading.value = false
            error.value = err.message
            return Promise.reject(err)
        }
    )

    // 响应拦截器
    service.interceptors.response.use(
        (response) => {
            isLoading.value = false
            return response.data
        },
        (err) => {
            isLoading.value = false
            error.value = err.response?.data?.message || err.message

            // 处理特定错误状态
            switch (err.response?.status) {
                case 401:
                    // 处理未授权错误
                    console.error('Unauthorized access')
                    break
                case 403:
                    // 处理禁止访问错误
                    console.error('Access forbidden')
                    break
                case 404:
                    // 处理未找到错误
                    console.error('Resource not found')
                    break
                default:
                    console.error('An error occurred:', err.message)
            }

            return Promise.reject(err)
        }
    )

    // 设置用户ID
    const setUserId = (id: string) => {
        userId.value = id
    }

    // 设置公钥
    const setPublicKey = (key: string) => {
        publicKey.value = key
    }

    // 封装GET请求
    const get = async (url: string, params?: any) => {
        try {
            return await service.get(url, { params })
        } catch (error) {
            console.error(`GET request to ${url} failed:`, error)
            throw error
        }
    }

    // 封装POST请求
    const post = async (url: string, data?: any) => {
        try {
            return await service.post(url, data)
        } catch (error) {
            console.error(`POST request to ${url} failed:`, error)
            throw error
        }
    }

    // 封装PUT请求
    const put = async (url: string, data?: any) => {
        try {
            return await service.put(url, data)
        } catch (error) {
            console.error(`PUT request to ${url} failed:`, error)
            throw error
        }
    }

    // 封装DELETE请求
    const del = async (url: string) => {
        try {
            return await service.delete(url)
        } catch (error) {
            console.error(`DELETE request to ${url} failed:`, error)
            throw error
        }
    }

    return {
        isLoading,
        error,
        setUserId,
        setPublicKey,
        get,
        post,
        put,
        del
    }
})
