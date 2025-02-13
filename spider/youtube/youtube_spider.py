import json
import os
import re
from datetime import datetime, date
from json import JSONEncoder
from typing import Optional, Dict, Any, List

import requests
from log.logger import global_log
from spider.sql.data_inner_db import inner_CelebrityProfile
from spider.youtube.base_youtube_spider import YouTubeSpider
from tool.download_file import download_image_file
from tool.grading_criteria import grade_criteria
from tool.ua_pool import get_random_user_agent, parse_ua


class DateTimeEncoder(JSONEncoder):
    """自定义JSON编码器，处理datetime和date对象的序列化"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


class YouTubeChannelSpider:
    """YouTube频道数据爬取类"""
    
    # 单位换算表
    CONVERT_WORDS_TO_NUMBERS = {
        "万": 10000,
        "m": 10000,
        "M": 10000,
        "k": 1000,
        "K": 1000,
        "千": 1000,
    }
    
    def __init__(self, proxy_port: int = 7890, save_raw: bool = True):
        """
        初始化YouTube频道爬虫
        
        Args:
            proxy_port: 本地代理端口号，默认7890
            save_raw: 是否保存原始数据，默认True
        """
        self.proxy = {
            'http': f'http://127.0.0.1:{proxy_port}',
            'https': f'http://127.0.0.1:{proxy_port}'
        }
        self.save_raw = save_raw
        self.base_spider = YouTubeSpider(proxy_port=proxy_port, save_raw=False)
        
        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _download_avatar(self, avatar_url: str, user_name: str) -> str:
        """
        下载头像
        
        Args:
            avatar_url: 头像URL
            user_name: 用户名
            
        Returns:
            str: 头像在数据库中的URL
        """
        try:
            # 处理用户名，将空格替换为下划线
            safe_user_name = user_name.replace(' ', '_')
            return download_image_file(avatar_url, safe_user_name)
        except Exception as e:
            global_log.error(f"下载头像出错: {e}")
            return avatar_url
    
    @staticmethod
    def _convert_follower_count(text: str) -> Optional[int]:
        """
        转换粉丝数量，处理单位换算
        
        Args:
            text: 粉丝数文本，如"3.34万位订阅者"
            
        Returns:
            int: 换算后的粉丝数
        """
        try:
            # 提取数字部分
            number = float(''.join([c for c in text if c.isdigit() or c == '.']))
            
            # 检查单位并换算
            for unit, multiplier in YouTubeChannelSpider.CONVERT_WORDS_TO_NUMBERS.items():
                if unit in text:
                    return int(number * multiplier)
            
            return int(number)
        except Exception as e:
            global_log.error(f"转换粉丝数量出错: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """生成随机请求头"""
        user_agent = get_random_user_agent("Chrome")
        ua_info = parse_ua(user_agent)
        
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": ua_info["sec-ch-ua"],
            "sec-ch-ua-mobile": ua_info["sec-ch-ua-mobile"],
            "sec-ch-ua-platform": ua_info["sec-ch-ua-platform"],
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": user_agent
        }
    
    def _get_cookies(self) -> Dict[str, str]:
        """获取YouTube cookies"""
        return {
            "YSC": "Rn4dOQv0n90",
            "VISITOR_INFO1_LIVE": "u9nH2mhD2G0",
            "VISITOR_PRIVACY_METADATA": "CgJTRxIEGgAgOg%3D%3D",
            "PREF": "tz=Asia.Shanghai&f6=40000000&f7=100",
            "GPS": "1"
        }
    
    @staticmethod
    def _extract_channel_id(url: str) -> Optional[str]:
        """
        从YouTube频道URL中提取频道ID或用户名
        
        Args:
            url: YouTube频道URL
            
        Returns:
            str: 频道ID或用户名，如果无法提取则返回None
        """
        try:
            if '@' in url:
                return url.split('@')[-1].split('/')[0]
            elif 'channel/' in url:
                return url.split('channel/')[-1].split('/')[0]
            elif 'user/' in url:
                return url.split('user/')[-1].split('/')[0]
            return None
        except Exception as e:
            global_log.error(f"提取频道ID出错: {e}")
            return None
    
    def _extract_video_urls(self, data: Dict[str, Any], limit: int = 10) -> List[str]:
        """
        从ytInitialData中提取最新的视频URL
        
        Args:
            data: ytInitialData数据
            limit: 限制获取的视频数量，默认10条
            
        Returns:
            List[str]: 视频URL列表
        """
        video_urls = []
        try:
            # 获取tabs列表
            tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
            # 遍历tabs找到视频标签
            for tab in tabs:
                tab_renderer = tab.get('tabRenderer', {})
                
                # 检查是否为视频标签
                if tab_renderer.get('title', '').lower() == 'videos' or tab_renderer.get('title', '').lower() == '视频':
                    # 获取视频内容列表
                    contents = tab_renderer.get('content', {}).get('richGridRenderer', {}).get('contents', [])
                    global_log.info(f"获取到视频内容列表: {contents}")
                    # 遍历视频内容
                    for content in contents:
                        global_log.info(f"当前已获取的视频URL: {video_urls}")
                        if len(video_urls) >= limit:
                            break
                            
                        try:
                            # 获取视频URL
                            video_data = content.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
                            global_log.info(f"获取到视频数据: {video_data}")
                            url = video_data.get('navigationEndpoint', {}).get('commandMetadata', {}).get('webCommandMetadata', {}).get('url')
                            global_log.info(f"提取的URL: {url}")
                            if url:
                                video_url = f"https://www.youtube.com{url}"
                                video_urls.append(video_url)
                                global_log.info(f"找到视频URL: {video_url}")
                        except Exception as e:
                            global_log.error(f"处理单个视频数据时出错: {e}")
                            continue
                    
                    # 找到视频标签后就可以退出tabs循环
                    break
            
            if not video_urls:
                global_log.info("未找到视频URL")
            else:
                global_log.info(f"总共找到 {len(video_urls)} 个视频URL")
                
        except Exception as e:
            global_log.error(f"提取视频URL时出错: {e}")
        
        return video_urls[:limit]
    
    def _calculate_averages(self, video_data_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算平均值"""
        total_likes = 0
        total_comments = 0
        total_views = 0
        total_engagement_rate = 0.0
        valid_count = len(video_data_list)
        
        for data in video_data_list:
            total_likes += data.get('likes', 0) or 0
            total_comments += data.get('comments', 0) or 0
            total_views += data.get('views', 0) or 0
            total_engagement_rate += data.get('engagement_rate', 0.0) or 0.0
        
        if valid_count > 0:
            return {
                'average_likes': round(total_likes / valid_count, 2),
                'average_comments': round(total_comments / valid_count, 2),
                'average_views': round(total_views / valid_count, 2),
                'average_engagement_rate': round(total_engagement_rate / valid_count, 4)
            }
        return {
            'average_likes': 0.0,
            'average_comments': 0.0,
            'average_views': 0.0,
            'average_engagement_rate': 0.0
        }
    
    def fetch_channel(self, url: str, output_dir: str = "output") -> Optional[Dict[str, Any]]:
        """
        获取YouTube频道最新10条视频数据并计算平均值
        
        Args:
            url: YouTube频道URL
            output_dir: 输出目录，默认为output
            
        Returns:
            Dict[str, Any]: 频道数据，格式符合CelebrityProfile，如果失败则返回None
        """
        # 提取频道ID或用户名
        channel_id = self._extract_channel_id(url)
        if not channel_id:
            global_log.error("无效的YouTube频道URL")
            return None
        # 检查URL是否包含/videos路径,如果没有则添加
        # 移除URL中的查询参数
        url = url.split('?')[0]
        # 移除URL末尾的斜杠和其他路径，只保留基本频道URL
        base_url = url.split('/')[0:4]
        url = '/'.join(base_url)
        global_log.info(f"修改后的url为 {url}")
        # 添加/videos路径
        if not url.endswith('/videos'):
            url = url.rstrip('/') + '/videos'
        global_log.info(f"处理YouTube频道URL: {url}")
        # 创建频道专属的输出目录
        channel_output_dir = os.path.join(output_dir, channel_id)
        if not os.path.exists(channel_output_dir):
            os.makedirs(channel_output_dir)
        
        try:
            # 获取频道页面数据
            response = requests.get(
                url,
                headers=self._get_headers(),
                cookies=self._get_cookies(),
                proxies=self.proxy,
                timeout=30,
                verify=False
            )
            response.raise_for_status()
            global_log.info(f"请求状态码: {response.status_code}")
            
            # 保存原始HTML
            if self.save_raw:
                html_file = os.path.join(channel_output_dir, "raw.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                global_log.info(f"原始HTML已保存到: {html_file}")
            
            # 提取ytInitialData
            pattern = r'<script nonce="[^"]*">var ytInitialData = ({.*?});</script>'
            match = re.search(pattern, response.text, re.DOTALL)
            
            if match:
                yt_data = json.loads(match.group(1))
                
                # 保存原始JSON数据
                if self.save_raw:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_file = os.path.join(channel_output_dir, f"youtube_channel_data_{timestamp}.json")
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(yt_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
                    global_log.info(f"原始JSON数据已保存到: {json_file}")
                
                # 提取最新10条视频URL
                video_urls = self._extract_video_urls(yt_data)
                if not video_urls:
                    global_log.error("未找到视频URL")
                    return None
                
                # 获取每个视频的详细数据
                video_data_list = []
                for video_url in video_urls:
                    global_log.info(f"正在处理视频URL: {video_url}")
                    try:
                        video_data = self.base_spider.fetch_video(video_url)
                        if video_data:
                            video_data_list.append(video_data)
                    except Exception as e:
                        global_log.error(str(e))
                global_log.info("视频数据获取成功")
                if not video_data_list:
                    global_log.error("未获取到任何视频数据")
                    return None
                
                # 计算平均值
                averages = self._calculate_averages(video_data_list)
                global_log.info(f"平均值 {averages}" )
                # 提取频道基本信息
                microformat = yt_data.get('microformat', {}).get('microformatDataRenderer', {})
                user_name = microformat.get('title', '')
                
                # 获取粉丝数
                subscriber_text = None
                try:
                    # 主路径：从header中获取粉丝数
                    header_data = yt_data.get('header', {}).get('pageHeaderRenderer', {})
                    if header_data:
                        metadata_rows = header_data.get('content', {}).get('pageHeaderViewModel', {}).get('metadata', {}).get('contentMetadataViewModel', {}).get('metadataRows', [])
                        if len(metadata_rows) > 1:  # 确保有足够的行
                            subscriber_text = metadata_rows[1].get('metadataParts', [])[0].get('text', {}).get('content', '')
                    
                    # 备用路径：如果主路径失败，尝试其他路径
                    if not subscriber_text:
                        metadata_parts = yt_data.get('header', {}).get('c4TabbedHeaderRenderer', {}).get('subscriberCountText', {}).get('simpleText', '')
                        if metadata_parts:
                            subscriber_text = metadata_parts
                    
                    global_log.info(f"获取到的粉丝数文本: {subscriber_text}")
                except Exception as e:
                    global_log.error(f"获取粉丝数时出错: {e}")
                
                follower_count = self._convert_follower_count(subscriber_text) if subscriber_text else None
                
                # 获取头像URL并下载
                try:
                    # 从header中获取头像信息
                    header_data = yt_data.get('header', {}).get('pageHeaderRenderer', {})
                    if header_data:
                        avatar_sources = header_data.get('content', {}).get('pageHeaderViewModel', {}).get('image', {}).get('decoratedAvatarViewModel', {}).get('avatar', {}).get('avatarViewModel', {}).get('image', {}).get('sources', [])
                        
                        # 找到尺寸最大的图片
                        max_size = 0
                        avatar_url = None
                        for source in avatar_sources:
                            width = source.get('width', 0)
                            height = source.get('height', 0)
                            size = width * height
                            if size > max_size:
                                max_size = size
                                avatar_url = source.get('url')
                        
                        if avatar_url:
                            profile_picture_url = self._download_avatar(avatar_url, user_name)
                        else:
                            # 备用路径
                            backup_avatar_url = yt_data.get('header', {}).get('c4TabbedHeaderRenderer', {}).get('avatar', {}).get('thumbnails', [{}])[0].get('url', '')
                            if backup_avatar_url:
                                profile_picture_url = self._download_avatar(backup_avatar_url, user_name)
                            else:
                                profile_picture_url = None
                    else:
                        # 如果header_data不存在，使用备用路径
                        backup_avatar_url = yt_data.get('header', {}).get('c4TabbedHeaderRenderer', {}).get('avatar', {}).get('thumbnails', [{}])[0].get('url', '')
                        if backup_avatar_url:
                            profile_picture_url = self._download_avatar(backup_avatar_url, user_name)
                        else:
                            profile_picture_url = None
                except Exception as e:
                    global_log.error(f"获取头像URL时出错: {e}")
                    profile_picture_url = None
                
                # 构建符合CelebrityProfile格式的数据
                result = {
                    'platform': 'youtube',
                    'user_id': microformat.get('urlCanonical', '').split('/')[-1],
                    'user_name': user_name,
                    'full_name': user_name,
                    'index_url': url,
                    'profile_picture_url': profile_picture_url,
                    'follower_count': follower_count,
                    'average_likes': averages['average_likes'],
                    'average_comments': averages['average_comments'],
                    'average_views': averages['average_views'],
                    'average_engagement_rate': averages['average_engagement_rate'],
                    'country': microformat.get('country', ''),
                    'level': grade_criteria('youtube', int(averages['average_views'])),
                    'updated_at': date.today().isoformat(),
                    'isDelete' : 0
                }
                
                return result
            
            global_log.info("未找到ytInitialData数据")
            return None
            
        except requests.RequestException as e:
            global_log.error(f"请求出错: {e}")
            return None
        except json.JSONDecodeError as e:
            global_log.error(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            global_log.error(f"发生未知错误: {e}")
            return None

def run_youtube_spider(url:str):
    spider = YouTubeChannelSpider(proxy_port=7890, save_raw=True)
    result = spider.fetch_channel(url)

    inner_CelebrityProfile(result, isByIndexUrl=True)
    if result:
        global_log.info("频道数据获取成功!")
        global_log.info(json.dumps(result, indent=2, ensure_ascii=False, cls=DateTimeEncoder))


if __name__ == "__main__":
    # 使用示例
    run_youtube_spider("https://www.youtube.com/@SteamFlow")
