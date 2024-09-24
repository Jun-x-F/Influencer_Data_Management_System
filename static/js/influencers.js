document.getElementById('influencerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var uniqueId = uuid.v4();
    var links = document.getElementById('influencerLinks').value.trim().split('\n');
    var responseMessage = document.getElementById('responseMessageInfluencer');
    // 定义需要排除的子字符串列表
    const excludedSubstrings = [
        '/reel/', '/video/', '/watch/',
        '/video?', '/watch?', '/reel?',
        '/p/', '/p?', '/shorts/', '/shorts?'
    ];

    responseMessage.innerHTML = '';

    // 检查本次提交中的重复链接
    var uniqueLinks = new Set();
    var duplicateLinks = [];
    links.forEach(link => {
        const containsExcluded = excludedSubstrings.some(substring => link.includes(substring));
        if (link.indexOf("http") === -1){
            if (!duplicateLinks.some(item => item.link === link && item.message === "这不是链接格式！！！")) {
                duplicateLinks.push({ link: link, message: "这不是链接格式！！！" });
            }
        }
        else if (containsExcluded) {
            // 检查 duplicateLinks 中是否已存在相同的 link 和 message
            if (!duplicateLinks.some(item => item.link === link && item.message === "这是视频链接，不是红人链接！！！")) {
                duplicateLinks.push({ link: link, message: "这是视频链接，不是红人链接！！！" });
            }
        } else if (uniqueLinks.has(link)) {
            // 检查 duplicateLinks 中是否已存在相同的 link 和 message
            if (!duplicateLinks.some(item => item.link === link && item.message === "链接重复了！！！")) {
                duplicateLinks.push({ link: link, message: "链接重复了！！！" });
            }
        } else {
            uniqueLinks.add(link);
        }
    });

    // 在循环结束后，如果存在被排除的链接，显示弹窗
    if (duplicateLinks.length > 0) {
        Swal.fire({
            title: '以下链接有问题，请查看',
            html: '<h3 class="subtitle">其余链接正常执行</h3>' +
                '<div class="swal-scrollable-content">'+
                '<ul class="link-list">' + duplicateLinks.map(item => `<li style="text-align: center"><span class="link-text">${item.link}</span> - <span class="error-message">${item.message}</span></li>`).join('') + '</ul>'
                + '</div>',
            icon: 'error',
            confirmButtonText: '确定',
            width: '700px',
            background: '#f9f9f9',
            confirmButtonColor: '#3085d6',
        });
    }

    // 测试
    // if (duplicateLinks.length > 0) {
    //     duplicateLinks.forEach(link => {
    //         responseMessage.innerHTML += `<p>提交链接 ${link} 时出错：该红人链接在本次提交中重复。</p>`;
    //     });
    //     responseMessage.style.color = 'red';
    //     return;
    // }

    // 提交非重复链接
    uniqueLinks.forEach(link => {
        responseMessage.innerHTML += `<p style="font-size: 14px">链接 ${link} 提交成功...</p>`;
        responseMessage.style.color = 'black';
        fetch('/influencer/submit_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ link: link, id: uniqueId })
        })
        .catch(error => {
            console.error('Error:', error);
            responseMessage.innerHTML += `<p>提交链接 ${link} 时出错，请重试。</p>`;
            responseMessage.style.color = 'red';
        });
    });

    // 定时任务 - 每隔5秒访问一次 localhost:5000/notice/spider
    const {intervalId, timeoutId} = startFetchSpiderNoticeWithTimeout('influencer', responseMessage, uniqueId, 5000, updateInfluencerTable);
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
    console.log('Platform Select Element:', platformSelect);
    console.log('Influencer Input Element:', influencerInput);
    console.log('Datalist Element:', datalist);
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
                    console.log('Received influencers:', data.influencers);
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

// 定义缓存键
const InfluencerDataCacheKey = 'influencerData';

/**
 * 清除视频表格的缓存
 */
function clearInfluencerDataCache() {
    localStorage.removeItem(InfluencerDataCacheKey);
}

/**
 * 设置视频表格的缓存数据
 * @param {Array} data - 要缓存的视频数据
 */
function setInfluencerDataCache(data) {
    localStorage.setItem(InfluencerDataCacheKey, JSON.stringify(data));
}

/**
 * 获取视频表格的缓存数据
 * @returns {Array|null} - 返回缓存的数据数组或 null（如果没有缓存）
 */
function getInfluencerDataCache() {
    const cachedData = localStorage.getItem(InfluencerDataCacheKey);
    return cachedData ? JSON.parse(cachedData) : null;
}


