document.getElementById('influencerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var links = document.getElementById('influencerLinks').value.trim().split('\n');
    var responseMessage = document.getElementById('responseMessageInfluencer');
    responseMessage.innerHTML = '';
    // 建立 WebSocket 连接
    var socket = io.connect('http://172.16.11.245:5000');

    // 处理 WebSocket 消息
    socket.on('progress', function(data) {
        responseMessage.innerHTML += `<p>${data.message.replace(/\n/g, '<br>')}</p>`;
    });

    // 检查本次提交中的重复链接
    var uniqueLinks = new Set();
    var duplicateLinks = [];
    links.forEach(link => {
        if (uniqueLinks.has(link)) {
            duplicateLinks.push(link);
        } else {
            uniqueLinks.add(link);
        }
    });
    // 测试
    // if (duplicateLinks.length > 0) {
    //     duplicateLinks.forEach(link => {
    //         responseMessage.innerHTML += `<p>提交链接 ${link} 时出错：该红人链接在本次提交中重复。</p>`;
    //     });
    //     responseMessage.style.color = 'red';
    //     return;
    // }

    // 提交非重复链接
    links.forEach(link => {
        responseMessage.innerHTML += `<p>红人链接 ${link} 提交成功。<br>数据抓取中...</p>`;

        fetch('http://172.16.11.245:5000/influencer/submit_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ link: link })
        })
        .then(response => response.json())
        .then(data => {
            responseMessage.innerHTML += `<p>${data.message.replace(/\n/g, '<br>')}</p>`;
            // 提交成功后，更新表格
    updateInfluencerTable();
        })
        .catch(error => {
            console.error('Error:', error);
            responseMessage.innerHTML += `<p>提交链接 ${link} 时出错，请重试。</p>`;
            responseMessage.style.color = 'red';
        });
    });

});



