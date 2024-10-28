/**
 * 判断 URL 是否为 YouTube URL（youtu.be 或 youtube.com），并提取视频 ID。
 *
 * @param {string} url - 需要解析的 URL。
 * @returns {string|null} - 返回视频 ID，如果 URL 不是有效的 YouTube URL 或无法提取 ID，则返回 null。
 */
function getYouTubeVideoID(url) {
    try {
        const parsedUrl = new URL(url);
        const hostname = parsedUrl.hostname.toLowerCase();
        let videoID = null;

        if (hostname === 'youtu.be') {
            // 对于 youtu.be，视频 ID 在 pathname 中
            // 例如: https://youtu.be/Q1QsXfiqSmI?si=pqgd1JdBxWv0i8yl&t=160
            videoID = parsedUrl.pathname.slice(1); // 去掉开头的斜杠 '/'
        } else if (hostname === 'www.youtube.com' || hostname === 'youtube.com' || hostname === 'm.youtube.com') {
            // 对于 youtube.com，视频 ID 通常在查询参数 'v' 中
            // 例如: https://www.youtube.com/watch?v=Q1QsXfiqSmI&t=160s
            videoID = parsedUrl.searchParams.get('v');

            // 有时，YouTube URL 可能是 /embed/VIDEO_ID 或其他格式
            if (!videoID) {
                const pathMatch = parsedUrl.pathname.match(/\/(?:embed|shorts)\/([a-zA-Z0-9_-]{11})/);
                if (pathMatch && pathMatch[1]) {
                    videoID = pathMatch[1];
                }
            }
        }

        // 验证视频 ID 是否符合 YouTube 视频 ID 的格式
        if (videoID && /^[a-zA-Z0-9_-]{11}$/.test(videoID)) {
            return videoID;
        } else {
            console.warn('未能从 URL 中提取有效的 YouTube 视频 ID。');
            console.error(url)
            return null;
        }

    } catch (error) {
        console.error('无效的 URL:', error);
        return null;
    }
}