document.getElementById('influencerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var uniqueId = uuid.v4();
    var links = document.getElementById('influencerLinks').value.trim().split('\n');
    var responseMessage = document.getElementById('responseMessageInfluencer');
    responseMessage.innerHTML = '';

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
        responseMessage.innerHTML += `<p style="font-size: 14px">链接 ${link} 提交成功...</p>`;
        responseMessage.style.color = 'black';
        fetch('/influencer/submit_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ link: link, id: uniqueId })
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error:', error);
            responseMessage.innerHTML += `<p>提交链接 ${link} 时出错，请重试。</p>`;
            responseMessage.style.color = 'red';

        });
    });

    // 定时任务 - 每隔5秒访问一次 localhost:5000/notice/spider
    const intervalId = setInterval(() => {
        fetch('/notice/spider/celebrity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({id: uniqueId})
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'clean' || data.isSuccess) {
                    clearInterval(intervalId); // 任务完成或任务需要关闭时，清除定时任务
                    updateInfluencerTable()
                }
                if (data.status !== 'wait'){
                responseMessage.innerHTML += `<p style="font-size: 14px">${data.message.replace(/\n/g, '<br>')}</p>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                responseMessage.innerHTML += `<p style="font-size: 14px">访问 http://172.16.11.245:5000/notice/spider 时出错，请重试。</p>`;
                responseMessage.style.color = 'red';
                clearInterval(intervalId);
            });
    }, 5000);
    // 设置30秒的超时定时器
    const timeoutId = setTimeout(() => {
        clearInterval(intervalId);  // 关闭定时任务
    }, 30000);
});


// 更新红人板块
// 在页面加载时获取平台列表
document.addEventListener('DOMContentLoaded', function() {
    fetch('/update/get_platforms')
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
window.onload = function() {
    var platformSelect = document.getElementById('updatePlatform');
    var influencerInput = document.getElementById('updateInfluencerName');
    var datalist = document.getElementById('influencerNames');
    // console.log('Platform Select Element:', platformSelect);
    // console.log('Influencer Input Element:', influencerInput);
    // console.log('Datalist Element:', datalist);
    if (!platformSelect || !influencerInput || !datalist) {
        console.error('必要的 DOM 元素未找到');
        return;
    }

    platformSelect.addEventListener('change', function() {
        var platform = this.value;
        datalist.innerHTML = ''; // 清空现有选项

        if (platform) {
            fetch('/update/get_influencers', {
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
                        datalist.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('获取红人信息时出错:', error);
            });
        }
    });
};

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




document.getElementById('updateInfluencerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    updateInfluencerTable();
    // 移除红色边框
    removeHighlight();
    // 在这里定义 datalist
    var datalist = document.getElementById('influencerNames');

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

    fetch('/update/influencer', {
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
        document.getElementById('responseMessageUpdateInfluencer').innerHTML = data.message;
        document.getElementById('responseMessageUpdateInfluencer').style.color = 'green';
        if (data.updated_fields) {
                let updatedFieldsMessage = '更新的字段: <br>';
                for (const [field, value] of Object.entries(data.updated_fields)) {
                    updatedFieldsMessage += `${field}: ${value}<br>`;
                }
                document.getElementById('responseMessageUpdateInfluencer').innerHTML += updatedFieldsMessage;
            }
        // 重置表单和datalistf
        document.getElementById('updateInfluencerForm').reset();
        datalist.innerHTML = '';  // 清空 datalist
        // 调用 updateInfluencerTable 立即更新表格
        updateInfluencerTable();
    })
    .catch(error => {
        console.error('提交时出错:', error);
        document.getElementById('responseMessageUpdateInfluencer').innerText = '提交时出错，请重试。';
        document.getElementById('responseMessageUpdateInfluencer').style.color = 'red';
    });
});



document.getElementById('resetUpdateInfluencerForm').addEventListener('click', function() {
    document.getElementById('updateInfluencerForm').reset();
    document.getElementById('updateInfluencerName').value = ''; // 确保红人名称没有选中任何选项
    document.getElementById('responseMessageUpdateInfluencer').innerHTML = '';
    // 移除红色边框
    removeHighlight();
    updateInfluencerTable();
});

document.addEventListener('DOMContentLoaded', function() {
    updateInfluencerTable();
});
// 更新数据库表格的函数
function updateInfluencerTable() {
    fetch('/update/get_influencer_data', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector('#influencerTable tbody');
        tableBody.innerHTML = ''; // 清空表格内容

        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="25">没有数据</td></tr>';
        } else {
            data.forEach(row => {
                var date = new Date(row.更新日期);
                var formattedDate = date.toISOString().split('T')[0]; // 格式为 YYYY-MM-DD
                const tr = document.createElement('tr');
                const avatarUrl = row.红人头像地址 || ''; // 保留原始头像地址，即使为空

                tr.innerHTML = `
                    <td><img src="${avatarUrl}" alt="头像" style="width: 50px; height: 50px;"></td>
                    <td>${row.id || ''}</td>
                    <td>${row.平台 || ''}</td>
                    <td><a href="${row.红人主页地址}" target="_blank">${row.红人名称 || ''}</a></td> <!-- 红人名称变为超链接 -->
                    <td>${row.红人全名 || ''}</td>
                    <td>${row.地区 || ''}</td>
                    <td>${row.国家编码 || ''}</td>
                    <td>${row.评级 || ''}</td>
                    <td>${row.粉丝数量 || ''}</td>
                    <td>${row.平均点赞数量 || ''}</td>
                    <td>${row.平均评论数量 || ''}</td>
                    <td>${row.平均播放量 || ''}</td>
                    <td>${row.平均参与率 || ''}</td>
                    <td>${row.邮箱 || ''}</td>
                    <td>${row.地址信息1 || ''}</td>
                    <td>${row.标签功能1 || ''}</td>
                    <td>${row.WhatsApp || ''}</td>
                    <td>${row.地址信息2 || ''}</td>
                    <td>${row.标签功能2 || ''}</td>
                    <td>${row.Discord || ''}</td>
                    <td>${row.地址信息3 || ''}</td>
                    <td>${row.标签功能3 || ''}</td>
                    <td>${formattedDate || ''}</td>
                `;
                tableBody.appendChild(tr);
            });
        }
        // 应用当前筛选条件
        var currentPlatform = document.getElementById('updatePlatform').value;
        var currentInfluencerName = document.getElementById('updateInfluencerName').value;
        filterTableByPlatformAndInfluencerName(currentPlatform, currentInfluencerName);
    })
    .catch(error => {
        console.error('Error fetching influencer table data:', error);
    });
}
document.addEventListener('DOMContentLoaded', function() {
    updateInfluencerTable();
});