// 更新红人板块
// 在页面加载时获取平台列表
document.addEventListener('DOMContentLoaded', function() {
    fetch('http://172.16.11.245:5000/update/get_platforms')
        .then(response => response.json())
        .then(data => {
            if (data.platforms) {
                var updatePlatformSelect = document.getElementById('updatePlatform');
                data.platforms.forEach(function(platform) {
                    var option = document.createElement('option');
                    option.value = platform;
                    option.text = platform;
                    updatePlatformSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching platforms:', error);
        });
});
// 当平台选项改变时获取红人信息（针对更新红人表单）
document.getElementById('updatePlatform').addEventListener('change', function() {
    var platform = this.value;
    var datalist = document.getElementById('updateInfluencerName');
    datalist.innerHTML = ''; // 清空现有选项

    if (platform) {
        fetch('http://172.16.11.245:5000/update/get_influencers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ platform: platform })
        })
        .then(response => response.json())
        .then(data => {
            if (data.influencers) {
                data.influencers.forEach(function(name) {
                    var option = document.createElement('option');
                    option.value = name;
                    option.text = name;
                    datalist.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching influencers:', error);
        });
    }
});
document.getElementById('updateInfluencerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var platform = document.getElementById('updatePlatform').value;
    var name = document.getElementById('updateInfluencerName').value;
    var email = document.getElementById('email').value;
    var whatsapp = document.getElementById('whatsapp').value;
    var discord = document.getElementById('discord').value;
    var address1 = document.getElementById('address1').value;
    var address2 = document.getElementById('address2').value;
    var address3 = document.getElementById('address3').value;
    var tag1 = document.getElementById('tag1').value;
    var tag2 = document.getElementById('tag2').value;
    var tag3 = document.getElementById('tag3').value;
    var country = document.getElementById('country').value;
    var country_code = document.getElementById('country_code').value;

    // Basic validation
    if (!platform || !name) {
        alert("请选择平台并输入红人名称。");
        return;
    }

    var responseMessage = document.getElementById('responseMessageUpdateInfluencer');
    responseMessage.innerHTML = '正在提交...';

    fetch('http://172.16.11.245:5000/update/influencer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            platform: platform,
            name: name,
            email: email,
            whatsapp: whatsapp,
            discord: discord,
            address1: address1,
            address2: address2,
            address3: address3,
            tag1: tag1,
            tag2: tag2,
            tag3: tag3,
            country: country,
            country_code: country_code
        })
    })

    .then(response => response.json())
    .then(data => {
        responseMessage.innerHTML = data.message;
        responseMessage.style.color = 'green';
        // 更新成功后，更新表格
    updateInfluencerTable();
    })

    .catch(error => {
        console.error('Error:', error);
        responseMessage.innerText = '提交时出错，请重试。';
        responseMessage.style.color = 'red';
    });

});

document.getElementById('resetUpdateInfluencerForm').addEventListener('click', function() {
    document.getElementById('updateInfluencerForm').reset();
    document.getElementById('responseMessageUpdateInfluencer').innerHTML = '';
});
document.addEventListener('DOMContentLoaded', function() {
    updateInfluencerTable();
});
// 更新数据库表格的函数
function updateInfluencerTable() {
    fetch('http://172.16.11.245:5000/update/get_influencer_data', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector('#influencerTable tbody');
        tableBody.innerHTML = ''; // 清空表格内容

        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="13">没有数据</td></tr>';
        } else {
            data.forEach(row => {
                var date = new Date(row.更新日期);
                var formattedDate = date.toISOString().split('T')[0]; // 格式为 YYYY-MM-DD
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.平台}</td>
                    <td>${row.红人名称}</td>
                    <td>${row.邮箱}</td>
                    <td>${row.WhatsApp}</td>
                    <td>${row.Discord}</td>
                    <td>${row.地址信息1}</td>
                    <td>${row.地址信息2}</td>
                    <td>${row.地址信息3}</td>
                    <td>${row.标签功能1}</td>
                    <td>${row.标签功能2}</td>
                    <td>${row.标签功能3}</td>
                    <td>${row.国家}</td>
                    <td>${row.国家编码}</td>
                    <td>${formattedDate}</td> <!-- 使用格式化后的日期 -->
                `;
                tableBody.appendChild(tr);
            });
        }
    })
    .catch(error => {
        console.error('Error fetching influencer table data:', error);
    });
}




// 更新视频板块
document.getElementById('videoForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var videoLinks = document.getElementById('videoLinks').value.trim();
    var uniqueId = document.getElementById('videoUniqueId').value.trim();
    var projectName = document.getElementById('videoProjectName').value.trim();
    var manager = document.getElementById('videoManager').value.trim();
    var progress = document.getElementById('videoProgress').value.trim();
    var logisticsProgress = document.getElementById('videoLogisticsProgress').value.trim();
    var logisticsNumber = document.getElementById('videoLogisticsNumber').value.trim();
    var cost = document.getElementById('videocost').value.trim();
    var product = document.getElementById('videoproduct').value.trim();
    var estimatedViews = document.getElementById('videoestimatedViews').value.trim();
    var estimatedLaunchDate = document.getElementById('videoestimatedLaunchDate').value.trim();

    var responseMessage = document.getElementById('responseMessageVideo');
    responseMessage.innerHTML = '正在提交...';

    // 检查本次提交中的重复链接
    var uniqueLinks = new Set();
    var duplicateLinks = [];
    var links = videoLinks.split('\n').map(link => link.trim()).filter(link => link !== '');
    links.forEach(link => {
        if (uniqueLinks.has(link)) {
            duplicateLinks.push(link);
        } else {
            uniqueLinks.add(link);
        }
    });

    // 提交非重复链接
    uniqueLinks.forEach(link => {
        responseMessage.innerHTML += `<p>视频链接 ${link} 提交成功。<br>数据抓取中...</p>`;
        fetch('http://172.16.11.236:5000/video/submit_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                link: link,
                uniqueId: uniqueId,
                projectName: projectName,
                manager: manager,
                progress: progress,
                logisticsProgress: logisticsProgress,
                logisticsNumber: logisticsNumber,
                cost: cost,
                product: product,
                estimatedViews: estimatedViews,
                estimatedLaunchDate: estimatedLaunchDate
            })
        })
        .then(response => response.json())
        .then(data => {
            responseMessage.innerHTML += `<p>${data.message.replace(/\n/g, '<br>')}</p>`;
            responseMessage.style.color = 'green';
            // 更新视频表格
            updateVideoTable();
        })
        .catch(error => {
            console.error('Error:', error);
            responseMessage.innerHTML += `<p>提交链接 ${link} 时出错，请重试。</p>`;
            responseMessage.style.color = 'red';
        });
    });
});


// 在页面加载时获取项目和负责人信息
document.addEventListener('DOMContentLoaded', function() {
    fetch('http://172.16.11.236:5000/video/get_project_info')
        .then(response => response.json())
        .then(data => {
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
        })
        .catch(error => {
            console.error('Error fetching project info:', error);
        });
});

// 点击“添加更多链接”
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('addLink').addEventListener('click', function() {
        var container = document.getElementById('linkFieldsContainer');
        var newLinkFields = document.createElement('div');
        newLinkFields.classList.add('linkFields');
        newLinkFields.innerHTML = `
            <hr>
            <div id="linkFieldsContainer">
            <div class="linkFields">
                <label for="videoLinks">视频链接:</label>
                <textarea id="videoLinks" class="videoLinks" placeholder="请输入视频链接"></textarea>

                <div class="form-row">
                    <div>
                        <label for="videoUniqueId">唯一id:</label>
                        <select id="videoUniqueId" class="videoUniqueId" required>
                            <option value="">选择唯一id</option>
                            <!-- 选项将在JavaScript中动态生成 -->
                        </select>
                    </div>
                    <div>
                        <label for="videoProjectName">项目:</label>
                        <select id="videoProjectName" class="videoProjectName">
                            <option value="">选择项目</option>
                            <!-- 选项将在JavaScript中动态生成 -->
                        </select>
                    </div>
                    <div>
                        <label for="videoManager">负责人:</label>
                        <select id="videoManager" class="videoManager">
                            <option value="">选择负责人</option>
                            <!-- 选项将在JavaScript中动态生成 -->
                        </select>
                    </div>
                </div>

                <div class="form-row">
                    <div>
                        <label for="videoProgress">合作进度:</label>
                        <input type="text" id="videoProgress" class="videoProgress" placeholder="请输入合作进度">
                    </div>
                    <div>
                        <label for="videoLogisticsProgress">物流进度:</label>
                        <input type="text" id="videoLogisticsProgress" class="videoLogisticsProgress" placeholder="请输入物流进度">
                    </div>
                    <div>
                        <label for="videoLogisticsNumber">物流单号:</label>
                        <input type="text" id="videoLogisticsNumber" class="videoLogisticsNumber" placeholder="请输入物流单号">
                    </div>
                </div>

                <div class="form-row">
                    <div>
                        <label for="videocost">花费:</label>
                        <input type="number" id="videocost" class="videocost" placeholder="请输入花费">
                    </div>
                    <div>
                        <label for="videoproduct">产品:</label>
                        <input type="text" id="videoproduct" class="videoproduct" placeholder="请输入产品名称">
                    </div>
                    <div>
                        <label for="videoestimatedViews">预估观看量:</label>
                        <input type="number" id="videoestimatedViews" name="videoestimatedViews" placeholder="预估观看量">
                    </div>
                    <div>
                        <label for="videoestimatedLaunchDate">预估上线时间:</label>
                        <input type="date" id="videoestimatedLaunchDate" name="videoestimatedLaunchDate" placeholder="预估上线时间">
                    </div>
                </div>
            </div>
        </div>
            <button type="button" class="removeLink">取消</button>
        `;
        container.appendChild(newLinkFields);
        newLinkFields.querySelector('.removeLink').addEventListener('click', function() {
            container.removeChild(newLinkFields);
        });
    });
});
document.addEventListener('DOMContentLoaded', function() {
    // 调用函数以更新红人数据表格
    updateVideoTable();
});
// 更新视频数据表格
function updateVideoTable() {
    fetch('/video/get_video_data', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector('#videoTable tbody');
        tableBody.innerHTML = ''; // 清空表格内容

        data.forEach(row => {
                // 格式化日期
            var date = new Date(row.更新日期);
            var formattedDate = date.toISOString().split('T')[0]; // 格式为 YYYY-MM-DD
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.id || ''}</td>
                <td>${row.项目 || ''}</td>
                <td>${row.负责人 || ''}</td>
                <td>${row.平台 || ''}</td>
                <td>${row.红人名称 || ''}</td>
                <td>${row.发布时间 || ''}</td>
                <td>${row.播放量 || ''}</td>
                <td>${row.点赞数 || ''}</td>
                <td>${row.评论数 || ''}</td>
                <td>${row.收藏数 || ''}</td>
                <td>${row.转发数 || ''}</td>
                <td>${row.参与率 || ''}</td>
                <td>${row.花费 || ''}</td>
                <td>${row.币种 || ''}</td>
                <td>${row.产品 || ''}</td>
                <td>${row.物流进度 || ''}</td>
                <td>${row.物流单号 || ''}</td>
                <td>${row.预估观看量 || ''}</td>
                <td>${row.预估上线时间 || ''}</td>
                <td>${formattedDate}</td> <!-- 使用格式化后的日期 -->
            `;
            tableBody.appendChild(tr);
        });
    })
    .catch(error => {
        console.error('Error fetching video table data:', error);
    });
}



