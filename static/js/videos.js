// 更新视频板块
// 提交表单、
document.getElementById('videoForm').addEventListener('submit', function(event) {
    event.preventDefault();
    removeHighlightVideo(); // 移除外层的红框

    var uniqueIdInput = document.getElementById('videoUniqueId').value.trim();
    var influencerNameInput = document.getElementById('videoInfluencerName').value.trim();
    var responseMessage = document.getElementById('responseMessageVideo');
    responseMessage.innerHTML = ''; // 清空之前的信息
    // 获取datalist中的所有选项
    var uniqueIdOptions = Array.from(document.querySelectorAll('#videoUniqueIdList option')).map(option => option.value);
    var influencerNameOptions = Array.from(document.querySelectorAll('#videoInfluencerNameList option')).map(option => option.value);
    // 验证用户输入的唯一ID是否在可用选项中
    if (!uniqueIdOptions.includes(uniqueIdInput)) {
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
    var uniqueId = document.getElementById('videoUniqueId').value.trim();
    var projectName = document.getElementById('videoProjectName').value.trim();
    var brand = document.getElementById('videobrand').value.trim();
    var manager = document.getElementById('videoManager').value.trim();
    var influencerName = document.getElementById('videoInfluencerName').value.trim();
    var videoType = document.getElementById('videoType').value.trim();
    var progress = document.getElementById('videoProgress').value.trim();
    var logisticsNumber = document.getElementById('videoLogisticsNumber').value.trim();
    var cost = document.getElementById('videocost').value.trim();
    var currency = document.getElementById('videocurrency').value.trim();
    var product = document.getElementById('videoproduct').value.trim();
    var estimatedViews = document.getElementById('videoestimatedViews').value.trim();
    var estimatedLaunchDate = document.getElementById('videoestimatedLaunchDate').value.trim();
    var uid = uuid.v4();
    var responseMessage = document.getElementById('responseMessageVideo');
    responseMessage.innerHTML = '正在提交...';

    var links = [];
    if (videoLinks) {
        links = videoLinks.split('\n').map(link => link.trim()).filter(link => link !== '');
        var uniqueLinks = new Set();
        var duplicateLinks = [];

        links.forEach(link => {
            if (uniqueLinks.has(link)) {
                duplicateLinks.push(link);
            } else {
                uniqueLinks.add(link);
            }
        });

        if (duplicateLinks.length > 0) {
            responseMessage.innerHTML = `<p style="color:red;">以下链接在提交中重复: ${duplicateLinks.join(', ')}</p>`;
            return;
        }
    }


    var submissions = links.length ? links : [''];

    Promise.all(submissions.map(link => {
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
            window.location.reload();
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
    const {intervalId, timeoutId} =startFetchSpiderNoticeWithTimeout('video', responseMessage, uid, 5000, updateVideoTable)
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
        data.uniqueIds.forEach(function(id) {
            var option = document.createElement('option');
            option.value = id;
            option.text = id;
            videoUniqueIdSelect.appendChild(option);
        });
    })
    .catch(error => console.error('Error fetching filtered unique IDs:', error));
}
function updateUniqueIdDropdown(brand, project, manager, influencerName) {
    fetch('/video/get_filtered_unique_ids', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ brand, project, manager, influencerName })
    })
    .then(response => response.json())
    .then(data => {
        const uniqueIdList = document.getElementById('videoUniqueIdList'); // 直接操作 datalist
        uniqueIdList.innerHTML = ''; // 清空之前的选项
        data.uniqueIds.forEach(function(id) {
            const option = document.createElement('option');
            option.value = id;
            uniqueIdList.appendChild(option);
        });
    })
    .catch(error => console.error('Error fetching filtered unique IDs:', error));
}
function updateInfluencerNameDropdown(brand, project, manager) {
    fetch('/video/get_project_info')
        .then(response => response.json())
        .then(data => {
            const influencerNameList = document.getElementById('videoInfluencerNameList');
            influencerNameList.innerHTML = ''; // 清空现有的选项

            // 根据选择的品牌、项目和负责人来过滤红人名称
            data.relationships.forEach(function(relation) {
                if (
                    (relation.brand === brand || brand === '') &&
                    (relation.project === project || project === '') &&
                    (relation.manager === manager || manager === '')
                ) {
                    const option = document.createElement('option');
                    option.value = relation.influencer;
                    influencerNameList.appendChild(option);
                }
            });
        })
        .catch(error => console.error('Error fetching filtered influencers:', error));
}