// 根据平台和红人名称自动筛选表格
function filterTableByPlatformAndInfluencerName(platform, influencerName) {
    const rows = document.querySelectorAll('#influencerTable tbody tr');
    rows.forEach(row => {
        const rowPlatform = row.querySelector('td:nth-child(3)').textContent.trim();  // 假设平台在第3列
        const rowInfluencerName = row.querySelector('td:nth-child(4)').textContent.trim();  // 假设红人名称在第4列

        // 检查平台和红人名称是否匹配
        if ((platform === "" || rowPlatform === platform) && (influencerName === "" || rowInfluencerName === influencerName)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// 当平台或红人名称改变时，自动筛选表格
document.getElementById('updatePlatform').addEventListener('change', function() {
    var platform = this.value;
    var influencerName = document.getElementById('updateInfluencerName').value;
    filterTableByPlatformAndInfluencerName(platform, influencerName);
});

document.getElementById('updateInfluencerName').addEventListener('change', function() {
    var influencerName = this.value;
    var platform = document.getElementById('updatePlatform').value;
    filterTableByPlatformAndInfluencerName(platform, influencerName);
});

// 确保页面加载完成后调用 updateInfluencerTable 函数
document.addEventListener('DOMContentLoaded', function() {
    updateInfluencerTable();
});


function fetchInfluencerDetails() {
    var platform = document.getElementById('updatePlatform').value;
    var influencerName = document.getElementById('updateInfluencerName').value.trim();

    if (platform && influencerName) {
        fetch('/update/get_influencer_details', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ platform: platform, influencerName: influencerName })
        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                console.log('获取到的数据:', data);

                var countryCodeField = document.getElementById('country_code');
                if (countryCodeField) {
                    countryCodeField.value = data.国家编码 || '';
                }

                var emailField = document.getElementById('email');
                if (emailField) {
                    emailField.value = data.email || '';
                }

                var whatsappField = document.getElementById('whatsapp');
                if (whatsappField) {
                    whatsappField.value = data.whatsapp || '';
                }

                var discordField = document.getElementById('discord');
                if (discordField) {
                    discordField.value = data.discord || '';
                }

                var address1Field = document.getElementById('address1');
                if (address1Field) {
                    address1Field.value = data.地址信息1 || '';
                }

                var address2Field = document.getElementById('address2');
                if (address2Field) {
                    address2Field.value = data.地址信息2 || '';
                }

                var address3Field = document.getElementById('address3');
                if (address3Field) {
                    address3Field.value = data.地址信息3 || '';
                }

                var tag1Field = document.getElementById('tag1');
                if (tag1Field) {
                    tag1Field.value = data.标签功能1 || '';
                }

                var tag2Field = document.getElementById('tag2');
                if (tag2Field) {
                    tag2Field.value = data.标签功能2 || '';
                }

                var tag3Field = document.getElementById('tag3');
                if (tag3Field) {
                    tag3Field.value = data.标签功能3 || '';
                }

                var regionField = document.getElementById('country');
                if (regionField) {
                    regionField.value = data.地区 || '';
                }

                // 高亮显示空字段
                highlightEmptyFields();
            }
        })
        .catch(error => {
            console.error('获取红人详情时出错:', error);
        });
    }
}
// 防抖函数
function debounce(func, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}
// 当平台或红人名称改变时，自动填充其他字段
// 使用防抖功能绑定到输入和选择事件
document.getElementById('updatePlatform').addEventListener('change', debounce(fetchInfluencerDetails, 300));
document.getElementById('updateInfluencerName').addEventListener('change', fetchInfluencerDetails);






