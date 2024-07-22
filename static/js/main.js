document.getElementById('influencerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var links = document.getElementById('influencerLinks').value.trim().split('\n');

    // Basic validation
    if (links.length === 0 || links[0] === '') {
        alert("请输入至少一个链接。");
        return;
    }

    var responseMessage = document.getElementById('responseMessageInfluencer');
    responseMessage.innerHTML = '';

    links.forEach(link => {
        responseMessage.innerHTML += `<p>红人链接 ${link} 提交成功。<br>数据抓取中...</p>`;

        fetch('/submit_influencer_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ link: link })
        })
        .then(response => response.json())
        .then(data => {
            responseMessage.innerHTML += `<p>${data.message.replace(/\n/g, '<br>')}</p>`;
        })
        .catch(error => {
            console.error('Error:', error);
            responseMessage.innerHTML += `<p>提交链接 ${link} 时出错，请重试。</p>`;
            responseMessage.style.color = 'red';
        });
    });
});

document.getElementById('videoForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var links = document.getElementById('videoLinks').value.trim().split('\n');

    // Basic validation
    if (links.length === 0 || links[0] === '') {
        alert("请输入至少一个链接。");
        return;
    }

    var responseMessage = document.getElementById('responseMessageVideo');
    responseMessage.innerHTML = '';

    links.forEach(link => {
        responseMessage.innerHTML += `<p>视频链接 ${link} 提交成功。<br>数据抓取中...</p>`;

        fetch('/submit_video_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ link: link })
        })
        .then(response => response.json())
        .then(data => {
            responseMessage.innerHTML += `<p>${data.message.replace(/\n/g, '<br>')}</p>`;
        })
        .catch(error => {
            console.error('Error:', error);
            responseMessage.innerHTML += `<p>提交链接 ${link} 时出错，请重试。</p>`;
            responseMessage.style.color = 'red';
        });
    });
});

document.getElementById('resetInfluencerForm').addEventListener('click', function() {
    document.getElementById('influencerForm').reset();
    document.getElementById('responseMessageInfluencer').innerHTML = '';
});

document.getElementById('resetVideoForm').addEventListener('click', function() {
    document.getElementById('videoForm').reset();
    document.getElementById('responseMessageVideo').innerHTML = '';
});