// 当品牌、项目或负责人改变时，更新唯一ID下拉菜单
// 当品牌、项目、负责人或红人名称改变时，更新唯一ID下拉菜单
['videobrand', 'videoProjectName', 'videoManager', 'videoInfluencerName'].forEach(function(className) {
    const element = document.getElementById(className);

    if (element) {
        // 根据元素类型添加合适的事件监听器
        const eventType = (className === 'videoInfluencerName') ? 'input' : 'change';

        element.addEventListener(eventType, function() {
            const brand = document.getElementById('videobrand').value;
            const project = document.getElementById('videoProjectName').value;
            const manager = document.getElementById('videoManager').value;
            const influencerName = document.getElementById('videoInfluencerName').value;

            // 调用更新唯一ID下拉列表的函数
            updateUniqueIdDropdown(brand, project, manager, influencerName);

            // 你也可以在这里调用其他函数，比如更新红人名称的下拉列表（如果需要）
            updateInfluencerNameDropdown(brand, project, manager);
        });
    } else {
        console.warn(`Element with id ${className} not found.`);
    }
});



// 选择id后，将数据显示在控件中
// 监听 videoUniqueId 的输入事件
document.getElementById('videoUniqueId').addEventListener('input', function(event) {
    const uniqueId = event.target.value;
    // 检查是否是唯一ID的下拉菜单触发了事件
    if (uniqueId) {
        fetch('/video/get_video_details', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ uniqueId: uniqueId })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // 使用空字符串作为默认值
            const brand = data.brand || '';
            const project = data.project || '';
            const manager = data.manager || '';
            const influencers = data.influencers || '';  // 新增红人名称字段
            const video_type = data.video_type || '';
            const videoLinks = data.videoLinks || '';
            const product = data.product || '';
            const progress = data.progress || '';
            const logisticsNumber = data.logisticsNumber || '';
            const cost = data.cost || '';
            const currency = data.currency || '';
            const estimatedViews = data.estimatedViews || '';
            const estimatedLaunchDate = data.estimatedLaunchDate || '';

            // 填充表单字段，确保元素存在再设置值
            if (document.getElementById('videobrand')) document.getElementById('videobrand').value = brand;
            if (document.getElementById('videoProjectName')) document.getElementById('videoProjectName').value = project;
            if (document.getElementById('videoManager')) document.getElementById('videoManager').value = manager;
            if (document.getElementById('videoInfluencerName')) document.getElementById('videoInfluencerName').value = influencers;  // 新增红人名称字段
            console.log("Video Type:", video_type);
            if (document.getElementById('videoType')) document.getElementById('videoType').value = video_type;
            if (document.getElementById('videoLinks')) document.getElementById('videoLinks').value = videoLinks;
            if (document.getElementById('videoproduct')) document.getElementById('videoproduct').value = product;
            if (document.getElementById('videoProgress')) document.getElementById('videoProgress').value = progress;
            if (document.getElementById('videoLogisticsNumber')) document.getElementById('videoLogisticsNumber').value = logisticsNumber;
            if (document.getElementById('videocost')) document.getElementById('videocost').value = cost;
            if (document.getElementById('videocurrency')) document.getElementById('videocurrency').value = currency;
            if (document.getElementById('videoestimatedViews')) document.getElementById('videoestimatedViews').value = estimatedViews;
            if (document.getElementById('videoestimatedLaunchDate')) document.getElementById('videoestimatedLaunchDate').value = estimatedLaunchDate;

            // 调用筛选函数
            filterTableByProjectBrandAndManager(project, brand, manager, influencers);
            // 调用高亮显示函数
            highlightEmptyFieldsVideo();
            // 高亮表格中对应的行
            highlightRowById(uniqueId);
        })
        .catch(error => console.error('Error:', error));
    } else {
        // 如果唯一ID为空，清空并解锁相关输入框
        resetFields(document.getElementById('videoForm'));
    }
});