document.getElementById('resetInfluencerForm').addEventListener('click', function() {
    document.getElementById('influencerForm').reset();
});

document.getElementById('resetVideoForm').addEventListener('click', function() {
    document.getElementById('videoForm').reset();
});


// 包含所有国家和地区的数组及其编码
const countries = [
    { name: "中国大陆", code: "CN" },
    { name: "中国香港", code: "HK" },
    { name: "中国台湾", code: "TW" },
    { name: "美国", code: "US" },
    { name: "英国", code: "UK" },
    { name: "阿富汗", code: "AF" },
    { name: "阿尔巴尼亚", code: "AL" },
    { name: "阿尔及利亚", code: "DZ" },
    { name: "安道尔", code: "AD" },
    { name: "安哥拉", code: "AO" },
    { name: "安提瓜和巴布达", code: "AG" },
    { name: "阿根廷", code: "AR" },
    { name: "亚美尼亚", code: "AM" },
    { name: "澳大利亚", code: "AU" },
    { name: "奥地利", code: "AT" },
    { name: "阿塞拜疆", code: "AZ" },
    { name: "巴哈马", code: "BS" },
    { name: "巴林", code: "BH" },
    { name: "孟加拉国", code: "BD" },
    { name: "巴巴多斯", code: "BB" },
    { name: "白俄罗斯", code: "BY" },
    { name: "比利时", code: "BE" },
    { name: "伯利兹", code: "BZ" },
    { name: "贝宁", code: "BJ" },
    { name: "不丹", code: "BT" },
    { name: "玻利维亚", code: "BO" },
    { name: "波斯尼亚和黑塞哥维那", code: "BA" },
    { name: "博茨瓦纳", code: "BW" },
    { name: "巴西", code: "BR" },
    { name: "文莱", code: "BN" },
    { name: "保加利亚", code: "BG" },
    { name: "布基纳法索", code: "BF" },
    { name: "布隆迪", code: "BI" },
    { name: "佛得角", code: "CV" },
    { name: "柬埔寨", code: "KH" },
    { name: "喀麦隆", code: "CM" },
    { name: "加拿大", code: "CA" },
    { name: "中非共和国", code: "CF" },
    { name: "乍得", code: "TD" },
    { name: "智利", code: "CL" },
    { name: "哥伦比亚", code: "CO" },
    { name: "科摩罗", code: "KM" },
    { name: "刚果共和国", code: "CG" },
    { name: "刚果民主共和国", code: "CD" },
    { name: "哥斯达黎加", code: "CR" },
    { name: "科特迪瓦", code: "CI" },
    { name: "克罗地亚", code: "HR" },
    { name: "古巴", code: "CU" },
    { name: "塞浦路斯", code: "CY" },
    { name: "捷克", code: "CZ" },
    { name: "丹麦", code: "DK" },
    { name: "吉布提", code: "DJ" },
    { name: "多米尼克", code: "DM" },
    { name: "多米尼加共和国", code: "DO" },
    { name: "东帝汶", code: "TL" },
    { name: "厄瓜多尔", code: "EC" },
    { name: "埃及", code: "EG" },
    { name: "萨尔瓦多", code: "SV" },
    { name: "赤道几内亚", code: "GQ" },
    { name: "厄立特里亚", code: "ER" },
    { name: "爱沙尼亚", code: "EE" },
    { name: "斯威士兰", code: "SZ" },
    { name: "埃塞俄比亚", code: "ET" },
    { name: "斐济", code: "FJ" },
    { name: "芬兰", code: "FI" },
    { name: "法国", code: "FR" },
    { name: "加蓬", code: "GA" },
    { name: "冈比亚", code: "GM" },
    { name: "格鲁吉亚", code: "GE" },
    { name: "德国", code: "DE" },
    { name: "加纳", code: "GH" },
    { name: "希腊", code: "GR" },
    { name: "格林纳达", code: "GD" },
    { name: "危地马拉", code: "GT" },
    { name: "几内亚", code: "GN" },
    { name: "几内亚比绍", code: "GW" },
    { name: "圭亚那", code: "GY" },
    { name: "海地", code: "HT" },
    { name: "洪都拉斯", code: "HN" },
    { name: "匈牙利", code: "HU" },
    { name: "冰岛", code: "IS" },
    { name: "印度", code: "IN" },
    { name: "印度尼西亚", code: "ID" },
    { name: "伊朗", code: "IR" },
    { name: "伊拉克", code: "IQ" },
    { name: "爱尔兰", code: "IE" },
    { name: "以色列", code: "IL" },
    { name: "意大利", code: "IT" },
    { name: "牙买加", code: "JM" },
    { name: "日本", code: "JP" },
    { name: "约旦", code: "JO" },
    { name: "哈萨克斯坦", code: "KZ" },
    { name: "肯尼亚", code: "KE" },
    { name: "基里巴斯", code: "KI" },
    { name: "朝鲜", code: "KP" },
    { name: "韩国", code: "KR" },
    { name: "科威特", code: "KW" },
    { name: "吉尔吉斯斯坦", code: "KG" },
    { name: "老挝", code: "LA" },
    { name: "拉脱维亚", code: "LV" },
    { name: "黎巴嫩", code: "LB" },
    { name: "莱索托", code: "LS" },
    { name: "利比里亚", code: "LR" },
    { name: "利比亚", code: "LY" },
    { name: "列支敦士登", code: "LI" },
    { name: "立陶宛", code: "LT" },
    { name: "卢森堡", code: "LU" },
    { name: "马达加斯加", code: "MG" },
    { name: "马拉维", code: "MW" },
    { name: "马来西亚", code: "MY" },
    { name: "马尔代夫", code: "MV" },
    { name: "马里", code: "ML" },
    { name: "马耳他", code: "MT" },
    { name: "马绍尔群岛", code: "MH" },
    { name: "毛里塔尼亚", code: "MR" },
    { name: "毛里求斯", code: "MU" },
    { name: "墨西哥", code: "MX" },
    { name: "密克罗尼西亚", code: "FM" },
    { name: "摩尔多瓦", code: "MD" },
    { name: "摩纳哥", code: "MC" },
    { name: "蒙古", code: "MN" },
    { name: "黑山", code: "ME" },
    { name: "摩洛哥", code: "MA" },
    { name: "莫桑比克", code: "MZ" },
    { name: "缅甸", code: "MM" },
    { name: "纳米比亚", code: "NA" },
    { name: "瑙鲁", code: "NR" },
    { name: "尼泊尔", code: "NP" },
    { name: "荷兰", code: "NL" },
    { name: "新西兰", code: "NZ" },
    { name: "尼加拉瓜", code: "NI" },
    { name: "尼日尔", code: "NE" },
    { name: "尼日利亚", code: "NG" },
    { name: "挪威", code: "NO" },
    { name: "阿曼", code: "OM" },
    { name: "巴基斯坦", code: "PK" },
    { name: "帕劳", code: "PW" },
    { name: "巴勒斯坦", code: "PS" },
    { name: "巴拿马", code: "PA" },
    { name: "巴布亚新几内亚", code: "PG" },
    { name: "巴拉圭", code: "PY" },
    { name: "秘鲁", code: "PE" },
    { name: "菲律宾", code: "PH" },
    { name: "波兰", code: "PL" },
    { name: "葡萄牙", code: "PT" },
    { name: "卡塔尔", code: "QA" },
    { name: "罗马尼亚", code: "RO" },
    { name: "俄罗斯", code: "RU" },
    { name: "卢旺达", code: "RW" },
    { name: "圣基茨和尼维斯", code: "KN" },
    { name: "圣卢西亚", code: "LC" },
    { name: "圣文森特和格林纳丁斯", code: "VC" },
    { name: "萨摩亚", code: "WS" },
    { name: "圣马力诺", code: "SM" },
    { name: "圣多美和普林西比", code: "ST" },
    { name: "沙特阿拉伯", code: "SA" },
    { name: "塞内加尔", code: "SN" },
    { name: "塞尔维亚", code: "RS" },
    { name: "塞舌尔", code: "SC" },
    { name: "塞拉利昂", code: "SL" },
    { name: "新加坡", code: "SG" },
    { name: "斯洛伐克", code: "SK" },
    { name: "斯洛文尼亚", code: "SI" },
    { name: "所罗门群岛", code: "SB" },
    { name: "索马里", code: "SO" },
    { name: "南非", code: "ZA" },
    { name: "南苏丹", code: "SS" },
    { name: "西班牙", code: "ES" },
    { name: "斯里兰卡", code: "LK" },
    { name: "苏丹", code: "SD" },
    { name: "苏里南", code: "SR" },
    { name: "斯威士兰", code: "SZ" },
    { name: "瑞典", code: "SE" },
    { name: "瑞士", code: "CH" },
    { name: "叙利亚", code: "SY" },
    { name: "塔吉克斯坦", code: "TJ" },
    { name: "坦桑尼亚", code: "TZ" },
    { name: "泰国", code: "TH" },
    { name: "多哥", code: "TG" },
    { name: "汤加", code: "TO" },
    { name: "特立尼达和多巴哥", code: "TT" },
    { name: "突尼斯", code: "TN" },
    { name: "土耳其", code: "TR" },
    { name: "土库曼斯坦", code: "TM" },
    { name: "图瓦卢", code: "TV" },
    { name: "乌干达", code: "UG" },
    { name: "乌克兰", code: "UA" },
    { name: "阿联酋", code: "AE" },
    { name: "乌拉圭", code: "UY" },
    { name: "乌兹别克斯坦", code: "UZ" },
    { name: "瓦努阿图", code: "VU" },
    { name: "梵蒂冈", code: "VA" },
    { name: "委内瑞拉", code: "VE" },
    { name: "越南", code: "VN" },
    { name: "也门", code: "YE" },
    { name: "赞比亚", code: "ZM" },
    { name: "津巴布韦", code: "ZW" }
];


