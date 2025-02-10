from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from spider.youtube.base_youtube_spider import YouTubeSpider


def youtube_video_spider(url):
    spider = YouTubeSpider(
        proxy_port=7890,
        save_raw=False,
        calc_engagement=True  # 启用参与率计算
    )
    # 使用完整URL
    result = spider.fetch_video(url)
    inner_InfluencersVideoProjectData(result)
    inner_InfluencersVideoProjectDataByDate(result)