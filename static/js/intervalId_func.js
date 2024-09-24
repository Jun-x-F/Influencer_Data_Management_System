function startFetchSpiderNoticeWithTimeout(url_path, responseMessage, uniqueId, timeout, updateCallback) {
    const url = '/notice/spider/'+url_path
    let timeoutId;
    const intervalId = setInterval(() => {
        fetch(url,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({id: uniqueId})
            })
            .then(response => response.json())
            .then(data => {
                const messages = data.message;
                messages.forEach((msgObj,index)=>{
                    let color;
                    let weight;
                    switch (msgObj.status) {
                        case 'error':
                            color = '#dc3545';
                            weight = 'bold';
                            break;
                        case 'finish':
                            color = '#f57c00';
                            weight = 'bold';
                            break;
                        default:
                            color = 'green';
                            weight = 'normal';
                            break;
                    }
                    responseMessage.innerHTML += `<p style="font-size: 14px; color: ${color}; font-weight:${weight}">${msgObj.message}<br></p>`;
                    // 强制滚动到最底部
                    responseMessage.scrollTop = responseMessage.scrollHeight;
                })

                if (data.status === "finish" || data.status === "error"){
                    updateCallback()
                    clearInterval(intervalId); // 请求错误时清除定时任务
                    clearTimeout(timeoutId);   // 清除超时定时器
                }else {
                    // 重置超时定时器
                    clearTimeout(timeoutId);
                    timeoutId = setTimeout(() => {
                        clearInterval(intervalId);  // 超时时间到后关闭定时任务
                        console.log('定时任务因超时120s被清除');
                    }, 120000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                responseMessage.innerHTML += `<p style="font-size: 14px">访问 ${url} 时出错，请重试。</p>`;
                responseMessage.style.color = 'red';
                clearInterval(intervalId); // 请求错误时清除定时任务
                clearTimeout(timeoutId);   // 清除超时定时器
            });
    }, timeout);


    return {intervalId, timeoutId}; // 返回 intervalId 和 timeoutId 以便外部控制
}
