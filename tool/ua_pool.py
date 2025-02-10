"""
@ProjectName: DataAnalysis
@FileName：ua_pool.py
@IDE：PyCharm
@Author：Libre
@Time：2024/10/17 下午2:24
"""

import random
import re

# 100个常见的User-Agent字符串
USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/85.0.4183.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 Firefox/79.0",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:72.0) Gecko/20100101 Firefox/72.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
    # Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/12.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/13.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/13.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko)"
    " Version/9.1.2 Safari/601.7.7",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko)"
    " Version/8.0.8 Safari/600.8.9",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/90.0.818.66 Safari/537.36 Edg/90.0.818.66",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/89.0.4389.82 Safari/537.36 Edg/89.0.774.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.81",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.63",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.63",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.58",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/82.0.4060.66 Safari/537.36 Edg/82.0.425.63",
    # Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.154",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/89.0.4389.128 Safari/537.36 OPR/75.0.3969.93",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/88.0.4324.190 Safari/537.36 OPR/74.0.3911.160",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.344",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.400",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.228",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/84.0.4147.89 Safari/537.36 OPR/70.0.3728.189",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.86",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/82.0.4060.66 Safari/537.36 OPR/68.0.3618.125",
    # Mobile Browsers
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/89.0.4389.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/13.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930V) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/87.0.4280.101 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/12.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 7.0; Nexus 5X Build/NBD90W) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/86.0.4240.110 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko)"
    " Version/11.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/85.0.4183.127 Mobile Safari/537.36",
    # Others
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "Mozilla/5.0 (compatible; DuckDuckBot/1.0; +http://duckduckgo.com/duckduckbot.html)",
    "Mozilla/5.0 (compatible; Sogou web spider/4.0; +http://www.sogou.com/docs/help/webmasters.htm#07)",
    "Mozilla/5.0 (compatible; Exabot/3.0; +http://www.exabot.com/go/robot)",
    "Mozilla/5.0 (compatible; facebot/1.0; +http://www.facebook.com/externalhit_uatext.php)",
    "Mozilla/5.0 (compatible; Twitterbot/1.0; +http://twitter.com)",
    "Mozilla/5.0 (compatible; Slackbot-LinkExpanding 1.0; +https://api.slack.com/robots)",
    # Additional UAs to make up 100
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/80.0.3987.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/82.0.4069.112 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/13.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/95.0.4638.54 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.1 Safari/605.1.15",
    # Additional UAs to reach 100
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/99.0.4844.51 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.2 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/100.0.4896.60 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/101.0.4951.54 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/103.0.5060.66 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_1) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/105.0.5195.54 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_2) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/106.0.5249.91 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_3) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/107.0.5304.87 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_4) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/108.0.5359.125 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_5) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.7 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/109.0.5414.87 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/110.0.5481.77 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.8 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/111.0.5563.111 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_8) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.8 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/112.0.5615.49 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_9) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.8 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/113.0.5672.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_10) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.8 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.5735.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_11) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.9 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:113.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/115.0.5770.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_12) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/116.0.5845.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_13) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/117.0.5938.62 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_14) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.8 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/118.0.5993.89 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_15) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 16_9 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.9 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/119.0.6103.75 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_16) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/120.0.6205.81 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_17) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/121.0.6324.103 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_18) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/122.0.6340.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_19) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/123.0.6359.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_20) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/124.0.6471.89 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_21) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/125.0.6591.89 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_22) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/126.0.6700.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_23) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/127.0.6749.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_24) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.8 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/128.0.6823.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_25) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.8 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 17_9 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/17.9 Mobile/15E148 Safari/604.1",
]


def get_random_user_agent(_filter: str = None):
    """
    从USER_AGENTS列表中随机选择一个User-Agent字符串。

    Returns:
        str: 随机选取的User-Agent字符串。
    """
    if _filter is None:
        return random.choice(USER_AGENTS)
    xx = []
    for ua in USER_AGENTS:
        if _filter.title() in ua:
            xx.append(ua)
    return random.choice(xx)


async def get_random_user_agent_async(_filter: str = None):
    """
    从USER_AGENTS列表中随机选择一个User-Agent字符串。

    Returns:
        str: 随机选取的User-Agent字符串。
    """
    if _filter is None:
        return random.choice(USER_AGENTS)
    xx = []
    for ua in USER_AGENTS:
        if _filter.title() in ua:
            xx.append(ua)
    return random.choice(xx)


def parse_ua(ua):
    # 解析 sec-ch-ua-mobile
    if "Windows NT" in ua or "Macintosh" in ua or "Linux" in ua:
        sec_ch_ua_mobile = "?0"  # 非移动设备
    else:
        sec_ch_ua_mobile = "?1"  # 移动设备

    # 解析 sec-ch-ua-platform
    if "Windows NT" in ua:
        sec_ch_ua_platform = "\"Windows\""
    elif "Macintosh" in ua:
        sec_ch_ua_platform = "\"Macintosh\""
    elif "Linux" in ua:
        sec_ch_ua_platform = "\"Linux\""
    elif "Android" in ua:
        sec_ch_ua_platform = "\"Android\""
    elif "iPhone" in ua:
        sec_ch_ua_platform = "\"iPhone\""
    else:
        sec_ch_ua_platform = "\"Unknown\""

    # 提取浏览器版本（Chrome/91.0.4472.124）
    chrome_match = re.search(r'Chrome/(\d+)', ua)
    if chrome_match:
        chrome_version = chrome_match.group(1)

    # 构建最终的解析结果
    parsed_ua = {
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "sec-ch-ua": f"\"Google Chrome\";v=\"{chrome_version}\", \"Chromium\";v=\"{chrome_version}\", \"Not_A Brand\";v=\"24\""
    }

    return parsed_ua


async def parse_ua_async(ua):
    # 解析 sec-ch-ua-mobile
    if "Windows NT" in ua or "Macintosh" in ua or "Linux" in ua:
        sec_ch_ua_mobile = "?0"  # 非移动设备
    else:
        sec_ch_ua_mobile = "?1"  # 移动设备

    # 解析 sec-ch-ua-platform
    if "Windows NT" in ua:
        sec_ch_ua_platform = "\"Windows\""
    elif "Macintosh" in ua:
        sec_ch_ua_platform = "\"Macintosh\""
    elif "Linux" in ua:
        sec_ch_ua_platform = "\"Linux\""
    elif "Android" in ua:
        sec_ch_ua_platform = "\"Android\""
    elif "iPhone" in ua:
        sec_ch_ua_platform = "\"iPhone\""
    else:
        sec_ch_ua_platform = "\"Unknown\""

    # 提取浏览器版本（Chrome/91.0.4472.124）
    chrome_match = re.search(r'Chrome/(\d+)', ua)
    if chrome_match:
        chrome_version = chrome_match.group(1)

    # 构建最终的解析结果
    parsed_ua = {
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "sec-ch-ua": f"\"Google Chrome\";v=\"{chrome_version}\", \"Chromium\";v=\"{chrome_version}\", \"Not_A Brand\";v=\"24\""
    }

    return parsed_ua


def generate_user_agents():
    """
    如果需要动态生成或扩展User-Agent池，可以在这里添加生成逻辑。
    目前，此函数仅作为占位符。
    """
    # 示例：添加更多User-Agent到池中
    additional_uas = [
        # 可以在此添加更多的User-Agent字符串
    ]
    USER_AGENTS.extend(additional_uas)


if __name__ == "__main__":
    # 示例：打印一个随机的User-Agent
    print(parse_ua(get_random_user_agent("Chrome")))
