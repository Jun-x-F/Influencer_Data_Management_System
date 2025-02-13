declare module '@/config/request' {
    export function useRequestStore(): {
        get: (url: string, params?: any) => Promise<any>;
        post: (url: string, data?: any) => Promise<any>;
        put: (url: string, data?: any) => Promise<any>;
        delete: (url: string) => Promise<any>;
    };
}

declare module '@/store/useInfluencerStore' {
    import { Ref } from 'vue';

    export interface InfluencerOption {
        label: string;
        value: string;
        children?: InfluencerOption[];
    }

    export interface VideoData {
        id: number;
        parentId: number;
        红人名称?: string;
        红人全称?: string;
        品牌?: string;
        项目?: string;
        平台?: string;
        类型?: string;
        发布时间?: string;
        视频链接?: string;
        products?: Array<{
            id: number;
            name: string;
            price: number;
        }>;
        [key: string]: any;
    }

    export function useInfluencerStore(): {
        projectDefinitions: Ref<InfluencerOption[]>;
        projectDefinitionsNoFomat: Ref<any[]>;
        // 添加其他需要的方法和属性
    };
}

declare module '*.vue' {
    import type { DefineComponent } from 'vue';
    const component: DefineComponent<{}, {}, any>;
    export default component;
}

declare module '@rollup/pluginutils' {
    export function createFilter(
        include?: Array<string | RegExp> | string | RegExp | null,
        exclude?: Array<string | RegExp> | string | RegExp | null,
        options?: {
            resolve?: string | false;
            [key: string]: any;
        }
    ): (id: string) => boolean;
}

declare module './obfuscator.config.js' {
    const config: any;
    export default config;
} 