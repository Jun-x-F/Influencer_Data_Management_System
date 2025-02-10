import json
import os
import random
import re
import string
from datetime import datetime, date
from json import JSONEncoder
from typing import Optional, Dict, Any

import requests

from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from tool.ua_pool import get_random_user_agent, parse_ua


class DateTimeEncoder(JSONEncoder):
    """自定义JSON编码器，处理datetime和date对象的序列化"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


class YouTubeSpider:
    """YouTube数据爬取类"""
    
    def __init__(self, proxy_port: int = 7890, save_raw: bool = True, calc_engagement: bool = True):
        """
        初始化YouTube爬虫
        
        Args:
            proxy_port: 本地代理端口号，默认7890
            save_raw: 是否保存原始数据，默认True
            calc_engagement: 是否计算参与率，默认True
        """
        self.proxy = {
            'http': f'http://127.0.0.1:{proxy_port}',
            'https': f'http://127.0.0.1:{proxy_port}'
        }
        self.save_raw = save_raw
        self.calc_engagement = calc_engagement
        
        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    @staticmethod
    def _generate_random_string(length: int) -> str:
        """生成指定长度的随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
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
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": user_agent
        }
    
    def _get_cookies(self) -> Dict[str, str]:
        """生成YouTube请求所需的cookies"""
        return {
            "GPS": "1",
            "YSC": self._generate_random_string(10),
            "VISITOR_INFO1_LIVE": self._generate_random_string(10),
            "VISITOR_PRIVACY_METADATA": "CgJTRxIEGgAgOg%3D%3D",
            "PREF": "tz=Asia.Shanghai&f6=40000000&f7=100"
        }
    
    @staticmethod
    def _convert_date(date_text: str) -> Optional[str]:
        """将YouTube日期文本转换为标准格式"""
        try:
            date_text = date_text.strip()
            
            # 处理带有前缀的日期
            prefixes = [
                "首播开始于", "直播开始于", "预定开始于",
                "直播开始期：", "开始时间：", "发布时间：",
                "首播时间：", "上传时间："
            ]
            for prefix in prefixes:
                if prefix in date_text:
                    date_text = date_text.replace(prefix, "").strip()
                    break
            
            # 处理日期格式
            date_text = date_text.replace('年', '-').replace('月', '-').replace('日', '')
            
            # 尝试不同的日期格式
            date_formats = [
                '%Y-%m-%d',  # 2025-1-7
                '%Y-%m-%d %H:%M',  # 2025-1-7 14:30
                '%Y-%m-%d %H:%M:%S',  # 2025-1-7 14:30:00
                '%Y.%m.%d',  # 2025.1.7
                '%Y.%m.%d %H:%M',  # 2025.1.7 14:30
                '%Y.%m.%d %H:%M:%S'  # 2025.1.7 14:30:00
            ]
            
            # 预处理日期文本，统一格式
            date_text = date_text.replace('.', '-')
            
            for date_format in date_formats:
                try:
                    dt = datetime.strptime(date_text, date_format)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            raise ValueError(f"无法解析日期格式: {date_text}")
            
        except Exception as e:
            print(f"日期转换错误: {str(e)}")
            return None
    
    @staticmethod
    def _calculate_engagement_rate(views: int, likes: int, comments: int, collections: int = 0) -> float:
        """
        计算参与率 = (点赞数 + 评论数) / 播放量
        参考youtube_video_spider.py的计算方式
        """
        try:
            if not views:
                return 0.0
            engagement = (likes or 0) + (comments or 0)  # 不再使用collections
            return round(engagement / views, 4)  # 保留4位小数
        except Exception:
            return 0.0
    
    @staticmethod
    def _safe_extract_number(text: str) -> Optional[int]:
        """安全提取数字"""
        try:
            if isinstance(text, (int, float)):
                return int(text)
            return int(''.join(filter(str.isdigit, str(text))))
        except (ValueError, TypeError, AttributeError):
            return None
    
    def _parse_data(self, data: Dict[str, Any], video_id: str, original_url: str) -> Optional[Dict[str, Any]]:
        """解析YouTube数据"""
        try:
            # 判断是否为短视频
            is_shorts = "shorts" in original_url
            # input(f"{is_shorts} {original_url}")
            result = {
                'platform': 'youtube',
                'type': "短视频" if is_shorts else "视频",
                'user_name': None,
                'full_name': None,
                'video_url': original_url,
                'updated_at': date.today().isoformat(),
            }
            
            if is_shorts:
                # 解析短视频数据
                # 优先从engagementPanels获取用户名
                engagement_panels = data.get('engagementPanels', [])
                user_name_found = False
                
                # 遍历engagement_panels查找用户名
                for panel in engagement_panels:
                    if not user_name_found:
                        panel_content = panel.get('engagementPanelSectionListRenderer', {}).get('content', {})
                        if panel_content and 'structuredDescriptionContentRenderer' in panel_content:
                            items = panel_content.get('structuredDescriptionContentRenderer', {}).get('items', [])
                            for item in items:
                                if 'videoDescriptionHeaderRenderer' in item:
                                    channel_info = item.get('videoDescriptionHeaderRenderer', {}).get('channel', {})
                                    if channel_info and 'simpleText' in channel_info:
                                        result['user_name'] = channel_info['simpleText']
                                        result['full_name'] = channel_info['simpleText']
                                        user_name_found = True
                                        break

                # 如果从engagementPanels获取失败，则使用备选方法
                if not user_name_found:
                    channel_path = data.get('overlay', {}).get('reelPlayerOverlayRenderer', {}).get('metapanel', {}).get('reelMetapanelViewModel', {}).get('metadataItems', [])
                    if channel_path and len(channel_path) > 0:
                        channel_url = channel_path[0].get('reelChannelBarViewModel', {}).get('channelName', {}).get('commandRuns', [])[0].get('onTap', {}).get('innertubeCommand', {}).get('commandMetadata', {}).get('webCommandMetadata', {}).get('url', '')
                        if channel_url:
                            # 从/@username/shorts中提取username
                            channel_name = channel_url.split('/')[1]  # 获取@username部分
                            if channel_name.startswith('@'):
                                result['user_name'] = channel_name
                                result['full_name'] = channel_name
                # input(result['user_name'])
                likes_found = False
                comments_found = False

                # 获取点赞数 - 第一种路径
                overlay_data = data.get('overlay', {})
                if overlay_data and not likes_found:
                    reel_player = overlay_data.get('reelPlayerOverlayRenderer', {})
                    if reel_player:
                        like_button = reel_player.get('likeButton', {})
                        if like_button:
                            like_renderer = like_button.get('likeButtonRenderer', {})
                            if like_renderer and 'likeCount' in like_renderer:
                                result['likes'] = self._safe_extract_number(like_renderer['likeCount'])
                                likes_found = True

                # 获取点赞数 - 第二种路径
                if not likes_found:
                    engagement_panels = data.get('engagementPanels', [])
                    for panel in engagement_panels:
                        if not likes_found and 'engagementPanelSectionListRenderer' in panel:
                            panel_content = panel.get('engagementPanelSectionListRenderer', {}).get('content', {})
                            if panel_content and 'structuredDescriptionContentRenderer' in panel_content:
                                items = panel_content.get('structuredDescriptionContentRenderer', {}).get('items', [])
                                for item in items:
                                    if 'videoDescriptionHeaderRenderer' in item:
                                        header = item.get('videoDescriptionHeaderRenderer', {})
                                        factoids = header.get('factoid', [])
                                        for factoid in factoids:
                                            if 'factoidRenderer' in factoid:
                                                value = factoid.get('factoidRenderer', {}).get('value', {})
                                                if value and 'simpleText' in value:
                                                    result['likes'] = self._safe_extract_number(value['simpleText'])
                                                    likes_found = True
                                                    break
                                    if likes_found:
                                        break
                
                # 获取评论数 - 第一种路径
                if overlay_data and reel_player and not comments_found:
                    view_comments = reel_player.get('viewCommentsButton', {})
                    if view_comments:
                        button_renderer = view_comments.get('buttonRenderer', {})
                        if button_renderer:
                            text_data = button_renderer.get('text', {})
                            if text_data and 'simpleText' in text_data:
                                result['comments'] = self._safe_extract_number(text_data['simpleText'])
                                comments_found = True

                # 获取评论数 - 第二种路径
                if not comments_found:
                    engagement_panels = data.get('engagementPanels', [])
                    for panel in engagement_panels:
                        if not comments_found and 'engagementPanelSectionListRenderer' in panel:
                            header = panel.get('engagementPanelSectionListRenderer', {}).get('header', {})
                            if header:
                                title_header = header.get('engagementPanelTitleHeaderRenderer', {})
                                if title_header:
                                    contextual_info = title_header.get('contextualInfo', {})
                                    if contextual_info:
                                        runs = contextual_info.get('runs', [])
                                        for run in runs:
                                            if 'text' in run:
                                                result['comments'] = self._safe_extract_number(run['text'])
                                                comments_found = True
                                                break
                
                # 获取观看次数和发布时间
                engagement_panels = data.get('engagementPanels', [])
                for panel in engagement_panels:
                    if 'engagementPanelSectionListRenderer' in panel:
                        content = panel.get('engagementPanelSectionListRenderer', {}).get('content', {}).get('structuredDescriptionContentRenderer', {}).get('items', [])
                        for item in content:
                            if 'videoDescriptionHeaderRenderer' in item:
                                header = item['videoDescriptionHeaderRenderer']
                                # 获取观看次数
                                factoids = header.get('factoid', [])
                                for factoid in factoids:
                                    if 'viewCountFactoidRenderer' in factoid:
                                        view_text = factoid.get('viewCountFactoidRenderer', {}).get('factoid', {}).get('factoidRenderer', {}).get('value', {}).get('simpleText', '0')
                                        result['views'] = self._safe_extract_number(view_text)
                                        break
                                
                                # 获取发布时间
                                date_text = header.get('publishDate', {}).get('simpleText', '')
                                if date_text:
                                    result['releasedTime'] = self._convert_date(date_text)
            else:
                # 原有的视频数据解析逻辑
                video_data = data.get('contents', {}).get('twoColumnWatchNextResults', {}).get('results', {}).get('results', {}).get('contents', [])
                
                # 遍历视频数据提取信息
                for content in video_data:
                    if 'videoPrimaryInfoRenderer' in content:
                        primary_info = content['videoPrimaryInfoRenderer']
                        
                        # 获取观看次数
                        if 'viewCount' in primary_info:
                            view_text = primary_info.get('viewCount', {}).get('videoViewCountRenderer', {}).get('viewCount', {}).get('simpleText', '0')
                            result['views'] = self._safe_extract_number(view_text)
                        
                        # 获取点赞数
                        if 'videoActions' in primary_info:
                            top_level_buttons = primary_info.get('videoActions', {}).get('menuRenderer', {}).get('topLevelButtons', [])
                            for button in top_level_buttons:
                                # 处理新版UI结构 - segmentedLikeDislikeButtonViewModel
                                if 'segmentedLikeDislikeButtonViewModel' in button:
                                    like_button = button.get('segmentedLikeDislikeButtonViewModel', {}).get('likeButtonViewModel', {})
                                    button_view_model = like_button.get('likeButtonViewModel', {}).get('toggleButtonViewModel', {}).get('toggleButtonViewModel', {})
                                    default_button = button_view_model.get('defaultButtonViewModel', {}).get('buttonViewModel', {})
                                    if 'title' in default_button:
                                        result['likes'] = self._safe_extract_number(default_button['title'])
                                        break
                                # 处理新版UI结构 - segmentedLikeDislikeButtonRenderer
                                elif 'segmentedLikeDislikeButtonRenderer' in button:
                                    like_button = button['segmentedLikeDislikeButtonRenderer'].get('likeButton', {}).get('toggleButtonRenderer', {})
                                    if 'toggledText' in like_button:
                                        like_text = like_button['toggledText']['accessibility']['accessibilityData']['label']
                                        result['likes'] = self._safe_extract_number(like_text)
                                        break
                                # 处理旧版UI结构
                                elif 'buttonRenderer' in button:
                                    button_data = button['buttonRenderer']
                                    if 'like' in str(button_data.get('accessibility', {}).get('label', '')).lower():
                                        like_text = button_data.get('accessibility', {}).get('label', '0')
                                        result['likes'] = self._safe_extract_number(like_text)
                                        break
                        
                        # 获取发布时间
                        if 'dateText' in primary_info:
                            date_text = primary_info['dateText'].get('simpleText', '')
                            result['releasedTime'] = self._convert_date(date_text)
                    
                    # 获取频道信息
                    elif 'videoSecondaryInfoRenderer' in content:
                        secondary_info = content['videoSecondaryInfoRenderer']
                        if 'owner' in secondary_info:
                            owner_info = secondary_info['owner'].get('videoOwnerRenderer', {})
                            # 获取频道名称
                            if 'title' in owner_info:
                                title_runs = owner_info['title'].get('runs', [])
                                for run in title_runs:
                                    if 'text' in run:
                                        result['user_name'] = run['text']
                                        result['full_name'] = result['user_name']  # 可以根据需要设置不同的值
                                        break
                
                # 获取评论数
                engagement_panels = data.get('engagementPanels', [])
                for panel in engagement_panels:
                    if 'engagementPanelSectionListRenderer' in panel:
                        panel_data = panel['engagementPanelSectionListRenderer']
                        if panel_data.get('panelIdentifier') == 'engagement-panel-comments-section':
                            if 'header' in panel_data:
                                header_runs = panel_data['header'].get('engagementPanelTitleHeaderRenderer', {}).get('contextualInfo', {}).get('runs', [])
                                for run in header_runs:
                                    if 'text' in run:
                                        result['comments'] = self._safe_extract_number(run['text'])
                                        break
            
            # 计算参与率（如果启用）
            if self.calc_engagement and result.get('views'):
                try:
                    result['engagement_rate'] = self._calculate_engagement_rate(
                        result.get('views', 0),
                        result.get('likes', 0),
                        result.get('comments', 0)
                    )
                except Exception as e:
                    print(f"计算参与率出错: {e}")
                    result['engagement_rate'] = 0.0
            
            return result
        except Exception as e:
            print(f"解析数据时出错: {e}")
            return None
    
    def _fetch_channel_data(self, url: str) -> Optional[Dict[str, Any]]:
        """获取频道数据"""
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                cookies=self._get_cookies(),
                proxies=self.proxy,
                timeout=30,
                verify=False
            )
            response.raise_for_status()
            
            pattern = r'<script nonce="[^"]*">var ytInitialData = ({.*?});</script>'
            match = re.search(pattern, response.text, re.DOTALL)
            
            if match:
                return json.loads(match.group(1))
            return None
        except Exception as e:
            print(f"获取频道数据时出错: {e}")
            return None
    
    @staticmethod
    def _extract_video_id(url: str) -> Optional[str]:
        """
        从YouTube URL中提取视频ID
        
        Args:
            url: YouTube视频URL或视频ID
            
        Returns:
            str: 视频ID，如果无法提取则返回None
        """
        try:
            # 如果输入的是完整URL
            if 'youtube.com' in url or 'youtu.be' in url:
                # 处理短视频URL
                if '/shorts/' in url:
                    return url.split('/shorts/')[1].split('?')[0]
                # 处理标准YouTube URL
                elif 'v=' in url:
                    return url.split('v=')[1].split('&')[0]
                # 处理短链接
                elif 'youtu.be/' in url:
                    return url.split('youtu.be/')[1].split('?')[0]
            # 如果输入的直接是视频ID
            elif len(url.strip()) > 8:  # YouTube视频ID通常为11位
                return url.strip()
            return None
        except Exception as e:
            print(f"提取视频ID出错: {e}")
            return None
    
    def fetch_video(self, url: str, output_dir: str = "output") -> Optional[Dict[str, Any]]:
        """
        获取YouTube视频数据
        
        Args:
            url: YouTube视频URL或视频ID
            output_dir: 输出目录，默认为output
            
        Returns:
            Dict[str, Any]: 解析后的视频数据，如果失败则返回None
        """
        # 提取视频ID
        video_id = self._extract_video_id(url)
        if not video_id:
            print("无效的YouTube URL或视频ID")
            return None
            
        # 创建视频专属的输出目录
        video_output_dir = os.path.join(output_dir, video_id)
        if not os.path.exists(video_output_dir):
            os.makedirs(video_output_dir)
            
        api_url = "https://www.youtube.com/watch"
        params = {"v": video_id}
        
        try:
            response = requests.get(
                api_url,
                headers=self._get_headers(),
                cookies=self._get_cookies(),
                params=params,
                proxies=self.proxy,
                timeout=30,
                verify=False
            )
            response.raise_for_status()
            print(f"请求状态码: {response.status_code}")
            
            # 保存原始HTML
            if self.save_raw:
                html_file = os.path.join(video_output_dir, "raw.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"原始HTML已保存到: {html_file}")
            
            pattern = r'<script nonce="[^"]*">var ytInitialData = ({.*?});</script>'
            match = re.search(pattern, response.text, re.DOTALL)
            
            if match:
                yt_data = json.loads(match.group(1))
                
                if self.save_raw:
                    # 保存原始JSON数据
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_file = os.path.join(video_output_dir, f"youtube_data_{timestamp}.json")
                    
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(yt_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
                    print(f"原始JSON数据已保存到: {json_file}")
                
                # 解析数据
                parsed_data = self._parse_data(yt_data, video_id, url)
                if parsed_data:
                    if self.save_raw:
                        # 保存解析后的数据
                        parsed_file = os.path.join(video_output_dir, f"youtube_parsed_data_{timestamp}.json")
                        with open(parsed_file, 'w', encoding='utf-8') as f:
                            json.dump(parsed_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
                        print(f"解析后的数据已保存到: {parsed_file}")
                    return parsed_data
            
            print("未找到ytInitialData数据")
            return None
            
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"发生未知错误: {e}")
            return None


if __name__ == "__main__":
    # 使用示例
    spider = YouTubeSpider(
        proxy_port=7890,
        save_raw=False,
        calc_engagement=True  # 启用参与率计算
    )
    # 使用完整URL
    result = spider.fetch_video("https://www.youtube.com/watch?v=-7Lyc-DGUA8")
    inner_InfluencersVideoProjectData(result)
    inner_InfluencersVideoProjectDataByDate(result)
    if result:
        print("数据获取成功!")
        print(json.dumps(result, indent=2, ensure_ascii=False, cls=DateTimeEncoder))