// 获取datalist元素
const datalistCountries = document.getElementById('countries');
const datalistCountryCodes = document.getElementById('country_codes');

// 动态生成选项并添加到datalist中
countries.forEach(country => {
    const optionCountry = document.createElement('option');
    optionCountry.value = country.name;
    datalistCountries.appendChild(optionCountry);

    const optionCode = document.createElement('option');
    optionCode.value = country.code;
    datalistCountryCodes.appendChild(optionCode);
});




// 自动填充国家编码或国家名称
function fillCountryDetails(type) {
    const countryInput = document.getElementById('country').value;
    const countryCodeInput = document.getElementById('country_code').value;

    if (type === 'name') {
        const foundCountry = countries.find(country => country.name.toLowerCase() === countryInput.toLowerCase());
        if (foundCountry) {
            document.getElementById('country_code').value = foundCountry.code;
        } else {
            document.getElementById('country_code').value = '';
        }
    } else if (type === 'code') {
        const foundCountry = countries.find(country => country.code.toUpperCase() === countryCodeInput.toUpperCase());
        if (foundCountry) {
            document.getElementById('country').value = foundCountry.name;
        } else {
            document.getElementById('country').value = '';
        }
    }
}


// 视频新增项目
// 视频新增项目
document.getElementById('addVideoDataButton').addEventListener('click', function() {
    document.getElementById('addVideoDataForm').style.display = 'block';
});

document.getElementById('cancelAddVideoData').addEventListener('click', function() {
    document.getElementById('addVideoDataForm').style.display = 'none';
});

document.getElementById('addVideoData').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = {
        "项目": document.getElementById('addprojectName').value,
        "负责人": document.getElementById('addmanager').value,
        "花费": document.getElementById('addcost').value,
        "币种": document.getElementById('addcurrency').value,
        "产品": document.getElementById('addproduct').value,
        "合作进度": document.getElementById('addProgress').value,
        "预估观看量": document.getElementById('addestimatedViews').value,
        "预估上线时间": document.getElementById('addestimatedLaunchDate').value
    };

    fetch('http://172.16.11.236:5000/video/add_video_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('addVideoDataForm').style.display = 'none';
        updateVideoTable();  // 提交成功后更新表格
    })
    .catch(error => console.error('Error:', error));
});