document.getElementById('updateInfluencerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // updateInfluencerTable();
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

    const cacheData = getInfluencerDataCache()

    // 检查名称是否存在
    if (cacheData && cacheData.some(item => item['红人名称'] !== name)) {
        console.log(`名称 "${name}" 不存在于缓存数据中。`);
        Swal.fire({
            title: '红人数据不存在',
            html: `
        <h3 class="subtitle">没有这个红人数据，先提交红人链接进行抓取！</h3>
        <div class="swal-scrollable-content">
            <ul class="link-list">
                <li style="text-align: center; font-size: 14px;">
                    <span class="link-text">${name}</span> -  
                    <span class="error-message">没有这个红人姓名的数据！！！</span>
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
        return;
    }

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

function updateInfluencerTable() {
    // 清除本地缓存中的数据
    clearInfluencerDataCache();

    fetch('/update/get_influencer_data', {
        method: 'GET'
    })
        .then(response => response.json())
        .then(data => {
            // 将数据存储到本地缓存中
            setInfluencerDataCache(data);
            console.log(getInfluencerDataCache())
            // 使用数据更新表格
            renderInfluencerTable(data);

            // 应用当前筛选条件
            var currentPlatform = document.getElementById('updatePlatform').value;
            var currentInfluencerName = document.getElementById('updateInfluencerName').value;
            filterTableByPlatformAndInfluencerName(currentPlatform, currentInfluencerName);
        })
        .catch(error => {
            console.error('Error fetching influencer table data:', error);
        });
}

// 渲染表格的函数
function renderInfluencerTable(data) {
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
                <td>${row.平台 || ''}</td>
                <td><a href="${row.红人主页地址}" target="_blank">${row.红人名称 || ''}</a></td> <!-- 红人名称变为超链接 -->
                <td>${row.红人全名 || ''}</td>
                <td>${row.地区 || ''}</td>
                <td>${row.国家编码 || ''}</td>
                <td>${row.评级 || ''}</td>
                <td>${row.粉丝数量 || ''}</td>
                <td>${row.平均播放量 || ''}</td>
                <td>${row.平均点赞数量 || ''}</td>
                <td>${row.平均评论数量 || ''}</td>
                <td>${row.平均参与率 || ''}</td>
                <td>${row.邮箱 || ''}</td>
                <td>${row.WhatsApp || ''}</td>
                <td>${row.Discord || ''}</td>
                <td>${row.地址信息1 || ''}</td>
                <td>${row.地址信息2 || ''}</td>
                <td>${row.地址信息3 || ''}</td>
                <td>${row.标签功能1 || ''}</td>
                <td>${row.标签功能2 || ''}</td>
                <td>${row.标签功能3 || ''}</td>
                <td>${formattedDate || ''}</td>
            `;
            tableBody.appendChild(tr);
        });
    }
}


// // 更新数据库表格的函数
// function updateInfluencerTable() {
//     fetch('/update/get_influencer_data', {
//         method: 'GET'
//     })
//     .then(response => response.json())
//     .then(data => {
//         const tableBody = document.querySelector('#influencerTable tbody');
//         tableBody.innerHTML = ''; // 清空表格内容
//
//         if (data.length === 0) {
//             tableBody.innerHTML = '<tr><td colspan="25">没有数据</td></tr>';
//         } else {
//             data.forEach(row => {
//                 var date = new Date(row.更新日期);
//                 var formattedDate = date.toISOString().split('T')[0]; // 格式为 YYYY-MM-DD
//                 const tr = document.createElement('tr');
//                 const avatarUrl = row.红人头像地址 || ''; // 保留原始头像地址，即使为空
//
//                 tr.innerHTML = `
//                     <td><img src="${avatarUrl}" alt="头像" style="width: 50px; height: 50px;"></td>
//                     <td>${row.平台 || ''}</td>
//                     <td><a href="${row.红人主页地址}" target="_blank">${row.红人名称 || ''}</a></td> <!-- 红人名称变为超链接 -->
//                     <td>${row.红人全名 || ''}</td>
//                     <td>${row.地区 || ''}</td>
//                     <td>${row.国家编码 || ''}</td>
//                     <td>${row.评级 || ''}</td>
//                     <td>${row.粉丝数量 || ''}</td>
//                     <td>${row.平均播放量 || ''}</td>
//                     <td>${row.平均点赞数量 || ''}</td>
//                     <td>${row.平均评论数量 || ''}</td>
//                     <td>${row.平均参与率 || ''}</td>
//                     <td>${row.邮箱 || ''}</td>
//                     <td>${row.WhatsApp || ''}</td>
//                     <td>${row.Discord || ''}</td>
//                     <td>${row.地址信息1 || ''}</td>
//                     <td>${row.地址信息2 || ''}</td>
//                     <td>${row.地址信息3 || ''}</td>
//                     <td>${row.标签功能1 || ''}</td>
//                     <td>${row.标签功能2 || ''}</td>
//                     <td>${row.标签功能3 || ''}</td>
//                     <td>${formattedDate || ''}</td>
//                 `;
//                 tableBody.appendChild(tr);
//             });
//         }
//         // 应用当前筛选条件
//         var currentPlatform = document.getElementById('updatePlatform').value;
//         var currentInfluencerName = document.getElementById('updateInfluencerName').value;
//         filterTableByPlatformAndInfluencerName(currentPlatform, currentInfluencerName);
//     })
//     .catch(error => {
//         console.error('Error fetching influencer table data:', error);
//     });
// }

// 根据平台和红人名称自动筛选表格
function filterTableByPlatformAndInfluencerName(platform, influencerName) {
    const rows = document.querySelectorAll('#influencerTable tbody tr');
    rows.forEach(row => {
        const rowPlatform = row.querySelector('td:nth-child(2)').textContent.trim();  // 假设平台在第3列
        const rowInfluencerName = row.querySelector('td:nth-child(3)').textContent.trim();  // 假设红人名称在第4列

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






