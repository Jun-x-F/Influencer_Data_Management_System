import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';
import { IndexedDBHelper } from './innodb_tools.js'; // 导入路径根据您的项目结构调整

export const useVideoStore = defineStore('videoStroe',
    () => {
        const dbName = 'videoDatabase';
        const dbVersion = 4;
        const storeSchemas = {
            // 红人表
            influencerTable: {
                keyPath: 'id',
                autoIncrement: false,
                indexes: ['id']
            },
            // 视频表
            videoTable: {
                keyPath: 'id',
                autoIncrement: false,
                indexes: ['id']
            },
            // 指标参数
            parametricIndicators: {
                keyPath: 'id',
                autoIncrement: false,
                indexes: ['id']
            },
            // 负责人
            manager: {
                keyPath: '负责人',
                autoIncrement: false,
                indexes: ['负责人']
            }
        };

        const dbHelper = new IndexedDBHelper(dbName, dbVersion, storeSchemas);

        /**
         * 页面初始化开始的时候 --> 从缓存中读取对应的数据信息
         * */
        document.addEventListener('DOMContentLoaded', async function () {
            try {
                // 初始化数据库
                await dbHelper.openDatabase();

                // 调用函数以更新视频表格并缓存数据
                await updateVideoTable();

                await updateProjectMetrics();

                await updateProjectManager();

                // 初始化视频表的下拉框数据
                await initializeDropdowns();

                // 初始化指标的下拉框数据
                await initMetrics();

                // 绑定监听器
                await bindDropdownEventListeners();

                // // 每30分钟更新一次数据库
                // setInterval(await updateVideoTable, 30 * 60 * 1000); // 30分钟 = 30 * 60 * 1000 毫秒
                // setInterval(await updateProjectMetrics, 30 * 60 * 1000); // 30分钟 = 30 * 60 * 1000 毫秒
            } catch (error) {
                console.error('初始化数据库时出错：', error);
            }
        });

        /**
         * 重置表格
         * */
        document.getElementById('resetVideoForm').addEventListener('click', async function () {
            const form = document.getElementById('videoForm');

            // 移除事件监听器
            unbindDropdownEventListeners();

            form.reset(); // 重置表单内容

            await removeHighlightVideo();

            // 重新加载品牌、项目和负责人选项
            await initializeDropdowns();

            // // 重新启用被禁用的字段
            // form.querySelector('.videoProjectName').disabled = false;
            // form.querySelector('.videobrand').disabled = false;
            // form.querySelector('.videoManager').disabled = false;
            //
            // // 处理动态添加的链接块部分
            // const dynamicLinkFields = document.querySelectorAll('.linkFields');
            // await dynamicLinkFields.forEach(function (linkField) {
            //     // 重新启用动态部分的选择框
            //     linkField.querySelector('.videoProjectName').disabled = false;
            //     linkField.querySelector('.videobrand').disabled = false;
            //     linkField.querySelector('.videoManager').disabled = false;
            //
            //     // 清空并重新加载动态添加的唯一ID字段
            //     const uniqueIdField = linkField.querySelector('.videoUniqueId');
            //     if (uniqueIdField) {
            //         uniqueIdField.value = '';  // 清空唯一ID字段的值
            //         reloadAllUniqueIdsForField(uniqueIdField);  // 重新加载唯一ID选项
            //     }
            //
            // });

            await updateVideoTable(); // 更新视频表格

            // 重新绑定事件监听器
            await bindDropdownEventListeners();

            // // 重新加载所有唯一ID，恢复为所有可选项
            // reloadAllUniqueIds();
        });
        /**
         * 更新红人表格并缓存数据
         */
        async function updateInfluencerTable() {
            fetch('/influencer/get_influencer_data', {
                method: 'GET'
            })
                .then(response => response.json())
                .then(async data => {
                    try {
                        // 清除之前的缓存
                        await dbHelper.clearStore('influencerTable');

                        // 批量写入新的缓存数据
                        await dbHelper.addOrUpdateDataBatch('influencerTable', data);

                        // 用新数据填充表格
                        await populateVideoTable(data);
                    } catch (error) {
                        console.error('更新视频表格时出错：', error);
                    }
                })
                .catch(error => console.error('获取视频表数据时出错：', error));
        }
        /**
         * 更新视频表格并缓存数据
         */
        async function updateVideoTable() {
            fetch('/video/get_video_data', {
                method: 'GET'
            })
                .then(response => response.json())
                .then(async data => {
                    try {
                        // 清除之前的缓存
                        await dbHelper.clearStore('videoTable');

                        // 批量写入新的缓存数据
                        await dbHelper.addOrUpdateDataBatch('videoTable', data);

                        // 用新数据填充表格
                        await populateVideoTable(data);
                    } catch (error) {
                        console.error('更新视频表格时出错：', error);
                    }
                })
                .catch(error => console.error('获取视频表数据时出错：', error));
        }
        /**
         * 更新项目指标并缓存数据
         */
        async function updateProjectMetrics() {
            fetch('video/get_metrics_all', {
                method: 'GET'
            })
                .then(response => response.json())
                .then(async data => {
                    try {
                        console.log(data)
                        // 清除之前的缓存
                        await dbHelper.clearStore('parametricIndicators');

                        // 批量写入新的缓存数据
                        await dbHelper.addOrUpdateDataBatch('parametricIndicators', data);

                        await updateMetricsTable();

                    } catch (error) {
                        console.error('更新视频表格时出错：', error);
                    }
                })
                .catch(error => console.error('获取视频表数据时出错：', error));
        }

        /**
         * 更新项目负责人并缓存数据
         */
        async function updateProjectManager() {
            fetch('video/get_manager_all', {
                method: 'GET'
            })
                .then(response => response.json())
                .then(async data => {
                    try {
                        console.log(data)
                        // 清除之前的缓存
                        await dbHelper.clearStore('manager');

                        // 批量写入新的缓存数据
                        await dbHelper.addOrUpdateDataBatch('manager', data);

                    } catch (error) {
                        console.error('更新视频表格时出错：', error);
                    }
                })
                .catch(error => console.error('获取视频表数据时出错：', error));
        }

        /**
         * 更新表单
         * */
        document.getElementById('videoForm').addEventListener('submit', async function (event) {
            await event.preventDefault();
            await removeHighlightVideo(); // 移除外层的红框

            // 统一变量定义，避免重复
            var uniqueIdInput = document.getElementById('videoUniqueId').value.trim();
            var influencerNameInput = document.getElementById('videoInfluencerName').value.trim();
            var responseMessage = document.getElementById('responseMessageVideo');
            responseMessage.innerHTML = ''; // 清空之前的信息

            // 获取datalist中的所有选项
            // 获取缓存数据 --> 每次更新表格都会更新缓存数据
            const influencerNameOptions = []
            const uniqueIdOptions = []
            await dbHelper.getAllData('videoTable')
                .then(data => {
                    console.info(data)
                    data.forEach(row => {
                        uniqueIdOptions.push(row.id);
                        influencerNameOptions.push(row.红人名称);
                    })
                });

            // 验证用户输入的唯一ID是否在可用选项中
            if (!uniqueIdOptions.includes(Number(uniqueIdInput))) {
                responseMessage.innerHTML = '<p style="color:red;">唯一ID不存在，请选择有效的ID。</p>';
                return; // 阻止表单提交
            }

            // 验证用户输入的红人名称是否在可用选项中
            if (!influencerNameOptions.includes(influencerNameInput)) {
                responseMessage.innerHTML = '<p style="color:red;">红人名称不存在，请选择有效的红人名称。</p>';
                return; // 阻止表单提交
            }

            // 获取字段值
            var productlist = document.getElementById('productOptions');
            var videoLinks = document.getElementById('videoLinks').value.trim();
            var uniqueId = uniqueIdInput; // 使用已获取的uniqueIdInput
            var projectName = document.getElementById('videoProjectName').value.trim();
            var brand = document.getElementById('videobrand').value.trim();
            var manager = document.getElementById('videoManager').value.trim();
            var influencerName = influencerNameInput; // 使用已获取的influencerNameInput
            var videoType = document.getElementById('videoType').value.trim();
            var progress = document.getElementById('videoProgress').value.trim();
            var logisticsNumber = document.getElementById('videoLogisticsNumber').value.trim();
            var cost = document.getElementById('videocost').value.trim();
            var currency = document.getElementById('videocurrency').value.trim();
            var product = document.getElementById('videoproduct').value.trim();
            var estimatedViews = document.getElementById('videoestimatedViews').value.trim();
            var estimatedLaunchDate = document.getElementById('videoestimatedLaunchDate').value.trim();
            var uid = uuid.v4();

            responseMessage.innerHTML = '正在提交...';

            var links = [];
            if (videoLinks) {
                links = videoLinks.split('\n').map(link => link.trim()).filter(link => link !== '');

                if (links.length > 1) {
                    Swal.fire({
                        title: '视频链接有问题，数量超过1条',
                        html: '<h3 class="subtitle">重新修改</h3>' +
                            '<div class="swal-scrollable-content">' +
                            '<ul class="link-list">' +
                            links.map(link => `
                    <li style="text-align: center">
                        <span class="error-message">${link}</span>
                    </li>
                `).join('') +
                            '</ul>' +
                            '</div>',
                        icon: 'error',
                        confirmButtonText: '确定',
                        width: '700px',
                        background: '#f9f9f9',
                        confirmButtonColor: '#3085d6',
                    });
                    responseMessage.innerHTML = '视频链接有问题，数量超过1条';
                    responseMessage.style.color = 'red'
                    return
                }

                var duplicateLinks = [];

                // 需要的子字符串列表
                const excludedSubstrings = [
                    '/reel/', '/video/', '/watch/',
                    '/video?', '/watch?', '/reel?',
                    '/p/', '/p?', '/shorts/', '/shorts?', '/status/', "https://youtu.be/"
                ];

                links.forEach(link => {
                    const isValidUrl = /^(https?:\/\/)?([\w-]+\.)+[\w-]+(\/[\w-./?%&=]*)?$/.test(link);
                    const containsExcluded = excludedSubstrings.some(substring => link.includes(substring));
                    if (!containsExcluded || !isValidUrl) {
                        duplicateLinks.push(link);
                    }
                });

                if (duplicateLinks.length > 0) {
                    Swal.fire({
                        title: '提交的链接有问题，不是视频链接格式',
                        html: '<h3 class="subtitle">重新修改</h3>' +
                            '<div class="swal-scrollable-content">' +
                            '<ul class="link-list">' +
                            duplicateLinks.map(_link => `
                    <li style="text-align: center">
                        <span class="error-message">${_link}</span>
                    </li>
                `).join('') +
                            '</ul>' +
                            '</div>',
                        icon: 'error',
                        confirmButtonText: '确定',
                        width: '700px',
                        background: '#f9f9f9',
                        confirmButtonColor: '#3085d6',
                    });
                    responseMessage.innerHTML = '提交的链接有问题，不是视频链接格式';
                    responseMessage.style.color = 'red'
                    return
                }
            }

            if (logisticsNumber) {
                // 定义一个正则表达式来匹配指定的URL格式
                const pattern = /https:\/\/t\.17track\.net\/zh-cn#nums=/;
                const isLogisticsNumber = pattern.test(logisticsNumber);
                if (!isLogisticsNumber) {
                    Swal.fire({
                        title: '提交的物流链接有问题',
                        html: `<h3 class="subtitle">重新修改, 参考<br>https://t.17track.net/zh-cn#nums=UJ712686735YP</h3>
                <div class="swal-scrollable-content">
                    <ul class="link-list">
                        <li style="text-align: center">
                            <span>你填写的链接为</span>
                            : 
                            <span class="error-message">${logisticsNumber}</span>
                        </li>
                    </ul>
                </div>`,
                        icon: 'error',
                        confirmButtonText: '确定',
                        width: '700px',
                        background: '#f9f9f9',
                        confirmButtonColor: '#3085d6',
                    });
                    responseMessage.innerHTML = '提交的物流链接有问题, 格式参考https://t.17track.net/zh-cn#nums=UJ712686735YP';
                    responseMessage.style.color = 'red';
                    return;
                }
            }


            var submissions = links.length ? links : [''];
            // 将红人名称还原回来 => 如果没有链接的话，会导致红人名称和红人全名一致
            const influencerTable = (await dbHelper.getAllData('influencerTable'));
            await influencerTable.forEach(
                row => {
                    if (row["红人全名"] === influencerName) {
                        influencerName = row["红人名称"];
                    }
                }
            );
            await Promise.all(submissions.map(link => {
                return fetch('/video/submit_link', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        link: link,
                        uniqueId: uniqueId,
                        projectName: projectName,
                        brand: brand,
                        manager: manager,
                        influencerName: influencerName,
                        videoType: videoType,
                        progress: progress,
                        logisticsNumber: logisticsNumber,
                        cost: cost,
                        currency: currency,
                        product: product,
                        estimatedViews: estimatedViews,
                        estimatedLaunchDate: estimatedLaunchDate,
                        uid: uid
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        responseMessage.innerHTML += `<p>${data.message.replace(/\n/g, '<br>')}</p>`;
                        // window.location.reload();
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        responseMessage.innerHTML += `<p style="color:red;">提交链接 ${link} 时出错，请重试。</p>`;
                    });
            }))
                .then(() => {
                    responseMessage.style.color = 'green';
                    updateVideoTable(); // 更新视频表格

                    // 自动触发重置按钮清空内容
                    document.getElementById('resetVideoForm').click();
                    productlist.innerHTML = '';

                    // 重新加载所有唯一ID，恢复为所有可选项
                    reloadAllUniqueIds();
                })
                .catch(error => {
                    responseMessage.style.color = 'red';
                    responseMessage.innerHTML = `<p>提交表单时发生错误，请稍后再试。</p>`;
                    console.error('提交表单时发生错误:', error);
                });

            // 定时任务 - 每隔5秒访问一次 localhost:5000/notice/spider/influencersVideo
            if ((links.length > 0) || (logisticsNumber.length > 0)) {
                const { intervalId, timeoutId } = startFetchSpiderNoticeWithTimeout('video', responseMessage, uid, 5000, updateVideoTable);
            }
        });

        // 更新唯一ID下拉菜单
        function updateUniqueIdDropdownOld(brand, project, manager, influencerName) {
            fetch('/video/get_filtered_unique_ids', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ brand: brand, project: project, manager: manager, influencerName: influencerName })
            })
                .then(response => response.json())
                .then(data => {
                    const videoUniqueIdSelect = document.getElementById('videoUniqueId');
                    videoUniqueIdSelect.innerHTML = ''; // 清空现有的选项

                    // 添加提示性选项
                    var placeholderOption = document.createElement('option');
                    placeholderOption.value = '';
                    placeholderOption.text = '请选择唯一ID';
                    placeholderOption.disabled = true; // 使其不可选
                    placeholderOption.selected = true; // 使其成为默认选项
                    videoUniqueIdSelect.appendChild(placeholderOption);

                    // 根据返回的ID列表填充唯一ID下拉菜单
                    data.uniqueIds.forEach(function (id) {
                        var option = document.createElement('option');
                        option.value = id;
                        option.text = id;
                        videoUniqueIdSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching filtered unique IDs:', error));
        }
        /**
         * 设置id、红人名称的关联关系 ==> 项目、产品、品牌
         * */
        async function updateItemDropdown(brand, project, product) {
            try {
                const videoTable = await dbHelper.getAllData('videoTable');
                const parametricIndicators = await dbHelper.getAllData('parametricIndicators');

                const videobrand = document.getElementById('videobrand');
                const videoProjectName = document.getElementById('videoProjectName');
                const productOptions = document.getElementById('productOptions');

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

        /**
         * 设置关联 ==> 新增板块的项目、产品、品牌
         * */
        async function updateItemDropdownByAdd(brand, project, product) {
            try {
                const parametricIndicators = await dbHelper.getAllData('parametricIndicators');

                const videobrand = document.getElementById('addBrandOptions');
                const videoProjectName = document.getElementById('addProjectOptions');
                const productOptions = document.getElementById('addProductOptions');

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

        /**
         * 设置关联 ==> 指标板块的项目、产品、品牌
         * */
        async function updateItemDropdownByMetrics(brand, project, product) {
            try {
                const parametricIndicators = await dbHelper.getAllData('parametricIndicators');

                const metricsBrandOptions = document.getElementById('metricsBrandOptions');
                const metricsProjectOptions = document.getElementById('metricsProjectOptions');
                const metricsProductOptions = document.getElementById('metricsProductOptions');


                // 保存当前选中的值
                const currentBrand = brand.value;
                const currentProject = project.value;
                const currentProduct = product.value;

                // 清空现有的选项
                metricsBrandOptions.innerHTML = '';
                metricsProjectOptions.innerHTML = '';
                metricsProductOptions.innerHTML = '';

                // 添加默认的“请选择”选项
                addDefaultOption(metricsBrandOptions, '请选择品牌');
                addDefaultOption(metricsProjectOptions, '请选择项目');
                addDefaultOption(metricsProductOptions, '请选择产品');

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
                    metricsBrandOptions.appendChild(option);
                });

                // 更新项目下拉列表
                uniqueProjects.forEach(projectValue => {
                    const option = document.createElement('option');
                    option.value = projectValue;
                    option.textContent = projectValue;
                    metricsProjectOptions.appendChild(option);
                });

                // 更新产品下拉列表
                uniqueProducts.forEach(productValue => {
                    const option = document.createElement('option');
                    option.value = productValue;
                    option.textContent = productValue;
                    metricsProductOptions.appendChild(option);
                });

                // 恢复用户的当前选择
                if (uniqueBrands.has(currentBrand)) {
                    metricsBrandOptions.value = currentBrand;
                }
                if (uniqueProjects.has(currentProject)) {
                    metricsProjectOptions.value = currentProject;
                }
                if (uniqueProducts.has(currentProduct)) {
                    metricsProductOptions.value = currentProduct;
                }
            } catch (error) {
                console.error('更新下拉列表时出错：', error);
            }
        }

        /**
         * 设置id、红人名称的关联关系 ==> 项目、产品、品牌
         * */
        async function updateItemDropdownByNameProductAndManager(manager, influencerName, product) {
            try {
                const videoTable = await dbHelper.getAllData('videoTable');

                const videoManager = document.getElementById('videoManager');
                const videoInfluencerNameList = document.getElementById('videoInfluencerNameList');
                const productOptions = document.getElementById('productOptions');

                // 保存当前选中的值
                const currentManager = videoManager.value;
                const currentInfluencerNameList = videoInfluencerNameList.value;
                const currentProduct = productOptions.value;

                // 清空现有的选项
                videoManager.innerHTML = '';
                videoInfluencerNameList.innerHTML = '';
                productOptions.innerHTML = '';

                // 添加默认的“请选择”选项
                await addDefaultOption(videoManager, '请选择负责人');
                await addDefaultOption(videoInfluencerNameList, '请选择红人名称');
                await addDefaultOption(productOptions, '请选择产品');

                // 构建搜索条件数组，仅使用提供的参数
                const searchCriteria = [
                    { field: '负责人', value: manager },
                    { field: '红人名称', value: influencerName },
                    { field: '产品', value: product }
                ];

                // 如果所有搜索条件的值都为空，则使用全部数据
                let filteredIndicators;
                if (!manager && !influencerName && !product) {
                    filteredIndicators = videoTable;
                } else {
                    // 根据搜索条件过滤数据
                    filteredIndicators = videoTable.filter(row => {
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
                const uniqueManager = new Set();
                const uniqueInfluencerName = new Set();
                const uniqueProducts = new Set();

                filteredIndicators.forEach(row => {
                    if (row['负责人']) {
                        uniqueManager.add(row['负责人']);
                    }
                    if (row['红人名称']) {
                        uniqueInfluencerName.add(row['红人名称']);
                    }
                    if (row['产品']) {
                        uniqueProducts.add(row['产品']);
                    }
                });

                // 更新负责人下拉列表
                await uniqueManager.forEach(brandValue => {
                    const option = document.createElement('option');
                    option.value = brandValue;
                    option.textContent = brandValue;
                    videoManager.appendChild(option);
                });

                // 更新红人下拉列表
                await uniqueInfluencerName.forEach(projectValue => {
                    const option = document.createElement('option');
                    option.value = projectValue;
                    option.textContent = projectValue;
                    videoInfluencerNameList.appendChild(option);
                });

                // 更新产品下拉列表
                await uniqueProducts.forEach(productValue => {
                    const option = document.createElement('option');
                    option.value = productValue;
                    option.textContent = productValue;
                    productOptions.appendChild(option);
                });

                // 恢复用户的当前选择
                if (uniqueManager.has(currentManager)) {
                    videoManager.value = currentManager;
                }
                if (uniqueInfluencerName.has(currentInfluencerNameList)) {
                    videoInfluencerNameList.value = currentInfluencerNameList;
                }
                if (uniqueProducts.has(currentProduct)) {
                    productOptions.value = currentProduct;
                }
            } catch (error) {
                console.error('更新下拉列表时出错：', error);
            }
        }

        // 根据输入的url解析并判断类型
        document.addEventListener('DOMContentLoaded', function () {
            const textarea = document.getElementById('videoLinks');
            const select = document.getElementById('videoType');

            textarea.addEventListener('input', function () {
                const value = textarea.value.trim();
                let newValue = ''; // 默认值为空

                // 依据文本内容设置 select 的值
                if (value.includes('/reel/') || value.includes('/video/') || value.includes('/watch/')
                    || value.includes('/video?') || value.includes('/watch?') || value.includes('/reel?')) {
                    newValue = '视频';
                } else if (value.includes('/p/') || value.includes('/p?')) {
                    newValue = '图片';
                } else if (value.includes('/shorts/') || value.includes('/shorts?')) {
                    newValue = '短视频';
                }

                // 更新 select 的值
                select.value = newValue;

                // 添加高亮效果
                if (newValue) {
                    select.classList.add('highlight-animation');

                    // 移除高亮效果（在 2 秒后）
                    setTimeout(() => {
                        select.classList.remove('highlight-animation');
                    }, 2000); // 2 秒钟
                }
            });
        });


        /**
         * 关联 - 监听对象
         * id -> 开启
         * 品牌、项目、产品关联 -> 开启
         * 品牌、负责人、红人关联 -> 关闭
         * 合作进度 -> 关闭
         * 视频类型 -> 开启
         * 防抖动
         * */
        function bindDropdownEventListeners() {
            const events = ["input"];
            /**
             * 根据id进行搜索功能 --> 读取的是应用里面的缓存数据
             * */
            document.getElementById('videoUniqueId').addEventListener('input', debounce(async function (event) {
                // event.stopImmediatePropagation(); // 阻止同一元素上其他 input 事件监听器执行
                const uniqueId = event.target.value.trim();
                if (uniqueId.length !== 0) {
                    console.log('输入的唯一ID：', uniqueId);
                    try {

                        // 使用 getData 方法更直接地获取数据
                        await dbHelper.getData('videoTable', parseInt(uniqueId)).then(
                            async selectRes => {
                                console.log(selectRes)
                                if (selectRes === null) {
                                    // 填充表单字段
                                    fieldMappings.forEach(mapping => {
                                        const element = formFields[mapping.field];
                                        if (element) {
                                            element.value = '';
                                        }
                                    });
                                    filterTableByProjectBrandAndManager('', '', '', '');
                                    highlightEmptyFieldsVideo();
                                    highlightRowById(uniqueId);
                                } else {
                                    // 重新加载下拉框，避免出现查询不到的问题...
                                    await initializeDropdowns();
                                    // 填充表单字段
                                    fieldMappings.forEach(mapping => {
                                        const element = formFields[mapping.field];
                                        if (element) {
                                            element.value = selectRes[mapping.key] || '';
                                        }
                                    });

                                    // 调用其他函数
                                    const project = selectRes['项目'] || '';
                                    const brand = selectRes['品牌'] || '';
                                    const manager = selectRes['负责人'] || '';
                                    const influencers = selectRes['红人名称'] || '';

                                    filterTableByProjectBrandAndManager(project, brand, manager, influencers);
                                    highlightEmptyFieldsVideo();
                                    highlightRowById(uniqueId);
                                }
                            }
                        );
                    } catch (error) {
                        console.error('获取数据时出错：', error);
                    }
                } else {
                    document.getElementById('resetVideoForm').click();
                }
            }, 300)); // 300 毫秒的防抖延迟，可根据需要调整
            ['videobrand', 'videoProjectName', 'videoproduct'].forEach(function (className) {
                const element = document.getElementById(className);

                if (element) {
                    // 根据元素类型添加合适的事件监听器

                    events.forEach(eventType => {
                        // 为了方便移除监听器，定义处理函数
                        const handler = async function (event) {
                            // 处理事件的代码
                            const brand = document.getElementById('videobrand').value;
                            const project = document.getElementById('videoProjectName').value;
                            const product = document.getElementById('videoproduct').value;
                            // const influencerName = document.getElementById('videoInfluencerName').value;

                            const target = event.target;
                            const formContainer = target.closest('.linkFields') || document.getElementById('videoForm');
                            const selectedValue = target.value;
                            const type = fieldMappings.find(item => item.field === className);

                            // 调用更新唯一ID下拉列表的函数
                            await updateItemDropdown(brand, project, product);

                            //筛选表格的数据
                            await filterTableByProjectBrandAndProduct(project, brand, product);
                            // await updateDropdownOptions(selectedValue, type.key, formContainer);
                        };

                        // 将处理函数存储在元素的属性中，以便稍后移除
                        element.addEventListener(eventType, handler);
                        if (!element._eventHandlers) {
                            element._eventHandlers = [];
                        }
                        element._eventHandlers.push({ eventType, handler });
                    });
                } else {
                    console.warn(`Element with id ${className} not found.`);
                }
            });
            // ['videoproduct', 'videoManager', 'videoInfluencerName'].forEach(function(className) {
            //     const element = document.getElementById(className);
            //
            //     if (element) {
            //         // 根据元素类型添加合适的事件监听器
            //         events.forEach(eventType => {
            //             // 为了方便移除监听器，定义处理函数
            //             const handler = async function(event) {
            //                 // 处理事件的代码
            //                 const videoManager = document.getElementById('videoManager').value;
            //                 const videoInfluencerNameList = document.getElementById('videoInfluencerNameList').value;
            //                 const videoInfluencerName = document.getElementById('videoInfluencerName').value;
            //                 const product = document.getElementById('videoproduct').value;
            //
            //                 // 调用更新唯一ID下拉列表的函数
            //                 await updateItemDropdownByNameProductAndManager(videoManager, videoInfluencerNameList, product);
            //
            //                 //筛选表格的数据
            //                 await filterTableByManagerInfluencerAndProduct(videoManager, videoInfluencerName);
            //             };
            //
            //             // 将处理函数存储在元素的属性中，以便稍后移除
            //             element.addEventListener(eventType, handler);
            //             if (!element._eventHandlers) {
            //                 element._eventHandlers = [];
            //             }
            //             element._eventHandlers.push({ eventType, handler });
            //         });
            //     } else {
            //         console.warn(`Element with id ${className} not found.`);
            //     }
            // });
            // document.getElementById('videoProgress').addEventListener('input', debounce(async function (event) {
            //     const videoProgress = event.target.value.trim();
            //     if (videoProgress.length !== 0){
            //         //筛选表格的数据
            //         await filterTableByProgress(videoProgress);
            //     }
            //
            // },300));
            document.getElementById('videoType').addEventListener('input', debounce(async function (event) {
                const videoType = event.target.value.trim();
                if (videoType.length !== 0) {
                    //筛选表格的数据
                    await filterTableByType(videoType);
                }

            }, 300));
        }
        // debounce(, 0)

        /**
         * 移除的是 ['videobrand', 'videoProjectName', 'videoproduct', 'videoInfluencerName']
         * 定义一个函数，用于移除事件监听器
         * */
        function unbindDropdownEventListeners() {
            ['videobrand', 'videoProjectName', 'videoproduct'].forEach(function (className) {
                const element = document.getElementById(className);

                if (element && element._eventHandlers) {
                    element._eventHandlers.forEach(({ eventType, handler }) => {
                        element.removeEventListener(eventType, handler);
                    });
                    element._eventHandlers = null;
                }
            });
            // ['videoproduct', 'videoManager', 'videoInfluencerName'].forEach(function(className) {
            //     const element = document.getElementById(className);
            //
            //     if (element && element._eventHandlers) {
            //         element._eventHandlers.forEach(({ eventType, handler }) => {
            //             element.removeEventListener(eventType, handler);
            //         });
            //         element._eventHandlers = null;
            //     }
            // });
        }

        /*
        * 英和html的映射表
        * */
        const formFields = {
            videobrand: document.getElementById('videobrand'),
            videoProjectName: document.getElementById('videoProjectName'),
            videoManager: document.getElementById('videoManager'),
            videoInfluencerName: document.getElementById('videoInfluencerName'),
            videoType: document.getElementById('videoType'),
            videoLinks: document.getElementById('videoLinks'),
            videoproduct: document.getElementById('videoproduct'),
            videoProgress: document.getElementById('videoProgress'),
            videoLogisticsNumber: document.getElementById('videoLogisticsNumber'),
            videocost: document.getElementById('videocost'),
            videocurrency: document.getElementById('videocurrency'),
            videoestimatedViews: document.getElementById('videoestimatedViews'),
            videoestimatedLaunchDate: document.getElementById('videoestimatedLaunchDate')
        };
        /*
        * 中英映射表
        * */
        const fieldMappings = [
            { field: 'videobrand', key: '品牌' },
            { field: 'videoProjectName', key: '项目' },
            { field: 'videoManager', key: '负责人' },
            { field: 'videoInfluencerName', key: '红人名称' },
            { field: 'videoType', key: '类型' },
            { field: 'videoLinks', key: '视频链接' },
            { field: 'videoproduct', key: '产品' },
            { field: 'videoProgress', key: '合作进度' },
            { field: 'videoLogisticsNumber', key: '物流单号' },
            { field: 'videocost', key: '花费' },
            { field: 'videocurrency', key: '币种' },
            { field: 'videoestimatedViews', key: '预估观看量' },
            { field: 'videoestimatedLaunchDate', key: '预估上线时间' }
        ];

        // 防抖函数，避免频繁调用
        function debounce(func, delay) {
            let debounceTimer;
            return function () {
                const context = this;
                const args = arguments;
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => func.apply(context, args), delay);
            };
        }


        // // 处理品牌、项目、负责人选择事件
        // ['videobrand', 'videoProjectName', 'videoManager', 'videoInfluencerName'].forEach(function(className) {
        //     const element = document.getElementById(className);
        //
        //     if (element) {
        //         // 根据元素类型添加合适的事件监听器
        //         const eventType = (className === 'videoInfluencerName') ? 'input' : 'change';
        //
        //         element.addEventListener(eventType, function(event) {
        //             const target = event.target;
        //             const formContainer = target.closest('.linkFields') || document.getElementById('videoForm');
        //             const selectedValue = target.value;
        //             const type = className === 'videobrand' ? 'brand' : className === 'videoProjectName' ? 'project' : className === 'videoManager' ? 'manager' : 'influencer';
        //
        //             updateDropdownOptions(selectedValue, type, formContainer);
        //         });
        //     } else {
        //         console.warn(`Element with id ${className} not found.`);
        //     }
        // });



        function highlightEmptyFieldsVideo(formContainer = document) {
            var fields = [
                'videoUniqueId', 'videobrand', 'videoProjectName', 'videoManager', 'videoInfluencerName', 'videoType',
                'videoLinks', 'videoproduct', 'videoProgress', 'videoLogisticsNumber',
                'videocost', 'videocurrency', 'videoestimatedLaunchDate', 'videoestimatedViews'
            ];

            fields.forEach(function (fieldId) {
                // 处理最外层表单，使用id
                var field = formContainer.getElementById ? formContainer.getElementById(fieldId) : null;

                // 如果没有找到id，处理动态生成的表单块，使用class
                if (!field && formContainer.querySelector) {
                    field = formContainer.querySelector('.' + fieldId);
                }

                // 高亮逻辑
                if (field && !field.value) {
                    field.style.borderColor = 'red'; // 高亮显示为空的字段
                } else if (field) {
                    field.style.borderColor = ''; // 移除高亮显示
                }
            });
        }

        function removeHighlightVideo(formContainer = document) {
            var fields = [
                'videoUniqueId', 'videobrand', 'videoProjectName', 'videoManager', 'videoInfluencerName', 'videoType',
                'videoLinks', 'videoproduct', 'videoProgress', 'videoLogisticsNumber',
                'videocost', 'videocurrency', 'videoestimatedLaunchDate', 'videoestimatedViews'
            ];

            fields.forEach(function (fieldId) {
                // 处理最外层表单，使用id
                var field = formContainer.getElementById ? formContainer.getElementById(fieldId) : null;

                // 如果没有找到id，处理动态生成的表单块，使用class
                if (!field && formContainer.querySelector) {
                    field = formContainer.querySelector('.' + fieldId);
                }

                // 移除高亮显示
                if (field) {
                    field.style.borderColor = ''; // 移除红色边框
                }
            });
        }


        /**
         * 获取唯一ID数据并自动填充项目、品牌、负责人
         * */
        function reloadAllUniqueIds() {
            const curData = dbHelper.getAllData('videoTable')
            curData.then(data => {
                const videoUniqueIdSelect = document.getElementById('videoUniqueId');
                videoUniqueIdSelect.innerHTML = ''; // 清空现有的选项

                // 添加提示性选项
                const placeholderOption = document.createElement('option');
                placeholderOption.value = '';
                placeholderOption.text = '请选择唯一ID';
                placeholderOption.disabled = true; // 使其不可选
                placeholderOption.selected = true; // 使其成为默认选项
                videoUniqueIdSelect.appendChild(placeholderOption);
                data.forEach(
                    row => {
                        const option = document.createElement('option');
                        option.value = row.id;
                        option.text = row.id;
                        videoUniqueIdSelect.appendChild(option);

                    }
                )
            });
        }

        /**
         * 初始化 选项提示词
         * 公用方法
         * */
        function addDefaultOption(selectElement, defaultText) {
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = defaultText;
            selectElement.appendChild(defaultOption);
        }

        /**
         * 清空下拉列表并添加默认选项
         * @param {HTMLSelectElement} selectElement - 下拉列表元素
         * @param {string} defaultText - 默认选项的文本
         */
        function clearAndAddDefaultOption(selectElement, defaultText) {
            selectElement.innerHTML = '';
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = defaultText;
            selectElement.appendChild(defaultOption);
        }

        /**
         * 初始化下拉框的数据
         * */
        async function initializeDropdowns() {
            try {
                // 获取 parametricIndicators 表的数据
                const parametricIndicators = await dbHelper.getAllData('parametricIndicators');
                const videoTable = await dbHelper.getAllData('videoTable');

                // 获取下拉框元素
                const videobrand = document.getElementById('videobrand');
                const videoProjectName = document.getElementById('videoProjectName');
                const productOptions = document.getElementById('productOptions');
                const videoUniqueIdList = document.getElementById('videoUniqueIdList');
                const videoInfluencerNameList = document.getElementById('videoInfluencerNameList');
                const videoManager = document.getElementById('videoManager');
                const videoType = document.getElementById('videoType');

                // **清空现有的选项**
                clearAndAddDefaultOption(videobrand, '请选择品牌');
                clearAndAddDefaultOption(videoProjectName, '请选择项目');
                clearAndAddDefaultOption(productOptions, '请选择产品');
                clearAndAddDefaultOption(videoUniqueIdList, '请选择唯一ID');
                clearAndAddDefaultOption(videoInfluencerNameList, '请选择红人名称');
                clearAndAddDefaultOption(videoManager, '请选择负责人');
                clearAndAddDefaultOption(videoType, '请选择类型');

                // 提取唯一的品牌、项目和产品
                const uniqueBrands = new Set();
                const uniqueProjects = new Set();
                const uniqueProducts = new Set();
                const uniqueUniqueIds = new Set();
                const uniqueInfluencerNames = new Set();
                const uniqueVideoManager = new Set();
                const uniqueType = new Set();

                parametricIndicators.forEach(row => {
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

                videoTable.forEach(
                    row => {
                        if (row['id']) {
                            uniqueUniqueIds.add(row['id']);
                        }
                        if (row['红人名称']) {
                            uniqueInfluencerNames.add(row['红人名称']);
                        }
                        if (row['负责人']) {
                            uniqueVideoManager.add(row['负责人']);
                        }
                        if (row['类型']) {
                            uniqueType.add(row['类型']);
                        }
                    }
                )


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

                let uniqueUniqueIdsSort = Array.from(uniqueUniqueIds).sort((a, b) => b - a);

                // 更新id下拉列表
                uniqueUniqueIdsSort.forEach(_id => {
                    const option = document.createElement('option');
                    option.value = _id;
                    option.textContent = _id;
                    videoUniqueIdList.appendChild(option);
                });

                // 更新产品下拉列表
                uniqueInfluencerNames.forEach(nameValue => {
                    const option = document.createElement('option');
                    option.value = nameValue;
                    option.textContent = nameValue;
                    videoInfluencerNameList.appendChild(option);
                });

                // 更新负责人下拉列表
                uniqueVideoManager.forEach(nameValue => {
                    const option = document.createElement('option');
                    option.value = nameValue;
                    option.textContent = nameValue;
                    videoManager.appendChild(option);
                });

                // 更新类型下拉列表
                uniqueType.forEach(nameValue => {
                    const option = document.createElement('option');
                    option.value = nameValue;
                    option.textContent = nameValue;
                    videoType.appendChild(option);
                });

            } catch (error) {
                console.error('初始化下拉列表时出错：', error);
            }
        }

        // 封装数据加载逻辑
        function loadUniqueIds(dropdownElement) {
            fetch('/video/get_unique_ids')
                .then(response => response.json())
                .then(data => {
                    if (data.uniqueIds) {
                        data.uniqueIds.forEach(function (id) {
                            var option = document.createElement('option');
                            option.value = id;
                            option.text = id;
                            dropdownElement.appendChild(option);
                        });
                    }
                })
                .catch(error => console.error('Error fetching unique IDs:', error));
        }

        /**
         * 关闭使用
         * */
        function loadProjectBrandManager(projectDropdown, brandDropdown, managerDropdown, influencerDropdown) {  // 新增红人名称字段
            fetch('/video/get_project_info')
                .then(response => response.json())
                .then(data => {
                    // 先清空现有选项，防止重复
                    projectDropdown.innerHTML = '<option value="">选择项目</option>';
                    brandDropdown.innerHTML = '<option value="">选择品牌</option>';
                    managerDropdown.innerHTML = '<option value="">选择负责人</option>';
                    influencerDropdown.innerHTML = '<option value="">选择红人名称</option>';  // 新增红人名称字段

                    if (data.projects) {
                        data.projects.forEach(function (project) {
                            var option = document.createElement('option');
                            option.value = project;
                            option.text = project;
                            projectDropdown.appendChild(option);
                        });
                    }
                    if (data.brands) {
                        data.brands.forEach(function (brand) {
                            var option = document.createElement('option');
                            option.value = brand;
                            option.text = brand;
                            brandDropdown.appendChild(option);
                        });
                    }
                    if (data.managers) {
                        data.managers.forEach(function (manager) {
                            var option = document.createElement('option');
                            option.value = manager;
                            option.text = manager;
                            managerDropdown.appendChild(option);
                        });
                    }
                    if (data.influencers) {  // 新增红人名称字段
                        data.influencers.forEach(function (influencer) {
                            var option = document.createElement('option');
                            option.value = influencer;
                            option.text = influencer;
                            influencerDropdown.appendChild(option);
                        });
                    }
                })
                .catch(error => console.error('Error fetching project info:', error));
        }

        // document.addEventListener('DOMContentLoaded', function() {
        //     var videoUniqueIdSelect = document.getElementById('videoUniqueId');
        //     var videoProjectSelect = document.getElementById('videoProjectName');
        //     var videoBrandSelect = document.getElementById('videobrand');
        //     var videoManagerSelect = document.getElementById('videoManager');
        //     var videoInfluencerNameSelect = document.getElementById('videoInfluencerName');  // 新增红人名称字段
        //
        //     loadUniqueIds(videoUniqueIdSelect);
        //     loadProjectBrandManager(videoProjectSelect, videoBrandSelect, videoManagerSelect, videoInfluencerNameSelect);  // 新增红人名称字段
        // });


        /**
         * 填充下拉菜单选项，并保持当前选中值
         * @param {HTMLSelectElement} dropdown - 下拉菜单元素
         * @param {Array<string>} options - 要填充的选项数组
         * @param {string} currentValue - 当前选中的值
         */
        function populateDropdown(dropdown, options, currentValue) {
            // 清空现有的选项
            dropdown.innerHTML = '';

            // 添加新的选项
            options.forEach(optionValue => {
                const option = document.createElement('option');
                option.value = optionValue;
                option.textContent = optionValue;
                dropdown.appendChild(option);
            });

            // 设置选中值，如果当前值仍然存在于新的选项中
            if (options.includes(currentValue)) {
                dropdown.value = currentValue;
            } else {
                dropdown.value = '';
            }
        }

        /**
         * 更新下拉菜单选项，根据用户的选择更新项目、负责人和红人名称的下拉菜单
         * @param {string} selectedValue - 用户选择的值
         * @param {string} type - 选择的类型（'项目'、'负责人'、'红人名称'）
         * @param {HTMLElement} formContainer - 包含下拉菜单的表单容器元素
         */
        async function updateDropdownOptions(selectedValue, type, formContainer) {
            // 如果未提供 formContainer，默认使用 id 为 'videoSection' 的元素
            if (!formContainer) {
                console.error(`Form container is undefined for selected value: ${selectedValue}, type: ${type}. Defaulting to #videoSection.`);
                formContainer = document.querySelector('#videoSection');
            }

            // 获取下拉菜单元素
            const projectDropdown = formContainer.querySelector('.videoProjectName');
            const managerDropdown = formContainer.querySelector('.videoManager');
            const influencerDropdown = formContainer.querySelector('.videoInfluencerName');
            const productDropdown = formContainer.querySelector('.videoproduct');

            // 检查下拉菜单元素是否存在
            if (!projectDropdown || !managerDropdown || !influencerDropdown) {
                console.error('Required elements not found within the form container.');
                return;
            }

            // 记录当前的选中值，以便更新后保持选中状态
            const currentProject = projectDropdown.value;
            const currentManager = managerDropdown.value;
            const currentInfluencer = influencerDropdown.value;
            const currentProduct = productDropdown.value;

            try {
                // 从 'videoTable' 数据库获取所有数据
                const data = await dbHelper.getAllData('videoTable');

                // 使用 Set 存储唯一的项目、负责人和红人名称
                let filteredProjects = new Set();
                let filteredManagers = new Set();
                let filteredInfluencers = new Set();
                let filteredProducts = new Set();

                // 定义字段映射，根据类型获取对应的字段名
                const fieldMap = {
                    '项目': '项目',
                    '负责人': '负责人',
                    '红人名称': '红人名称',
                    '产品': '产品'
                };

                // 获取用于过滤的字段名
                const fieldToFilter = fieldMap[type];

                // 如果类型不匹配，抛出错误
                if (!fieldToFilter) {
                    console.error(`Invalid type provided: ${type}`);
                    return;
                }

                // 遍历数据，根据所选类型的值进行过滤，并收集相关字段的值
                data.forEach(row => {
                    if (row[fieldToFilter] === selectedValue) {
                        if (row['项目']) filteredProjects.add(row['项目']);
                        if (row['负责人']) filteredManagers.add(row['负责人']);
                        if (row['红人名称']) filteredInfluencers.add(row['红人名称']);
                        if (row['产品']) filteredProducts.add(row['产品']);
                    }
                });

                // 将 Set 转换为数组，并更新下拉菜单
                populateDropdown(projectDropdown, Array.from(filteredProjects), currentProject);
                populateDropdown(managerDropdown, Array.from(filteredManagers), currentManager);
                populateDropdown(influencerDropdown, Array.from(filteredInfluencers), currentInfluencer);
                populateDropdown(productDropdown, Array.from(filteredProducts), currentProduct);

            } catch (error) {
                console.error('Error fetching data from videoTable:', error);
            }
        }

        /**
         * debug -- 下拉框
         * 根据点击情况修改对应的输出值
         * */
        // document.addEventListener('DOMContentLoaded', function() {
        //     const formContainer = document.querySelector('#videoSection');
        //     if (!formContainer) {
        //         console.error('Form container #videoSection is not found.');
        //         return;
        //     }
        //
        //     const videoBrand = formContainer.querySelector('#videobrand');
        //     const videoProject = formContainer.querySelector('#videoProjectName');
        //     const videoManager = formContainer.querySelector('#videoManager');
        //     const videoInfluencerName = formContainer.querySelector('#videoInfluencerName');  // 新增红人名称字段
        //
        //     console.log('Elements found:', { videoBrand, videoProject, videoManager, videoInfluencerName });  // 调试点3
        //
        //     if (videoBrand) {
        //         videoBrand.addEventListener('change', function() {
        //             console.log('Brand changed, updating dropdowns');
        //             const project = videoProject ? videoProject.value : '';
        //             const manager = videoManager ? videoManager.value : '';
        //             const influencerName = videoInfluencerName ? videoInfluencerName.value : '';  // 新增红人名称字段
        //             updateDropdownOptions(this.value, '品牌', formContainer);
        //             filterTableByProjectBrandAndManager(project, this.value, manager,influencerName);
        //         });
        //     }
        //
        //     if (videoProject) {
        //         videoProject.addEventListener('change', function() {
        //             console.log('Project changed, updating dropdowns');
        //             const brand = videoBrand ? videoBrand.value : '';
        //             const manager = videoManager ? videoManager.value : '';
        //             const influencerName = videoInfluencerName ? videoInfluencerName.value : '';  // 新增红人名称字段
        //             updateDropdownOptions(this.value, '项目', formContainer);
        //             filterTableByProjectBrandAndManager(this.value, brand, manager,influencerName);
        //         });
        //     }
        //
        //     if (videoManager) {
        //         videoManager.addEventListener('change', function() {
        //             console.log('Manager changed, updating dropdowns');
        //             const brand = videoBrand ? videoBrand.value : '';
        //             const project = videoProject ? videoProject.value : '';
        //             const influencerName = videoInfluencerName ? videoInfluencerName.value : '';  // 新增红人名称字段
        //             updateDropdownOptions(this.value, '负责人', formContainer);
        //             filterTableByProjectBrandAndManager(project, brand, this.value,influencerName);
        //         });
        //     }
        //
        //     if (videoInfluencerName) {  // 新增红人名称字段的事件监听
        //         videoInfluencerName.addEventListener('change', function() {
        //             console.log('Influencer changed, updating dropdowns');
        //             const brand = videoBrand ? videoBrand.value : '';
        //             const project = videoProject ? videoProject.value : '';
        //             const manager = videoManager ? videoManager.value : '';
        //             updateDropdownOptions(this.value, '红人名称', formContainer);
        //             filterTableByProjectBrandAndManager(project, brand, manager, this.value);
        //         });
        //     }
        //
        //     loadUniqueIds(formContainer.querySelector('#videoUniqueId'));
        //     loadProjectBrandManager(videoProject, videoBrand, videoManager, videoInfluencerName);  // 新增红人名称字段
        //     updateVideoTable(); // 更新视频表格
        // });


        /**
         * 根据项目、品牌和负责人和红人 自动筛选表格
         * */
        function filterTableByProjectBrandAndManager(project, brand, manager, InfluencerName) {
            const rows = document.querySelectorAll('#videoTable tbody tr');
            rows.forEach(row => {
                const rowProject = row.querySelector('td:nth-child(3)').textContent.trim();
                const rowBrand = row.querySelector('td:nth-child(2)').textContent.trim();
                const rowManager = row.querySelector('td:nth-child(4)').textContent.trim();
                const rowInfluencerName = row.querySelector('td:nth-child(15)').textContent.trim();  // 更新到正确的列索引

                if ((project === '' || rowProject === project) &&
                    (brand === '' || rowBrand === brand) &&
                    (manager === '' || rowManager === manager) &&
                    (InfluencerName === '' || rowInfluencerName === InfluencerName)) {  // 修正为 rowInfluencerName
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        /**
         * 根据项目、品牌和负责人和红人 自动筛选表格
         * */
        async function filterTableByProgress(progress) {
            const rows = document.querySelectorAll('#videoTable tbody tr');
            await rows.forEach(row => {
                const rowProgress = row.querySelector('td:nth-child(5)').textContent.trim();

                if ((progress === '' || rowProgress === progress)) {  // 修正为 rowInfluencerName
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        /**
         * 根据项目、品牌和产品 自动筛选表格
         * */
        function filterTableByProjectBrandAndProduct(project, brand, product) {
            const rows = document.querySelectorAll('#videoTable tbody tr');
            rows.forEach(row => {
                const rowProject = row.querySelector('td:nth-child(3)').textContent.trim();
                const rowBrand = row.querySelector('td:nth-child(2)').textContent.trim();
                const rowProduct = row.querySelector('td:nth-child(10)').textContent.trim();

                if ((project === '' || rowProject === project) &&
                    (brand === '' || rowBrand === brand) &&
                    (product === '' || rowProduct === product)) {  // 修正为 rowInfluencerName
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        /**
         * 过滤指标表
         * 根据项目、品牌和产品 自动筛选表格
         * */
        function filterMetricsByProjectBrandAndProduct(brand, project, product) {
            const rows = document.querySelectorAll('#metricsTable tbody tr');
            rows.forEach(row => {
                const rowProject = row.querySelector('td:nth-child(3)').textContent.trim();
                const rowBrand = row.querySelector('td:nth-child(2)').textContent.trim();
                const rowProduct = row.querySelector('td:nth-child(4)').textContent.trim();

                if ((project === '' || rowProject === project) &&
                    (brand === '' || rowBrand === brand) &&
                    (product === '' || rowProduct === product)) {  // 修正为 rowInfluencerName
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        /**
         * 根据负责人、红人和产品 自动筛选表格
         * */
        async function filterTableByManagerInfluencerAndProduct(manager, influencer) {
            const rows = document.querySelectorAll('#videoTable tbody tr');
            await rows.forEach(row => {
                const rowManager = row.querySelector('td:nth-child(4)').textContent.trim();
                const rowInfluencer = row.querySelector('td:nth-child(15)').textContent.trim();

                if ((manager === '' || rowManager === manager) &&
                    (influencer === '' || rowInfluencer === influencer)) {  // 修正为 rowInfluencerName
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }


        // 函数：为动态生成的字段重新加载唯一ID选项
        function reloadAllUniqueIdsForField(uniqueIdField) {
            fetch('/video/get_unique_ids')
                .then(response => response.json())
                .then(data => {
                    uniqueIdField.innerHTML = ''; // 清空现有的选项

                    // 添加提示性选项
                    var placeholderOption = document.createElement('option');
                    placeholderOption.value = '';
                    placeholderOption.text = '选择唯一id';
                    placeholderOption.disabled = true; // 使其不可选
                    placeholderOption.selected = true; // 使其成为默认选项
                    uniqueIdField.appendChild(placeholderOption);

                    // 根据返回的ID列表填充唯一ID下拉菜单
                    data.uniqueIds.forEach(function (id) {
                        var option = document.createElement('option');
                        option.value = id;
                        option.text = id;
                        uniqueIdField.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching unique IDs:', error));
        }

        // 删除按钮
        document.getElementById('deleteVideoData').addEventListener('click', function () {
            var uniqueId = document.getElementById('videoUniqueId').value;

            if (!uniqueId) {
                alert("请先选择要删除的视频的唯一ID。");
                return;
            }
            if (confirm("确定要删除此视频数据吗？")) {
                fetch('/video/delete_video_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id: uniqueId })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert("删除成功");
                            document.getElementById('videoForm').reset(); // 清空表单
                            updateVideoTable(); // 刷新表格
                        } else {
                            alert("删除失败: " + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting video data:', error);
                        alert("删除失败，请重试。");
                    });
            }
        });


        // // 更新产品
        // document.addEventListener('DOMContentLoaded', function() {
        //     // 获取产品选项和类型选项
        //     fetch('/video/get_product_options')
        //     .then(response => response.json())
        //     .then(data => {
        //         console.log('Received data:', data); // 调试输出
        //
        //         // 处理产品选项
        //         if (data && Array.isArray(data.product)) {
        //             var productOptions = document.getElementById('productOptions');
        //             data.product.forEach(function(product) {
        //                 var option = document.createElement('option');
        //                 option.value = product;
        //                 productOptions.appendChild(option);
        //             });
        //         } else {
        //             console.error('Invalid data format for products:', data);
        //         }
        //
        //         // 处理类型选项
        //         if (data && Array.isArray(data.unique_video_type)) {
        //             var typeSelects = document.querySelectorAll('.videoType'); // 获取所有类型字段
        //
        //             typeSelects.forEach(function(typeSelect) {
        //                 data.unique_video_type.forEach(function(type) {
        //                     var option = document.createElement('option');
        //                     option.value = type;
        //                     option.text = type;
        //                     typeSelect.appendChild(option);
        //                 });
        //
        //                 // 为每个类型字段添加事件监听器
        //                 typeSelect.addEventListener('change', function() {
        //                     const selectedType = this.value;
        //                     filterTableByType(selectedType);
        //                 });
        //             });
        //         } else {
        //             console.error('Invalid data format for types:', data);
        //         }
        //     })
        //     .catch(error => console.error('Error fetching product or type options:', error));
        // });
        // 单独的类型字段筛选函数
        /**
         * 过滤相关类型
         * */
        async function filterTableByType(type) {
            const rows = document.querySelectorAll('#videoTable tbody tr');
            await rows.forEach(row => {
                const rowType = row.querySelector('td:nth-child(14)').textContent.trim(); // 假设类型字段在第6列

                if (type === '' || rowType === type) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }



        /**
         * 填充视频表格
         * @param {Array} data - 要填充的视频数据
         */
        function populateVideoTable(data) {
            const tableBody = document.querySelector('#videoTable tbody');
            tableBody.innerHTML = ''; // 清空表格内容
            // 排序
            data.sort((a, b) => b.id - a.id);
            data.forEach(row => {
                var date = row.更新日期 ? new Date(row.更新日期) : null;
                var formattedDate = date && !isNaN(date) ? date.toISOString().split('T')[0] : ''; // 检查是否为有效日期

                var date2 = row.预估上线时间 ? new Date(row.预估上线时间) : null;
                var formattedDate2 = date2 && !isNaN(date2) ? date2.toISOString().split('T')[0] : ''; // 检查是否为有效日期

                var date3 = row.发布时间 ? new Date(row.发布时间) : null;
                var formattedDate3 = date3 && !isNaN(date3) ? date3.toISOString().split('T')[0] : ''; // 检查是否为有效日期

                const tr = document.createElement('tr');
                tr.innerHTML = `
            <td>${row.id || ''}</td>
            <td>${row.品牌 || ''}</td>
            <td>${row.项目 || ''}</td>
            <td>${row.负责人 || ''}</td>
            <td>${row.合作进度 || ''}</td>
            <td>${row.物流进度 || ''}</td>
            <td><a href="${row.物流单号 || ''}" target="_blank">${row.物流单号 || ''}</a></td>
            <td>${row.花费 || ''}</td>
            <td>${row.币种 || ''}</td>
            <td>${row.产品 || ''}</td>
            <td>${row.预估观看量 || ''}</td>
            <td>${formattedDate2}</td>
            <td>${row.平台 || ''}</td>
            <td>${row.类型 || ''}</td>
            <td>${row.红人名称 || ''}</td>
            <td><a href="${row.视频链接}" target="_blank">${row.视频链接}</a></td> 
            <td>${formattedDate3}</td>
            <td>${row.播放量 || ''}</td>
            <td>${row.点赞数 || ''}</td>
            <td>${row.评论数 || ''}</td>
            <td>${row.收藏数 || ''}</td>
            <td>${row.转发数 || ''}</td>
            <td>${row.参与率 || ''}</td>
            <td>${formattedDate}</td>
        `;
                tableBody.appendChild(tr);
            });

            // 应用当前筛选条件
            var currentProject = document.getElementById('videoProjectName').value;
            var currentBrand = document.getElementById('videobrand').value;
            var currentManager = document.getElementById('videoManager').value;
            var currentInfluencerName = document.getElementById('videoInfluencerName').value;
            if (currentProject || currentBrand || currentManager || currentInfluencerName) {
                filterTableByProjectBrandAndManager(currentProject, currentBrand, currentManager, currentInfluencerName);
            }
        }



        // 全局定义 updateVideoTable 函数
        // function updateVideoTable() {
        //     fetch('/video/get_video_data', {
        //         method: 'GET'
        //     })
        //     .then(response => response.json())
        //     .then(data => {
        //         const tableBody = document.querySelector('#videoTable tbody');
        //         tableBody.innerHTML = ''; // 清空表格内容
        //
        //         data.forEach(row => {
        //             var date = row.更新日期 ? new Date(row.更新日期) : null;
        //             var formattedDate = date && !isNaN(date) ? date.toISOString().split('T')[0] : ''; // 检查是否为有效日期
        //
        //             var date2 = row.预估上线时间 ? new Date(row.预估上线时间) : null;
        //             var formattedDate2 = date2 && !isNaN(date2) ? date2.toISOString().split('T')[0] : ''; // 检查是否为有效日期
        //
        //             var date3 = row.发布时间 ? new Date(row.发布时间) : null;
        //             var formattedDate3 = date3 && !isNaN(date3) ? date3.toISOString().split('T')[0] : ''; // 检查是否为有效日期
        //
        //             const tr = document.createElement('tr');
        //             tr.innerHTML = `
        //                 <td>${row.id || ''}</td>
        //                 <td>${row.品牌 || ''}</td>
        //                 <td>${row.项目 || ''}</td>
        //                 <td>${row.负责人 || ''}</td>
        //                 <td>${row.合作进度 || ''}</td>
        //                 <td>${row.物流进度 || ''}</td>
        //                 <td>${row.物流单号 || ''}</td>
        //                 <td>${row.花费 || ''}</td>
        //                 <td>${row.币种 || ''}</td>
        //                 <td>${row.产品 || ''}</td>
        //                 <td>${row.预估观看量 || ''}</td>
        //                 <td>${formattedDate2}</td>
        //                 <td>${row.平台 || ''}</td>
        //                 <td>${row.类型 || ''}</td>
        //                 <td>${row.红人名称 || ''}</td>
        //                 <td><a href="${row.视频链接}" target="_blank">${row.视频链接}</a></td>
        //                 <td>${formattedDate3}</td>
        //                 <td>${row.播放量 || ''}</td>
        //                 <td>${row.点赞数 || ''}</td>
        //                 <td>${row.评论数 || ''}</td>
        //                 <td>${row.收藏数 || ''}</td>
        //                 <td>${row.转发数 || ''}</td>
        //                 <td>${row.参与率 || ''}</td>
        //                 <td>${formattedDate}</td>
        //             `;
        //             tableBody.appendChild(tr);
        //         });
        //
        //         // 应用当前筛选条件
        //         var currentProject = document.getElementById('videoProjectName').value;
        //         var currentBrand = document.getElementById('videobrand').value;
        //         var currentManager = document.getElementById('videoManager').value;
        //         var currentInfluencerName = document.getElementById('videoInfluencerName').value;
        //         if (currentProject || currentBrand || currentManager || currentInfluencerName) {
        //             filterTableByProjectBrandAndManager(currentProject, currentBrand, currentManager,currentInfluencerName);
        //         }
        //     })
        //     .catch(error => console.error('Error fetching video table data:', error));
        // }

        // 重置表单字段和状态
        function resetFields(form) {
            // 重置主表单字段
            resetFormBlock(form);

            // 查找所有通过“添加更多链接”生成的子表单块，并重置它们的字段
            var linkFields = form.querySelectorAll('.linkFields');
            linkFields.forEach(function (linkField) {
                resetFormBlock(linkField);
            });

            // 重新加载品牌、项目和负责人选项
            loadProjectBrandManager(
                form.querySelector('.videoProjectName'),
                form.querySelector('.videobrand'),
                form.querySelector('.videoManager'),
                form.querySelector('.videoInfluencerName')
            );
            // 重新加载唯一ID下拉菜单，确保恢复为所有可选项
            reloadAllUniqueIds();
        }
        function resetFormBlock(block) {
            var projectNameField = block.querySelector('.videoProjectName');
            var brandField = block.querySelector('.videobrand');
            var managerField = block.querySelector('.videoManager');
            var influencerField = block.querySelector('.videoInfluencerName');  // 新增红人名称字段
            var uniqueIdField = block.querySelector('.videoUniqueId');

            if (projectNameField) {
                projectNameField.value = '';
                projectNameField.disabled = false;
            }
            if (brandField) {
                brandField.value = '';
                brandField.disabled = false;
            }
            if (managerField) {
                managerField.value = '';
                managerField.disabled = false;
            }
            if (influencerField) {  // 新增红人名称字段
                influencerField.value = '';
                influencerField.disabled = false;
            }
            if (uniqueIdField) {
                uniqueIdField.value = '';
            }
            // 清除高亮行的红框或其他视觉效果
            var rows = document.querySelectorAll('#videoTable tbody tr');
            rows.forEach(row => {
                row.style.backgroundColor = '';  // 重置背景色
            });
        }
        // 数据表
        function highlightRowById(uniqueId) {
            // 清除之前高亮的行
            var rows = document.querySelectorAll('#videoTable tbody tr');
            rows.forEach(row => {
                row.style.backgroundColor = '';  // 重置背景色
            });

            // 查找对应的行并更改背景色
            if (uniqueId) {
                rows.forEach(row => {
                    var rowId = row.querySelector('td:first-child').textContent.trim();
                    if (rowId === uniqueId) {
                        row.style.backgroundColor = '#d1e7dd';  // 你可以选择你喜欢的颜色
                    }
                });
            }
        }




        /**
         * 新增项目 -> 点击的时候, 加载各种选项
         * */
        document.getElementById('addVideoDataButton').addEventListener('click', async function () {
            await initAddProject();
            document.getElementById('addVideoDataForm').style.display = 'block';

        });

        /**
         * 初始化新增项目板块
         * */
        async function initAddProject() {
            // 点击新增板块的时候，自动更新一次指标数据和视频数据
            await updateVideoTable();
            await updateProjectMetrics();
            await updateInfluencerTable();

            let brandSet = new Set();
            let projectSet = new Set();
            let productSet = new Set();
            let managerSet = new Set();
            let InfluencerNameSet = new Set();
            const influencerTable = await dbHelper.getAllData('influencerTable');
            const videoTables = await dbHelper.getAllData('videoTable');
            const parametricIndicators = await dbHelper.getAllData('parametricIndicators');
            parametricIndicators.forEach(row => {
                if (row['品牌']) {
                    brandSet.add(row['品牌']);
                }
                if (row['项目']) {
                    projectSet.add(row['项目']);
                }
                if (row['产品']) {
                    productSet.add(row['产品']);
                }
            });

            videoTables.forEach(row => {
                if (row['负责人']) {
                    managerSet.add(row['负责人']);
                }
                if (row['红人名称']) {
                    InfluencerNameSet.add(row['红人名称']);
                }
            });

            influencerTable.forEach(
                row => {
                    if (row['红人全名']) {
                        InfluencerNameSet.add(row['红人全名']);
                    }
                }
            )

            populateDatalist('addBrandOptions', brandSet);
            populateDatalist('addProjectOptions', projectSet);
            populateDatalist('addProductOptions', productSet);
            populateDatalist('addInfluencerNameOptions', InfluencerNameSet);
            populateDatalist('addManagerOptions', managerSet);
        }

        // 关闭模态框
        document.getElementById('closeAddVideoForm').onclick = debounce(async function () {
            // 点击的时候，自动更新一次数据
            await updateVideoTable();
            await updateProjectMetrics();
            document.getElementById('addVideoDataForm').style.display = 'none';
        }, 5);

        // 点击取消按钮关闭模态框
        document.getElementById('cancelAddVideoData').addEventListener('click', debounce(async function () {
            // 点击的时候，自动更新一次数据
            await updateVideoTable();
            await updateProjectMetrics();
            document.getElementById('addVideoDataForm').style.display = 'none';
        }, 5));

        /**
         * 选项联动器 --> 新增品牌、项目名、产品
         * */
        ['addbrand', 'addprojectName', 'addProductOptions'].forEach(function (className) {
            const element = document.getElementById(className);

            if (element) {
                // 根据元素类型添加合适的事件监听器
                element.addEventListener("change", async function () {
                    const addBrand = document.getElementById('addbrand').value;
                    const addProjectName = document.getElementById('addprojectName').value;
                    const addProduct = document.getElementById('addProductOptions').value;
                    await updateItemDropdownByAdd(addBrand, addProjectName, addProduct);
                });
            } else {
                console.warn(`Element with id ${className} not found.`);
            }
        });

        /**
         * 监听输入新增链接的时候，是否存在相同
         * */
        document.addEventListener('DOMContentLoaded', function () {
            const addLinksTextarea = document.getElementById('addLinks');
            const errorMessage = document.getElementById('addLinksMessage');
            const addLinksBtn = document.getElementById('addLinksBtn');

            addLinksTextarea.addEventListener('input', async function (event) {
                const currentValue = event.target.value.trim();
                const cacheVideoTable = await dbHelper.getAllData('videoTable'); // 获取缓存的视频链接表
                // 缓存的youtube url的version
                const videoIDs = []
                // 将缓存里面的数据全部加载成为YouTube中的videoId
                cacheVideoTable.forEach(item => {
                    const url = item['视频链接'];
                    const platform = item['平台']
                    if (platform === "youtube") {
                        const videoID = getYouTubeVideoID(url);
                        if (videoID) {
                            videoIDs.push({
                                "id": item.id,
                                "link": item.视频链接,
                                "code": videoID
                            });
                        }
                    }
                });

                // 获取输入的链接
                const inputLinks = currentValue.split('\n').map(link => link.trim()).filter(link => link !== '');

                // 查找重复的链接及其对应的 id
                const duplicateEntries = inputLinks
                    .map(link => {
                        const matchedItem = cacheVideoTable && cacheVideoTable.find(item => item['视频链接'] === link);
                        const curVideoId = getYouTubeVideoID(link);
                        const matchedYouTuBeItem = videoIDs && videoIDs.find(cur => cur["code"] === curVideoId);

                        if (matchedYouTuBeItem) {
                            return { id: matchedYouTuBeItem.id, link: matchedYouTuBeItem['link'] };
                        } else if (matchedItem) {
                            return { id: matchedItem.id, link: matchedItem['视频链接'] };
                        } else {
                            return null;
                        }
                    })
                    .filter(item => item !== null);

                if (duplicateEntries.length > 0) {
                    errorMessage.classList.add('show');
                    const duplicateInfo = duplicateEntries.map(item => `ID: ${item.id}, 链接: ${item.link}`).join('\n');
                    errorMessage.textContent = `链接已存在，请检查：\n${duplicateInfo}`;
                    addLinksTextarea.classList.add('addLinks-error');
                    addLinksBtn.disabled = true;
                } else {
                    // 清除错误状态
                    addLinksTextarea.classList.remove('addLinks-error');
                    errorMessage.classList.remove('show');
                    errorMessage.textContent = '';
                    addLinksBtn.disabled = false;
                }
            });
        });

        // 提交新增表单时处理数据
        document.getElementById('addVideoData').addEventListener('submit', async function (event) {
            event.preventDefault();
            var responseMessage = document.getElementById('formErrorMessage');
            responseMessage.innerHTML = ''; // 清空之前的信息

            // 获取表单值
            var brandInput = document.getElementById('addbrand').value.trim();
            var projectInput = document.getElementById('addprojectName').value.trim();
            var managerInput = document.getElementById('addmanager').value.trim();
            var influencerNameInput = document.getElementById('addInfluencerName').value.trim();
            var currencyInput = document.getElementById('addcurrency').value.trim();
            var productInput = document.getElementById('addproduct').value.trim();
            var progressInput = document.getElementById('addProgress').value.trim();
            // 视频链接
            var videoLinks = document.getElementById('addLinks').value.trim();
            // 获取选择框中的所有选项值
            var brandOptions = Array.from(document.querySelectorAll('#addBrandOptions option')).map(option => option.value);
            var projectOptions = Array.from(document.querySelectorAll('#addProjectOptions option')).map(option => option.value);
            var managerOptions = Array.from(document.querySelectorAll('#addManagerOptions option')).map(option => option.value);
            var influencerNameOptions = Array.from(document.querySelectorAll('#addInfluencerNameOptions option')).map(option => option.value);
            var currencyOptions = Array.from(document.querySelectorAll('#addcurrency option')).map(option => option.value);
            var productOptions = Array.from(document.querySelectorAll('#addProductOptions option')).map(option => option.value);
            var progressOptions = Array.from(document.querySelectorAll('#addProgressOptions option')).map(option => option.value);
            var uid = uuid.v4();

            // 验证用户输入的品牌是否在可用选项中
            if (!brandOptions.includes(brandInput)) {
                responseMessage.innerHTML = '<p style="color:red;">品牌不存在，请选择有效的品牌。</p>';
                return; // 阻止表单提交
            }
            // 验证用户输入的项目是否在可用选项中
            if (!projectOptions.includes(projectInput)) {
                responseMessage.innerHTML = '<p style="color:red;">项目不存在，请选择有效的项目。</p>';
                return; // 阻止表单提交
            }
            // 验证用户输入的负责人是否在可用选项中
            if (!managerOptions.includes(managerInput)) {
                responseMessage.innerHTML = '<p style="color:red;">负责人不存在，请选择有效的负责人。</p>';
                return; // 阻止表单提交
            }
            // 验证用户输入的红人名称是否在可用选项中
            if (!influencerNameOptions.includes(influencerNameInput)) {
                responseMessage.innerHTML = '<p style="color:red;">红人名称不存在，请选择有效的红人名称。</p>';
                return; // 阻止表单提交
            }
            // 验证用户输入的币种是否在可用选项中
            if (!currencyOptions.includes(currencyInput)) {
                responseMessage.innerHTML = '<p style="color:red;">币种不存在，请选择有效的币种。</p>';
                return; // 阻止表单提交
            }
            // 验证用户输入的产品是否在可用选项中
            if (!productOptions.includes(productInput)) {
                responseMessage.innerHTML = '<p style="color:red;">产品不存在，请选择有效的产品。</p>';
                return; // 阻止表单提交
            }
            // 验证用户输入的合作进度是否在可用选项中
            if (!progressOptions.includes(progressInput)) {
                responseMessage.innerHTML = '<p style="color:red;">合作进度不存在，请选择有效的合作进度。</p>';
                return; // 阻止表单提交
            }

            await fetch('/video/check_url_existing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "url": videoLinks
                })
            }).then(response => response.json()).then(data => {
                if (data.isSame) {
                    Swal.fire({
                        title: '链接已存在，请检查',
                        html: `
            <h3 class="subtitle">重新确认</h3>
            <div class="swal-scrollable-content">
                <ul class="link-list">
                    <li style="text-align: center; font-size: 14px;">
                        <span class="link-text">${videoLinks}</span> - 对应唯一id为 
                        <span class="error-message">${data.data}</span>
                    </li>
                </ul>
            </div>
        `,
                        icon: 'error',
                        confirmButtonText: '确定',
                        width: '700px',
                        background: '#f9f9f9',
                        confirmButtonColor: '#3085d6',
                    });
                }
                return;
            })

            // 如果所有验证通过，组装表单数据并提交
            var formData = {
                "uid": uid,
                "品牌": brandInput,
                "项目": projectInput,
                "负责人": managerInput,
                "红人名称": influencerNameInput,  // 新增红人名称字段
                "视频链接": document.getElementById('addLinks').value,  // 新增视频链接字段
                "花费": document.getElementById('addcost').value,
                "币种": currencyInput,
                "产品": productInput,
                "合作进度": progressInput,
                "预估观看量": document.getElementById('addestimatedViews').value,
                "预估上线时间": document.getElementById('addestimatedLaunchDate').value
            };
            const influencerTable = await dbHelper.getAllData('influencerTable');
            // 避免出现匹配不上的问题
            await influencerTable.forEach(row => {
                if (row["红人全名"] === influencerNameInput) {
                    console.log("匹配成功");
                    console.log(row);
                    formData["红人名称"] = row["红人名称"];
                    formData["红人全称"] = row["红人全名"];
                }
            })
            await fetch('/video/add_video_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);

                    // 清空表单字段
                    document.getElementById('addbrand').value = '';
                    document.getElementById('addprojectName').value = '';
                    document.getElementById('addmanager').value = '';
                    document.getElementById('addInfluencerName').value = '';  // 清空红人名称
                    document.getElementById('addLinks').value = '';  // 清空视频链接
                    document.getElementById('addcost').value = '';
                    document.getElementById('addcurrency').value = '';
                    document.getElementById('addproduct').value = '';
                    document.getElementById('addProgress').value = '';
                    document.getElementById('addestimatedViews').value = '';
                    document.getElementById('addestimatedLaunchDate').value = '';

                    document.getElementById('addVideoDataForm').style.display = 'none';
                    updateVideoTable();  // 提交成功后更新表格
                    // 提交成功后刷新页面
                    window.location.reload();
                })
                .catch(error => console.error('Error:', error));
        });

        // 表单重置
        document.getElementById('addresetMetricsForm').addEventListener('click', async function () {
            const form = document.getElementById('addVideoData');
            form.reset(); // 重置表单内容

            // 重新初始化
            await initAddProject();

            // loadAllOptions();
            // updateMetricsTable();
        });

        /**
         * 指标表
         * 监听事件 联动选择和筛选
         * */
        ['metricsBrand', 'metricsProject', 'metricsProduct'].forEach(function (className) {
            const element = document.getElementById(className);
            if (element) {
                // 根据元素类型添加合适的事件监听器
                element.addEventListener("change", async function () {
                    const metricsBrand = document.getElementById('metricsBrand').value;
                    const metricsProject = document.getElementById('metricsProject').value;
                    const metricsProduct = document.getElementById('metricsProduct').value;
                    await updateItemDropdownByMetrics(metricsBrand, metricsProject, metricsProduct);
                    await filterMetricsByProjectBrandAndProduct(metricsBrand, metricsProject, metricsProduct);
                });
            } else {
                console.warn(`Element with id ${className} not found.`);
            }
        })

        /**
         * 指标数据 => 表单提交
         * */
        document.getElementById('metricsDefinitionForm').addEventListener('submit', function (event) {
            event.preventDefault();

            const brand = document.getElementById('metricsBrand').value.trim();
            const project = document.getElementById('metricsProject').value.trim();
            const manager = document.getElementById('metricsManager').value.trim();
            const product = document.getElementById('metricsProduct').value.trim();
            const responseMessage = document.getElementById('responseMessageMetrics');

            responseMessage.innerHTML = '正在提交...';

            fetch('video/add_metrics_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    brand: brand,
                    project: project,
                    manager: manager,
                    product: product
                })
            })
                .then(response => response.json())
                .then(async data => {
                    responseMessage.innerHTML = `<p>${data.message}</p>`;
                    responseMessage.style.color = 'green';
                    await updateMetricsTable();
                })
                .catch(error => {
                    console.error('Error:', error);
                    responseMessage.innerHTML = `<p style="color:red;">提交时出错，请重试。</p>`;
                });
        });

        /**
         * 重置指标参数
         * */
        document.getElementById('resetMetricsForm').addEventListener('click', async function () {
            const form = document.getElementById('metricsDefinitionForm');
            form.reset(); // 重置表单内容

            // 重新加载品牌、项目、负责人和产品选项
            await initMetrics();
            // loadAllOptions();
            await updateMetricsTable();
        });

        /**
         * 初始化指标看板的数据
         * */
        async function initMetrics() {
            const parametricIndicators = await dbHelper.getAllData('parametricIndicators');
            const managers = await dbHelper.getAllData('manager');

            let brandSet = new Set();
            let projectSet = new Set();
            let productSet = new Set();
            let managerSet = new Set();
            parametricIndicators.forEach(data => {
                if (data['品牌']) {
                    brandSet.add(data['品牌']);
                }
                if (data['项目']) {
                    projectSet.add(data['项目']);
                }
                if (data['产品']) {
                    productSet.add(data['产品']);
                }
            });

            await managers.forEach(data => {
                if (data['负责人']) {
                    managerSet.add(data['负责人']);
                }
            });

            await populateDatalist('metricsBrandOptions', brandSet);
            await populateDatalist('metricsProjectOptions', projectSet);
            await populateDatalist('metricsProductOptions', productSet);
            await populateDatalist('metricsManagerOptions', managerSet);
        }

        function loadAllOptions() {
            fetch('video/get_metrics_options')
                .then(response => response.json())
                .then(async data => {
                    console.log('Fetched data:', data);  // 打印获取的数据
                    window.allOptions = data;
                    window.allOptions.relationships = data.relationships || [];  // 确保 relationships 被正确设置

                    populateDatalist('metricsBrandOptions', data.brands);
                    populateDatalist('metricsProjectOptions', data.projects);
                    populateDatalist('metricsProductOptions', data.products);
                    populateDatalist('metricsManagerOptions', data.managers);
                })
                .catch(error => console.error('Error fetching options:', error));
        }


        /**
         * 生成对应id的options
         * */
        function populateDatalist(datalistId, items) {
            const datalist = document.getElementById(datalistId);
            datalist.innerHTML = ''; // 清空现有的选项
            items.forEach(function (item) {
                const option = document.createElement('option');
                option.value = item;
                datalist.appendChild(option);
            });
        }

        // 根据用户的选择，动态更新其他字段的可选项
        function updateProjectAndProductOptions(selectedBrand, selectedProject, selectedProduct) {
            if (!window.allOptions || !window.allOptions.relationships) {
                console.error('Error: Relationships data is missing or undefined.');
                return;
            }

            const filteredProjects = window.allOptions.projects.filter(project => {
                return window.allOptions.relationships.some(relation => relation.brand === selectedBrand && relation.project === project);
            });

            const filteredProducts = window.allOptions.products.filter(product => {
                return window.allOptions.relationships.some(relation => relation.brand === selectedBrand && relation.product === product);
            });

            if (filteredProjects.length > 0) {
                populateDatalist('metricsProjectOptions', filteredProjects);
            }

            if (filteredProducts.length > 0) {
                populateDatalist('metricsProductOptions', filteredProducts);
            }
        }


        function updateBrandAndProductOptions(selectedBrand, selectedProject, selectedProduct) {
            if (!window.allOptions || !window.allOptions.relationships) {
                console.error('Error: Relationships data is missing or undefined.');
                return;
            }

            const filteredBrands = window.allOptions.brands.filter(brand => {
                return window.allOptions.relationships.some(relation => relation.project === selectedProject && relation.brand === brand);
            });

            const filteredProducts = window.allOptions.products.filter(product => {
                return window.allOptions.relationships.some(relation => relation.project === selectedProject && relation.product === product);
            });

            if (filteredBrands.length > 0) {
                populateDatalist('metricsBrandOptions', filteredBrands);
            }

            if (filteredProducts.length > 0) {
                populateDatalist('metricsProductOptions', filteredProducts);
            }
        }

        function updateBrandAndProjectOptions(selectedBrand, selectedProject, selectedProduct) {
            if (!window.allOptions || !window.allOptions.relationships) {
                console.error('Error: Relationships data is missing or undefined.');
                return;
            }

            const filteredBrands = window.allOptions.brands.filter(brand => {
                return window.allOptions.relationships.some(relation => relation.product === selectedProduct && relation.brand === brand);
            });

            const filteredProjects = window.allOptions.projects.filter(project => {
                return window.allOptions.relationships.some(relation => relation.product === selectedProduct && relation.project === project);
            });

            if (filteredBrands.length > 0) {
                populateDatalist('metricsBrandOptions', filteredBrands);
            }

            if (filteredProjects.length > 0) {
                populateDatalist('metricsProjectOptions', filteredProjects);
            }
        }



        /**
         * updateMetricsTable 更新项目指标的数据
         * */
        function updateMetricsTable() {
            dbHelper.getAllData('parametricIndicators').then(data => {
                const tableBody = document.querySelector('#metricsTable tbody');
                tableBody.innerHTML = ''; // 清空表格内容
                // 排序
                data.sort((a, b) => b.id - a.id);
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                <td>${row.id || ''}</td>
                <td>${row.品牌 || ''}</td>
                <td>${row.项目 || ''}</td>
                <td>${row.产品 || ''}</td>
            `;
                    tableBody.appendChild(tr);
                });

                // 应用当前筛选条件（如有需要）
                var currentBrand = document.getElementById('metricsBrand').value;
                var currentProject = document.getElementById('metricsProject').value;
                var currentProduct = document.getElementById('metricsProduct').value;
                if (currentBrand || currentProject || currentProduct) {
                    filterTableByMetrics(currentBrand, currentProject, currentProduct);
                }
            })
        }

        // 可选：用于按条件筛选表格的函数
        function filterTableByMetrics(brand, project, product) {
            const tableRows = document.querySelectorAll('#metricsTable tbody tr');
            tableRows.forEach(row => {
                const brandMatch = row.children[0].textContent.includes(brand);
                const projectMatch = row.children[1].textContent.includes(project);
                const productMatch = row.children[2].textContent.includes(product);

                if (brandMatch && projectMatch && productMatch) {
                    row.style.display = ''; // 显示匹配的行
                } else {
                    row.style.display = 'none'; // 隐藏不匹配的行
                }
            });
        }
        document.getElementById('deleteMetricsData').addEventListener('click', function () {
            var uniqueId = document.getElementById('metricsId').value;

            if (!uniqueId) {
                alert("请先选择要删除的视频的唯一ID。");
                return;
            }
            if (confirm("确定要删除此视频数据吗？")) {
                fetch('/video/delete_metrics_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id: uniqueId })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert("删除成功");
                            document.getElementById('videoForm').reset(); // 清空表单
                            updateMetricsTable();
                        } else {
                            alert("删除失败: " + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting video data:', error);
                        alert("删除失败，请重试。");
                    });
            }
        });

    }
)