function highlightEmptyFields() {
    var fields = [
        'email', 'whatsapp', 'discord', 'address1',
        'address2', 'address3', 'tag1', 'tag2', 'tag3',
        'country', 'country_code'
    ];

    fields.forEach(function(fieldId) {
        var field = document.getElementById(fieldId);
        if (!field.value) {
            field.style.borderColor = 'red'; // 高亮显示为空的字段
        } else {
            field.style.borderColor = ''; // 移除高亮显示
        }
    });
}
function removeHighlight() {
    var fields = [
        'email', 'whatsapp', 'discord', 'address1',
        'address2', 'address3', 'tag1', 'tag2', 'tag3',
        'country', 'country_code'
    ];

    fields.forEach(function(fieldId) {
        var field = document.getElementById(fieldId);
        field.style.borderColor = ''; // 移除红色边框
    });
}






// 更新视频板块
// 表单提交时
document.getElementById('videoForm').addEventListener('submit', function(event) {
    event.preventDefault();
    removeHighlightVideo(); // 移除外层的红框

    // 处理所有动态生成的表单块，移除红框
    const dynamicLinkFields = document.querySelectorAll('.linkFields');
    dynamicLinkFields.forEach(function(linkField) {
        removeHighlightVideoAdd(linkField);
    });

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

    // 定时任务 - 每隔5秒访问一次 localhost:5000/notice/spider/influencersVideo
    const intervalId = setInterval(() => {
        fetch('/notice/spider/influencersVideo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({send_id: uid})
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'clean' || data.isSuccess) {
                    clearInterval(intervalId); // 任务完成或任务需要关闭时，清除定时任务
                    updateVideoTable();
                    clearTimeout(timeoutId);
                }
                if (data.status !== 'wait'){
                    responseMessage.innerHTML += `<p style="font-size: 14px">${data.message.replace(/\n/g, '<br>')}</p>`;
                }

            })
            .catch(error => {
                console.error('Error:', error);
                responseMessage.innerHTML += `<p style="font-size: 14px">访问 http://172.16.11.245:5000/notice/spider/influencersVideo 时出错，请重试。</p>`;
                responseMessage.style.color = 'red';
                clearInterval(intervalId);
                clearTimeout(timeoutId);
            });
    }, 5000);

    // 设置30秒的超时定时器
    const timeoutId = setTimeout(() => {
        clearInterval(intervalId);  // 关闭定时任务
    }, 30000);

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
                estimatedLaunchDate: estimatedLaunchDate
            })
        })
        .then(response => response.json())
        .then(data => {
            responseMessage.innerHTML += `<p>${data.message.replace(/\n/g, '<br>')}</p>`;
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
});