// 处理品牌、项目、负责人选择事件
['videobrand', 'videoProjectName', 'videoManager', 'videoInfluencerName'].forEach(function(className) {
    const element = document.getElementById(className);

    if (element) {
        // 根据元素类型添加合适的事件监听器
        const eventType = (className === 'videoInfluencerName') ? 'input' : 'change';

        element.addEventListener(eventType, function(event) {
            const target = event.target;
            const formContainer = target.closest('.linkFields') || document.getElementById('videoForm');
            const selectedValue = target.value;
            const type = className === 'videobrand' ? 'brand' : className === 'videoProjectName' ? 'project' : className === 'videoManager' ? 'manager' : 'influencer';

            updateDropdownOptions(selectedValue, type, formContainer);
        });
    } else {
        console.warn(`Element with id ${className} not found.`);
    }
});



function highlightEmptyFieldsVideo(formContainer = document) {
    var fields = [
        'videoUniqueId', 'videobrand', 'videoProjectName', 'videoManager','videoInfluencerName','videoType',
        'videoLinks', 'videoproduct', 'videoProgress', 'videoLogisticsNumber',
        'videocost', 'videocurrency', 'videoestimatedLaunchDate', 'videoestimatedViews'
    ];

    fields.forEach(function(fieldId) {
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
        'videoUniqueId', 'videobrand', 'videoProjectName', 'videoManager','videoInfluencerName','videoType',
        'videoLinks', 'videoproduct', 'videoProgress', 'videoLogisticsNumber',
        'videocost', 'videocurrency', 'videoestimatedLaunchDate', 'videoestimatedViews'
    ];

    fields.forEach(function(fieldId) {
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


// 获取唯一ID数据并自动填充项目、品牌、负责人
function reloadAllUniqueIds() {
    fetch('/video/get_unique_ids')
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

            // 填充所有的唯一ID
            data.uniqueIds.forEach(function(id) {
                var option = document.createElement('option');
                option.value = id;
                option.text = id;
                videoUniqueIdSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching all unique IDs:', error));
}


// 在页面加载时获取项目、品牌和负责人信息
document.addEventListener('DOMContentLoaded', function() {
    fetch('/video/get_project_info')
        .then(response => response.json())
        .then(data => {
            if (data.brands) {
                var videoBrandSelect = document.getElementById('videobrand');
                data.brands.forEach(function(brand) {
                    var option = document.createElement('option');
                    option.value = brand;
                    option.text = brand;
                    videoBrandSelect.appendChild(option);
                });
            }
            if (data.projects) {
                var videoProjectSelect = document.getElementById('videoProjectName');
                data.projects.forEach(function(project) {
                    var option = document.createElement('option');
                    option.value = project;
                    option.text = project;
                    videoProjectSelect.appendChild(option);
                });
            }
            if (data.managers) {
                var videoManagerSelect = document.getElementById('videoManager');
                data.managers.forEach(function(manager) {
                    var option = document.createElement('option');
                    option.value = manager;
                    option.text = manager;
                    videoManagerSelect.appendChild(option);
                });
            }
            // if (data.influencers) {
            //     var videoInfluencerNameSelect = document.getElementById('videoInfluencerName');
            //     data.influencers.forEach(function(influencer) {
            //         var option = document.createElement('option');
            //         option.value = influencer;
            //         option.text = influencer;
            //         videoInfluencerNameSelect.appendChild(option);
            //     });
            // }
            if (data.influencers) {
                var videoInfluencerNameList = document.getElementById('videoInfluencerNameList');
                videoInfluencerNameList.innerHTML = ''; // 清空现有的选项

                data.influencers.forEach(function(influencer) {
                    var option = document.createElement('option');
                    option.value = influencer;
                    videoInfluencerNameList.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error fetching project info:', error));
});

// 封装数据加载逻辑
function loadUniqueIds(dropdownElement) {
    fetch('/video/get_unique_ids')
        .then(response => response.json())
        .then(data => {
            if (data.uniqueIds) {
                data.uniqueIds.forEach(function(id) {
                    var option = document.createElement('option');
                    option.value = id;
                    option.text = id;
                    dropdownElement.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error fetching unique IDs:', error));
}

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
                data.projects.forEach(function(project) {
                    var option = document.createElement('option');
                    option.value = project;
                    option.text = project;
                    projectDropdown.appendChild(option);
                });
            }
            if (data.brands) {
                data.brands.forEach(function(brand) {
                    var option = document.createElement('option');
                    option.value = brand;
                    option.text = brand;
                    brandDropdown.appendChild(option);
                });
            }
            if (data.managers) {
                data.managers.forEach(function(manager) {
                    var option = document.createElement('option');
                    option.value = manager;
                    option.text = manager;
                    managerDropdown.appendChild(option);
                });
            }
            if (data.influencers) {  // 新增红人名称字段
                data.influencers.forEach(function(influencer) {
                    var option = document.createElement('option');
                    option.value = influencer;
                    option.text = influencer;
                    influencerDropdown.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error fetching project info:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    var videoUniqueIdSelect = document.getElementById('videoUniqueId');
    var videoProjectSelect = document.getElementById('videoProjectName');
    var videoBrandSelect = document.getElementById('videobrand');
    var videoManagerSelect = document.getElementById('videoManager');
    var videoInfluencerNameSelect = document.getElementById('videoInfluencerName');  // 新增红人名称字段

    loadUniqueIds(videoUniqueIdSelect);
    loadProjectBrandManager(videoProjectSelect, videoBrandSelect, videoManagerSelect, videoInfluencerNameSelect);  // 新增红人名称字段
});


// 更新选择框时联动过滤其他选择框的选项
// 填充下拉菜单的通用函数
function populateDropdown(dropdown, items, selectedValue = '') {
    dropdown.innerHTML = ''; // 清空现有选项

    var defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.text = '选择选项';
    dropdown.appendChild(defaultOption);

    items.forEach(function(item) {
        var option = document.createElement('option');
        option.value = item;
        option.text = item;
        if (item === selectedValue) {
            option.selected = true;
        }
        dropdown.appendChild(option);
    });
}

// 更新下拉菜单选项的函数
function updateDropdownOptions(selectedValue, type, formContainer) {
    if (!formContainer) {
        console.error(`Form container is undefined for selected value: ${selectedValue}, type: ${type}. Defaulting to #videoSection.`);
        formContainer = document.querySelector('#videoSection'); // 如果没有定义，则默认到 videoSection
    }

    const projectDropdown = formContainer.querySelector('.videoProjectName');
    const managerDropdown = formContainer.querySelector('.videoManager');
    const influencerDropdown = formContainer.querySelector('.videoInfluencerName'); // 新增红人名称下拉菜单

    if (!projectDropdown || !managerDropdown || !influencerDropdown) { // 检查红人名称下拉菜单是否存在
        console.error('Required elements not found within the form container.');
        return;
    }

    // 记录当前的已选值
    const currentProject = projectDropdown.value;
    const currentManager = managerDropdown.value;
    const currentInfluencer = influencerDropdown.value;

    fetch('/video/get_project_info')
        .then(response => response.json())
        .then(data => {
            let filteredProjects = [];
            let filteredManagers = [];
            let filteredInfluencers = []; // 新增红人名称的过滤

            if (type === 'brand') {
                data.relationships.forEach(function(relation) {
                    if (relation.brand === selectedValue) {
                        filteredProjects.push(relation.project);
                        filteredManagers.push(relation.manager);
                        filteredInfluencers.push(relation.influencer); // 过滤红人名称
                    }
                });
                populateDropdown(projectDropdown, [...new Set(filteredProjects)], currentProject);
                populateDropdown(managerDropdown, [...new Set(filteredManagers)], currentManager);
                populateDropdown(influencerDropdown, [...new Set(filteredInfluencers)], currentInfluencer);

            } else if (type === 'project') {
                data.relationships.forEach(function(relation) {
                    if (relation.project === selectedValue) {
                        filteredManagers.push(relation.manager);
                        filteredInfluencers.push(relation.influencer); // 过滤红人名称
                    }
                });
                populateDropdown(managerDropdown, [...new Set(filteredManagers)], currentManager);
                populateDropdown(influencerDropdown, [...new Set(filteredInfluencers)], currentInfluencer);

            } else if (type === 'manager') {
                data.relationships.forEach(function(relation) {
                    if (relation.manager === selectedValue) {
                        filteredProjects.push(relation.project);
                        filteredInfluencers.push(relation.influencer); // 过滤红人名称
                    }
                });
                populateDropdown(projectDropdown, [...new Set(filteredProjects)], currentProject);
                populateDropdown(influencerDropdown, [...new Set(filteredInfluencers)], currentInfluencer);
            }
        })
        .catch(error => console.error('Error:', error));
}


document.addEventListener('DOMContentLoaded', function() {
    const formContainer = document.querySelector('#videoSection');
    console.log('Form container in DOMContentLoaded:', formContainer);
    if (!formContainer) {
        console.error('Form container #videoSection is not found.');
        return;
    }

    const videoBrand = formContainer.querySelector('#videobrand');
    const videoProject = formContainer.querySelector('#videoProjectName');
    const videoManager = formContainer.querySelector('#videoManager');
    const videoInfluencerName = formContainer.querySelector('#videoInfluencerName');  // 新增红人名称字段

    console.log('Elements found:', { videoBrand, videoProject, videoManager, videoInfluencerName });  // 调试点3

    if (videoBrand) {
        videoBrand.addEventListener('change', function() {
            console.log('Brand changed, updating dropdowns');
            const project = videoProject ? videoProject.value : '';
            const manager = videoManager ? videoManager.value : '';
            const influencerName = videoInfluencerName ? videoInfluencerName.value : '';  // 新增红人名称字段
            updateDropdownOptions(this.value, 'brand', formContainer);
            filterTableByProjectBrandAndManager(project, this.value, manager,influencerName);
        });
    }

    if (videoProject) {
        videoProject.addEventListener('change', function() {
            console.log('Project changed, updating dropdowns');
            const brand = videoBrand ? videoBrand.value : '';
            const manager = videoManager ? videoManager.value : '';
            const influencerName = videoInfluencerName ? videoInfluencerName.value : '';  // 新增红人名称字段
            updateDropdownOptions(this.value, 'project', formContainer);
            filterTableByProjectBrandAndManager(this.value, brand, manager,influencerName);
        });
    }

    if (videoManager) {
        videoManager.addEventListener('change', function() {
            console.log('Manager changed, updating dropdowns');
            const brand = videoBrand ? videoBrand.value : '';
            const project = videoProject ? videoProject.value : '';
            const influencerName = videoInfluencerName ? videoInfluencerName.value : '';  // 新增红人名称字段
            updateDropdownOptions(this.value, 'manager', formContainer);
            filterTableByProjectBrandAndManager(project, brand, this.value,influencerName);
        });
    }

    if (videoInfluencerName) {  // 新增红人名称字段的事件监听
        videoInfluencerName.addEventListener('change', function() {
            console.log('Influencer changed, updating dropdowns');
            const brand = videoBrand ? videoBrand.value : '';
            const project = videoProject ? videoProject.value : '';
            const manager = videoManager ? videoManager.value : '';
            updateDropdownOptions(this.value, 'influencer', formContainer);
            filterTableByProjectBrandAndManager(project, brand, manager, this.value);
        });
    }

    loadUniqueIds(formContainer.querySelector('#videoUniqueId'));
    loadProjectBrandManager(videoProject, videoBrand, videoManager, videoInfluencerName);  // 新增红人名称字段
    updateVideoTable(); // 更新视频表格
});


// 根据项目、品牌和负责人自动筛选表格
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




// 确保页面加载完成后调用 updateVideoTable 函数
document.addEventListener('DOMContentLoaded', function() {
    updateVideoTable();
});




document.getElementById('resetVideoForm').addEventListener('click', function() {
    const form = document.getElementById('videoForm');
    form.reset(); // 重置表单内容
    removeHighlightVideo();

    // 重新加载品牌、项目和负责人选项
    loadProjectBrandManager(
        form.querySelector('.videoProjectName'),
        form.querySelector('.videobrand'),
        form.querySelector('.videoManager'),
        form.querySelector('.videoInfluencerName')
    );

    // 重新启用被禁用的字段
    form.querySelector('.videoProjectName').disabled = false;
    form.querySelector('.videobrand').disabled = false;
    form.querySelector('.videoManager').disabled = false;

    // 处理动态添加的链接块部分
    const dynamicLinkFields = document.querySelectorAll('.linkFields');
    dynamicLinkFields.forEach(function(linkField) {
        // 重新启用动态部分的选择框
        linkField.querySelector('.videoProjectName').disabled = false;
        linkField.querySelector('.videobrand').disabled = false;
        linkField.querySelector('.videoManager').disabled = false;

        // 清空并重新加载动态添加的唯一ID字段
        const uniqueIdField = linkField.querySelector('.videoUniqueId');
        if (uniqueIdField) {
            uniqueIdField.value = '';  // 清空唯一ID字段的值
            reloadAllUniqueIdsForField(uniqueIdField);  // 重新加载唯一ID选项
        }

    });

    updateVideoTable(); // 更新视频表格

    // 重新加载所有唯一ID，恢复为所有可选项
    reloadAllUniqueIds();
});
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
            data.uniqueIds.forEach(function(id) {
                var option = document.createElement('option');
                option.value = id;
                option.text = id;
                uniqueIdField.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching unique IDs:', error));
}

// 删除按钮
document.getElementById('deleteVideoData').addEventListener('click', function() {
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


// 更新产品
document.addEventListener('DOMContentLoaded', function() {
    // 获取产品选项和类型选项
    fetch('/video/get_product_options')
    .then(response => response.json())
    .then(data => {
        console.log('Received data:', data); // 调试输出

        // 处理产品选项
        if (data && Array.isArray(data.product)) {
            var productOptions = document.getElementById('productOptions');
            data.product.forEach(function(product) {
                var option = document.createElement('option');
                option.value = product;
                productOptions.appendChild(option);
            });
        } else {
            console.error('Invalid data format for products:', data);
        }

        // 处理类型选项
        if (data && Array.isArray(data.unique_video_type)) {
            var typeSelects = document.querySelectorAll('.videoType'); // 获取所有类型字段

            typeSelects.forEach(function(typeSelect) {
                data.unique_video_type.forEach(function(type) {
                    var option = document.createElement('option');
                    option.value = type;
                    option.text = type;
                    typeSelect.appendChild(option);
                });

                // 为每个类型字段添加事件监听器
                typeSelect.addEventListener('change', function() {
                    const selectedType = this.value;
                    filterTableByType(selectedType);
                });
            });
        } else {
            console.error('Invalid data format for types:', data);
        }
    })
    .catch(error => console.error('Error fetching product or type options:', error));
});
// 单独的类型字段筛选函数
function filterTableByType(type) {
    const rows = document.querySelectorAll('#videoTable tbody tr');
    rows.forEach(row => {
        const rowType = row.querySelector('td:nth-child(14)').textContent.trim(); // 假设类型字段在第6列

        if (type === '' || rowType === type) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}






// 更新视频数据表格
// 更新下拉菜单选项的函数
document.addEventListener('DOMContentLoaded', function() {
    // 调用函数以更新红人数据表格
    updateVideoTable();
});
// 全局定义 updateVideoTable 函数
function updateVideoTable() {
    fetch('/video/get_video_data', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector('#videoTable tbody');
        tableBody.innerHTML = ''; // 清空表格内容

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
                <td>${row.物流单号 || ''}</td>
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
            filterTableByProjectBrandAndManager(currentProject, currentBrand, currentManager,currentInfluencerName);
        }
    })
    .catch(error => console.error('Error fetching video table data:', error));
}

// 确保页面加载完成后调用 updateVideoTable 函数
document.addEventListener('DOMContentLoaded', function() {
    updateVideoTable();
});
// 重置表单字段和状态
function resetFields(form) {
    // 重置主表单字段
    resetFormBlock(form);

    // 查找所有通过“添加更多链接”生成的子表单块，并重置它们的字段
    var linkFields = form.querySelectorAll('.linkFields');
    linkFields.forEach(function(linkField) {
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




// 新增项目
// 视频新增项目
document.getElementById('addVideoDataButton').addEventListener('click', function() {
    document.getElementById('addVideoDataForm').style.display = 'block';
});
// 关闭模态框
document.getElementById('closeAddVideoForm').onclick = function() {
    document.getElementById('addVideoDataForm').style.display = 'none';
};
// 点击取消按钮关闭模态框
document.getElementById('cancelAddVideoData').addEventListener('click', function() {
    document.getElementById('addVideoDataForm').style.display = 'none';
});

// 在页面加载时获取品牌、项目、产品和负责人信息并填充datalist
document.addEventListener('DOMContentLoaded', function () {
    fetch('/video/get_metrics_options')
        .then(response => response.json())
        .then(data => {
            if (data.brands) {
                var brandOptions = document.getElementById('addBrandOptions');
                data.brands.forEach(function (brand) {
                    var option = document.createElement('option');
                    option.value = brand;
                    brandOptions.appendChild(option);
                });
            }
            if (data.projects) {
                var projectOptions = document.getElementById('addProjectOptions');
                data.projects.forEach(function (project) {
                    var option = document.createElement('option');
                    option.value = project;
                    projectOptions.appendChild(option);
                });
            }
            if (data.products) {
                var productOptions = document.getElementById('addProductOptions');
                data.products.forEach(function (product) {
                    var option = document.createElement('option');
                    option.value = product;
                    productOptions.appendChild(option);
                });
            }
            if (data.managers) {
                var managerOptions = document.getElementById('addManagerOptions');
                data.managers.forEach(function (manager) {
                    var option = document.createElement('option');
                    option.value = manager;
                    managerOptions.appendChild(option);
                });
            }
            if (data.InfluencerNames) {
                var InfluencerNameOptions = document.getElementById('addInfluencerNameOptions');
                data.managers.forEach(function (InfluencerName) {
                    var option = document.createElement('option');
                    option.value = InfluencerName;
                    InfluencerNameOptions.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error fetching metrics options:', error));
});


// 提交新增表单时处理数据
document.getElementById('addVideoData').addEventListener('submit', function (event) {
    event.preventDefault();
    var responseMessage = document.getElementById('responseMessageVideo');
    responseMessage.innerHTML = ''; // 清空之前的信息

    // 获取表单值
    var brandInput = document.getElementById('addbrand').value.trim();
    var projectInput = document.getElementById('addprojectName').value.trim();
    var managerInput = document.getElementById('addmanager').value.trim();
    var influencerNameInput = document.getElementById('addInfluencerName').value.trim();
    var currencyInput = document.getElementById('addcurrency').value.trim();
    var productInput = document.getElementById('addproduct').value.trim();
    var progressInput = document.getElementById('addProgress').value.trim();

    // 获取选择框中的所有选项值
    var brandOptions = Array.from(document.querySelectorAll('#addBrandOptions option')).map(option => option.value);
    var projectOptions = Array.from(document.querySelectorAll('#addProjectOptions option')).map(option => option.value);
    var managerOptions = Array.from(document.querySelectorAll('#addManagerOptions option')).map(option => option.value);
    var influencerNameOptions = Array.from(document.querySelectorAll('#addInfluencerNameList option')).map(option => option.value);
    var currencyOptions = Array.from(document.querySelectorAll('#addcurrency option')).map(option => option.value);
    var productOptions = Array.from(document.querySelectorAll('#addProductOptions option')).map(option => option.value);
    var progressOptions = Array.from(document.querySelectorAll('#addProgressOptions option')).map(option => option.value);

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

    // 如果所有验证通过，组装表单数据并提交
    var formData = {
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

    fetch('/video/add_video_data', {
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
document.getElementById('addresetMetricsForm').addEventListener('click', function() {
    const form = document.getElementById('addVideoData');
    form.reset(); // 重置表单内容

    // 重新加载品牌、项目、负责人和产品选项
    loadAllOptions();
    updateMetricsTable();
});




// 指标定义板块
document.addEventListener('DOMContentLoaded', function() {
    // 初始加载所有选项
    loadAllOptions();

    // 监听品牌、项目和产品的选择变化
    document.getElementById('metricsBrand').addEventListener('change', function() {
        const selectedBrand = this.value;
        updateProjectAndProductOptions(selectedBrand, null, null);
    });

    document.getElementById('metricsProject').addEventListener('change', function() {
        const selectedProject = this.value;
        updateBrandAndProductOptions(null, selectedProject, null);
    });

    document.getElementById('metricsProduct').addEventListener('change', function() {
        const selectedProduct = this.value;
        updateBrandAndProjectOptions(null, null, selectedProduct);
    });

    // 表单提交
    document.getElementById('metricsDefinitionForm').addEventListener('submit', function(event) {
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
        .then(data => {
            responseMessage.innerHTML = `<p>${data.message}</p>`;
            responseMessage.style.color = 'green';
            updateMetricsTable();
        })
        .catch(error => {
            console.error('Error:', error);
            responseMessage.innerHTML = `<p style="color:red;">提交时出错，请重试。</p>`;
        });
    });

    // 表单重置
    document.getElementById('resetMetricsForm').addEventListener('click', function() {
        const form = document.getElementById('metricsDefinitionForm');
        form.reset(); // 重置表单内容

        // 重新加载品牌、项目、负责人和产品选项
        loadAllOptions();
        updateMetricsTable();
    });
});

function loadAllOptions() {
    fetch('video/get_metrics_options')
        .then(response => response.json())
        .then(data => {
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

function populateDatalist(datalistId, items) {
    const datalist = document.getElementById(datalistId);
    datalist.innerHTML = ''; // 清空现有的选项
    items.forEach(function(item) {
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



// 数据表
document.addEventListener('DOMContentLoaded', function() {
    // 调用函数以更新指标定义数据表格
    updateMetricsTable();
});

// 全局定义 updateMetricsTable 函数
function updateMetricsTable() {
    fetch('video/get_metrics_data', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector('#metricsTable tbody');
        tableBody.innerHTML = ''; // 清空表格内容

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
    .catch(error => console.error('Error fetching metrics table data:', error));
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
document.getElementById('deleteMetricsData').addEventListener('click', function() {
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
