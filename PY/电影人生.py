# -*- coding: utf-8 -*-
# 电影人生 Python版 (by Grok, converted from JS)
import json
import re
import sys
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def init(self, extend=""):
        self.BASE_URL = 'https://www.dyrsvip.de'
        self.IMG_HOST = 'https://pic2.tupian.click'
        pass

    def getName(self):
        return "电影人生"

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def safe_text(self, text):
        if not text:
            return ''
        return re.sub(r'\s+', ' ', text.strip())

    def fix_img_url(self, img_url):
        if not img_url:
            return ''
        if img_url.startswith('http') and 'data:' not in img_url:
            return img_url
        if img_url.startswith('/'):
            return self.IMG_HOST + img_url
        return self.IMG_HOST + '/' + img_url

    def extract_list(self, html_text):
        """从HTML中提取影片列表（简化版，使用正则或后续用BeautifulSoup）"""
        # 由于base.spider中fetch返回的是文本，这里需要解析HTML
        # 推荐在实际环境中使用BeautifulSoup，但为了兼容，这里先用简单正则
        items = []
        # 匹配 .relative.group 块
        pattern = r'<div class="relative group[^"]*">.*?</div>'
        blocks = re.findall(pattern, html_text, re.DOTALL)
        for block in blocks:
            # 提取链接
            link_match = re.search(r'<a href="([^"]+)"[^>]*title="([^"]+)"', block)
            if not link_match:
                continue
            href = link_match.group(1)
            title = link_match.group(2)
            
            # 提取图片
            img_match = re.search(r'<img[^>]+src="([^"]+)"', block)
            img = img_match.group(1) if img_match else ''
            
            # 提取remark
            remark_match = re.search(r'<div class="absolute top-2 right-2[^"]*">([^<]+)', block)
            remark = remark_match.group(1).strip() if remark_match else ''
            
            items.append({
                'vod_id': href,
                'vod_name': title,
                'vod_pic': self.fix_img_url(img),
                'vod_remarks': remark
            })
        return items

    def homeContent(self, filter):
        common_filters = {
            'dianying': [
                {"key": "class", "name": "分类", "value": [
                    {"n": "全部", "v": ""}, {"n": "剧情", "v": "剧情"}, {"n": "喜剧", "v": "喜剧"},
                    {"n": "动作", "v": "动作"}, {"n": "爱情", "v": "爱情"}, {"n": "惊悚", "v": "惊悚"},
                    {"n": "犯罪", "v": "犯罪"}, {"n": "悬疑", "v": "悬疑"}, {"n": "冒险", "v": "冒险"},
                    {"n": "奇幻", "v": "奇幻"}, {"n": "战争", "v": "战争"}, {"n": "历史", "v": "历史"},
                    {"n": "传记", "v": "传记"}, {"n": "武侠", "v": "武侠"}, {"n": "动画", "v": "动画"},
                    {"n": "音乐", "v": "音乐"}
                ]},
                {"key": "area", "name": "地区", "value": [
                    {"n": "全部", "v": ""}, {"n": "美国", "v": "美国"}, {"n": "内地", "v": "内地"},
                    {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "日本", "v": "日本"},
                    {"n": "韩国", "v": "韩国"}, {"n": "英国", "v": "英国"}, {"n": "法国", "v": "法国"},
                    {"n": "德国", "v": "德国"}, {"n": "印度", "v": "印度"}, {"n": "意大利", "v": "意大利"},
                    {"n": "澳大利亚", "v": "澳大利亚"}, {"n": "泰国", "v": "泰国"}, {"n": "比利时", "v": "比利时"}
                ]},
                {"key": "year", "name": "年份", "value": [
                    {"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"},
                    {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"},
                    {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"},
                    {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"},
                    {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"},
                    {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"},
                    {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"},
                    {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"},
                    {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"},
                    {"n": "2000", "v": "2000"}
                ]},
                {"key": "sort_field", "name": "排序", "value": [
                    {"n": "默认", "v": ""}, {"n": "热度", "v": "play_hot"}, {"n": "年份", "v": "year"}
                ]}
            ]
        }

        return {
            'class': [
                {'type_id': 'dianying', 'type_name': '电影'},
                {'type_id': 'dianshiju', 'type_name': '电视剧'},
                {'type_id': 'zongyi', 'type_name': '综艺'},
                {'type_id': 'dongman', 'type_name': '动漫'},
                {'type_id': 'duanju', 'type_name': '短剧'}
            ],
            'filters': {
                'dianying': common_filters['dianying'],
                'dianshiju': common_filters['dianying'],
                'zongyi': common_filters['dianying'],
                'dongman': common_filters['dianying'],
                'duanju': common_filters['dianying']
            }
        }

    def homeVideoContent(self):
        res = self.fetch(self.BASE_URL + '/', returnType='text')
        if not res:
            return {'list': []}
        
        all_list = []
        containers = ['#dianying', '#dianshiju', '#zongyi', '#dongman', '#duanju']
        
        for container in containers:
            # 简单提取对应区块内容
            section_pattern = rf'{container}.*?id="{container[1:]}"[^>]*>(.*?)</section>'
            section_match = re.search(section_pattern, res, re.DOTALL)
            if section_match:
                section_html = section_match.group(1)
                part = self.extract_list(section_html)
                all_list.extend(part)
        
        return {'list': all_list}

    def categoryContent(self, tid, pg, filter, extend):
        p = int(pg) if pg else 1
        page = p - 1
        url = f"{self.BASE_URL}/{tid}.html?page={page}"
        
        if extend:
            if extend.get('class'):
                url += f"&class={extend['class']}"
            if extend.get('area'):
                url += f"&area={extend['area']}"
            if extend.get('year'):
                url += f"&year={extend['year']}"
            if extend.get('sort_field'):
                url += f"&sort_field={extend['sort_field']}"
        
        res = self.fetch(url, returnType='text')
        if not res:
            return {'list': []}
        
        list_data = self.extract_list(res)
        return {
            'page': p,
            'pagecount': 0,
            'list': list_data,
            'total': 0
        }

    def detailContent(self, ids):
        id = ids[0] if isinstance(ids, list) else ids
        url = self.BASE_URL + id
        res = self.fetch(url, returnType='text')
        if not res:
            return {'list': []}
        
        # 提取标题
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', res)
        title = self.safe_text(title_match.group(1)) if title_match else ''
        
        # 年份、地区
        year_match = re.search(r'class="text-gray-500[^"]*"[^>]*>.*?<span[^>]*>(.*?)</span>', res)
        year = self.safe_text(year_match.group(1)) if year_match else ''
        
        area_match = re.search(r'地区.*?>(.*?)</', res)
        area = self.safe_text(area_match.group(1)) if area_match else ''
        
        # 描述
        desc_match = re.search(r'class="text-sm text-justify[^"]*"[^>]*>(.*?)</', res, re.DOTALL)
        desc = self.safe_text(desc_match.group(1)) if desc_match else ''
        
        # 图片
        pic_match = re.search(r'poster[^>]*src="([^"]+)"', res) or re.search(r'img[^>]+src="([^"]+)"', res)
        pic = self.fix_img_url(pic_match.group(1)) if pic_match else ''
        
        # 播放源
        origins = ['jsm3u8']  # 默认
        
        # 剧集
        eps = []
        ep_matches = re.findall(r'<a href="[^"]*p=(\d+)"[^>]*>.*?<button[^>]*>(.*?)</button>', res)
        for p_val, name in ep_matches:
            eps.append({'name': name.strip() or f'第{len(eps)+1}集', 'p': p_val})
        
        play_from = []
        play_url = []
        for origin in origins:
            play_from.append(origin)
            ep_parts = []
            for ep in eps:
                link = f"{self.BASE_URL}{id}?origin={origin}&p={ep['p']}"
                ep_parts.append(f"{ep['name']}${link}")
            if not ep_parts:
                ep_parts.append(f"正片${self.BASE_URL}{id}?origin={origin}")
            play_url.append('#'.join(ep_parts))
        
        vod = {
            'vod_id': id,
            'vod_name': title,
            'vod_pic': pic,
            'vod_year': year,
            'vod_area': area,
            'vod_content': desc,
            'vod_play_from': '$$$'.join(play_from),
            'vod_play_url': '$$$'.join(play_url)
        }
        
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        p = int(pg) if pg else 1
        page = p - 1
        url = f"{self.BASE_URL}/s.html?name={key}&page={page}&sort_field=_id"
        res = self.fetch(url, returnType='text')
        if not res:
            return {'list': []}
        
        list_data = self.extract_list(res)
        return {'list': list_data, 'page': p}

    def playerContent(self, flag, id, vipFlags):
        return {
            'parse': 1,
            'url': id,
            'header': {'Referer': self.BASE_URL}
        }

    def localProxy(self, param):
        return None