// 更新唯一ID下拉菜单
function updateUniqueIdDropdown(brand, project, manager, influencerName) {
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


// 当品牌、项目或负责人改变时，更新唯一ID下拉菜单
// 当品牌、项目、负责人或红人名称改变时，更新唯一ID下拉菜单
['videobrand', 'videoProjectName', 'videoManager', 'videoInfluencerName'].forEach(function(className) {
    document.getElementById(className).addEventListener('change', function() {
        const brand = document.getElementById('videobrand').value;
        const project = document.getElementById('videoProjectName').value;
        const manager = document.getElementById('videoManager').value;
        const influencerName = document.getElementById('videoInfluencerName').value;
        updateUniqueIdDropdown(brand, project, manager, influencerName);
    });
});
// 选择id后，将数据显示在控件中
document.getElementById('videoUniqueId').addEventListener('change', function(event) {
    const target = event.target;
    // 检查是否是唯一ID的下拉菜单触发了事件
    if (target.classList.contains('videoUniqueId')) {
        var uniqueId = target.value;
        var formContainer = target.closest('.linkFields') || document.getElementById('videoForm');
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
    }

    // 处理品牌、项目、负责人选择事件
    ['videobrand', 'videoProjectName', 'videoManager', 'videoInfluencerName'].forEach(function(className) {  // 新增红人名称字段
        if (target.classList.contains(className)) {
            const formContainer = target.closest('.linkFields') || document.getElementById('videoForm');
            const selectedValue = target.value;
            const type = className === 'videobrand' ? 'brand' : className === 'videoProjectName' ? 'project' : className === 'videoManager' ? 'manager' : 'influencer';
            updateDropdownOptions(selectedValue, type, formContainer);
        }
    });
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
            if (data.influencers) {
                var videoInfluencerNameSelect = document.getElementById('videoInfluencerName');
                data.influencers.forEach(function(influencer) {
                    var option = document.createElement('option');
                    option.value = influencer;
                    option.text = influencer;
                    videoInfluencerNameSelect.appendChild(option);
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



document.addEventListener('DOMContentLoaded', function() {
    var videoUniqueIdSelect = document.getElementById('videoUniqueId');
    var videoProjectSelect = document.getElementById('videoProjectName');
    var videoBrandSelect = document.getElementById('videobrand');
    var videoManagerSelect = document.getElementById('videoManager');
    var videoInfluencerNameSelect = document.getElementById('videoInfluencerName');  // 新增红人名称字段

    loadUniqueIds(videoUniqueIdSelect);
    loadProjectBrandManager(videoProjectSelect, videoBrandSelect, videoManagerSelect, videoInfluencerNameSelect);  // 新增红人名称字段
});




// 更新下拉菜单选项的函数
document.addEventListener('DOMContentLoaded', function() {
    // 调用函数以更新红人数据表格
    updateVideoTable();
});
// 更新视频数据表格
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
            var date = new Date(row.更新日期);
            var formattedDate = date.toISOString().split('T')[0]; // 格式为 YYYY-MM-DD
            var date2 = new Date(row.预估上线时间);
            var formattedDate2 = date2.toISOString().split('T')[0]; // 格式为 YYYY-MM-DD
            var date3 = new Date(row.发布时间);
            var formattedDate3 = date3.toISOString().split('T')[0]; // 格式为 YYYY-MM-DD

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



document.getElementById('resetInfluencerForm').addEventListener('click', function() {
    document.getElementById('influencerForm').reset();
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
        removeHighlightVideoAdd(linkField); // 处理每个动态表单块的去红
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

// 在页面加载时获取项目、品牌和负责人信息并填充datalist
document.addEventListener('DOMContentLoaded', function () {
    fetch('/video/get_project_info')
        .then(response => response.json())
        .then(data => {
            if (data.brands) {
                var brandOptions = document.getElementById('brandOptions');
                data.brands.forEach(function (brand) {
                    var option = document.createElement('option');
                    option.value = brand;
                    brandOptions.appendChild(option);
                });
            }
            if (data.projects) {
                var projectOptions = document.getElementById('projectOptions');
                data.projects.forEach(function (project) {
                    var option = document.createElement('option');
                    option.value = project;
                    projectOptions.appendChild(option);
                });
            }
            if (data.managers) {
                var managerOptions = document.getElementById('managerOptions');
                data.managers.forEach(function (manager) {
                    var option = document.createElement('option');
                    option.value = manager;
                    managerOptions.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error fetching project info:', error));
});

// 提交新增表单时处理数据
document.getElementById('addVideoData').addEventListener('submit', function (event) {
    event.preventDefault();

    var formData = {
        "品牌": document.getElementById('addbrand').value,
        "项目": document.getElementById('addprojectName').value,
        "负责人": document.getElementById('addmanager').value,
        "花费": document.getElementById('addcost').value,
        "币种": document.getElementById('addcurrency').value,
        "产品": document.getElementById('addproduct').value,
        "合作进度": document.getElementById('addProgress').value,
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
            document.getElementById('addVideoDataForm').style.display = 'none';
            updateVideoTable();  // 提交成功后更新表格
        })
        .catch(error => console.error('Error:', error));
});


//
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



