import {defineStore} from 'pinia';
import {ref} from 'vue';
import {dbHelper} from '@/stores/init'

export const addVideoData = defineStore('addVideo', ()=>{
    const videobrand = ref();
    const videoProjectName = ref();
    const productOptions = ref();
    /**
         * 设置关联 ==> 新增板块的项目、产品、品牌
         * */
    const updateItemDropdownByAdd = async function updateItemDropdownByAdd(brand, project, product) {
        try {
            const parametricIndicators = await dbHelper.getAllData('parametricIndicators');

            // 保存当前选中的值
            const currentBrand = videobrand.value;
            const currentProject = videoProjectName.value;
            const currentProduct = productOptions.value;

            // 清空现有的选项
            videobrand.innerHTML = '';
            videoProjectName.innerHTML = '';
            productOptions.innerHTML = '';

            // 添加默认的“请选择”选项
            addDefaultOption(videobrand, '请选择品牌');
            addDefaultOption(videoProjectName, '请选择项目');
            addDefaultOption(productOptions, '请选择产品');

            // 构建搜索条件数组，仅使用提供的参数
            const searchCriteria = [
                { field: '品牌', value: brand },
                { field: '项目', value: project },
                { field: '产品', value: product }
            ];

            // 如果所有搜索条件的值都为空，则使用全部数据
            let filteredIndicators;
            if (!brand && !project && !product) {
                filteredIndicators = parametricIndicators;
            } else {
                // 根据搜索条件过滤数据
                filteredIndicators = parametricIndicators.filter(row => {
                    return searchCriteria.every(criteria => {
                        if (criteria.value) {
                            const fieldValue = row[criteria.field] ? row[criteria.field].toLowerCase() : '';
                            const searchValue = criteria.value.toLowerCase();
                            return fieldValue.includes(searchValue);
                        } else {
                            return true;
                        }
                    });
                });
            }

            // 提取唯一的品牌、项目和产品
            const uniqueBrands = new Set();
            const uniqueProjects = new Set();
            const uniqueProducts = new Set();

            filteredIndicators.forEach(row => {
                if (row['品牌']) {
                    uniqueBrands.add(row['品牌']);
                }
                if (row['项目']) {
                    uniqueProjects.add(row['项目']);
                }
                if (row['产品']) {
                    uniqueProducts.add(row['产品']);
                }
            });

            // 更新品牌下拉列表
            uniqueBrands.forEach(brandValue => {
                const option = document.createElement('option');
                option.value = brandValue;
                option.textContent = brandValue;
                videobrand.appendChild(option);
            });

            // 更新项目下拉列表
            uniqueProjects.forEach(projectValue => {
                const option = document.createElement('option');
                option.value = projectValue;
                option.textContent = projectValue;
                videoProjectName.appendChild(option);
            });

            // 更新产品下拉列表
            uniqueProducts.forEach(productValue => {
                const option = document.createElement('option');
                option.value = productValue;
                option.textContent = productValue;
                productOptions.appendChild(option);
            });

            // 恢复用户的当前选择
            if (uniqueBrands.has(currentBrand)) {
                videobrand.value = currentBrand;
            }
            if (uniqueProjects.has(currentProject)) {
                videoProjectName.value = currentProject;
            }
            if (uniqueProducts.has(currentProduct)) {
                productOptions.value = currentProduct;
            }
        } catch (error) {
            console.error('更新下拉列表时出错：', error);
        }
    }

})