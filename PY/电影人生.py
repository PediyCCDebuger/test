# -*- coding: utf-8 -*-
import sys
import json
import urllib.parse
from base.spider import Spider
import requests
from lxml import etree

class Spider(Spider):
    """
    电影人生 TvBox 爬虫脚本
    配置示例：
    {
        "key": "dyrs",
        "name": "电影人生",
        "type": 3,
        "api": "此脚本路径",
        "searchable": 1,
        "quickSearch": 1,
        "filterable": 1,
        "changeable": 1,
        "ext": {
            "base_url": "https://www.dyrsvip.de",
            "img_host": "https://pic2.tupian.click"
        }
    }
    """
    def init(self, extend=""):
        """初始化配置"""
        self.base_url = "https://www.dyrsvip.de"
        self.img_host = "https://pic2.tupian.click"
        if extend:
            ext = json.loads(extend)
            self.base_url = ext.get("base_url", self.base_url)
            self.img_host = ext.get("img_host", self.img_host)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Mobile; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
            "Referer": self.base_url
        }

    def getName(self):
        return "电影人生"

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def safe_text(self, element):
        """安全提取文本，对应js的safeText函数"""
        if not element:
            return ""
        text = element.xpath("string(.)").strip()
        return " ".join(text.split())

    def fix_img_url(self, img_element):
        """修复图片链接，对应js的fixImgUrl函数"""
        if not img_element:
            return ""
        
        src = img_element.get("src", "")
        data_src = img_element.get("data-src", "")
        
        # 优先处理完整http链接
        if src and src.startswith("http") and not src.startswith("data:"):
            return src
        
        # 处理data-src
        if data_src and not data_src.startswith("data:"):
            if data_src.startswith("/"):
                return f"{self.img_host}{data_src}"
            return f"{self.img_host}/{data_src}"
        
        # 处理相对路径的src
        if src and not src.startswith("data:") and not src.startswith("http"):
            if src.startswith("/"):
                return f"{self.img_host}{src}"
            return f"{self.img_host}/{src}"
        
        return src

    def extract_list_from_container(self, html, container_selector):
        """从容器提取影片列表，对应js的extractListFromContainer函数"""
        tree = etree.HTML(html)
        container = tree.xpath(container_selector)
        if not container:
            return []
        
        items = container[0].xpath('.//div[contains(@class, "relative") and contains(@class, "group")]')
        list_data = []
        
        for item in items:
            link = item.xpath('.//a[@href]')[0] if item.xpath('.//a[@href]') else None
            img = item.xpath('.//img')[0] if item.xpath('.//img') else None
            remark_el = item.xpath('.//div[contains(@class, "absolute") and contains(@class, "top-2") and contains(@class, "right-2")]')
            
            vod_id = link.get("href", "") if link else ""
            vod_name = link.get("title", self.safe_text(item.xpath('.//h3')[0] if item.xpath('.//h3') else "")) if link else ""
            vod_pic = self.fix_img_url(img)
            vod_remarks = self.safe_text(remark_el[0]) if remark_el else ""
            
            list_data.append({
                "vod_id": vod_id,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_remarks": vod_remarks
            })
        return list_data

    def homeContent(self, filter_data):
        """获取首页分类和筛选器"""
        common_filters = {
            "class": {
                "key": "class",
                "name": "分类",
                "value": [
                    {"n": "全部", "v": ""}, {"n": "剧情", "v": "剧情"}, {"n": "喜剧", "v": "喜剧"},
                    {"n": "动作", "v": "动作"}, {"n": "爱情", "v": "爱情"}, {"n": "惊悚", "v": "惊悚"},
                    {"n": "犯罪", "v": "犯罪"}, {"n": "悬疑", "v": "悬疑"}, {"n": "冒险", "v": "冒险"},
                    {"n": "奇幻", "v": "奇幻"}, {"n": "战争", "v": "战争"}, {"n": "历史", "v": "历史"},
                    {"n": "传记", "v": "传记"}, {"n": "武侠", "v": "武侠"}, {"n": "动画", "v": "动画"},
                    {"n": "音乐", "v": "音乐"}
                ]
            },
            "area": {
                "key": "area",
                "name": "地区",
                "value": [
                    {"n": "全部", "v": ""}, {"n": "美国", "v": "美国"}, {"n": "内地", "v": "内地"},
                    {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "日本", "v": "日本"},
                    {"n": "韩国", "v": "韩国"}, {"n": "英国", "v": "英国"}, {"n": "法国", "v": "法国"},
                    {"n": "德国", "v": "德国"}, {"n": "印度", "v": "印度"}, {"n": "意大利", "v": "意大利"},
                    {"n": "澳大利亚", "v": "澳大利亚"}, {"n": "泰国", "v": "泰国"}, {"n": "比利时", "v": "比利时"}
                ]
            },
            "year": {
                "key": "year",
                "name": "年份",
                "value": [
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
                ]
            },
            "sort_field": {
                "key": "sort_field",
                "name": "排序",
                "value": [
                    {"n": "默认", "v": ""}, {"n": "热度", "v": "play_hot"}, {"n": "年份", "v": "year"}
                ]
            }
        }
        
        # 构造分类列表
        classes = [
            {"type_id": "dianying", "type_name": "电影"},
            {"type_id": "dianshiju", "type_name": "电视剧"},
            {"type_id": "zongyi", "type_name": "综艺"},
            {"type_id": "dongman", "type_name": "动漫"},
            {"type_id": "duanju", "type_name": "短剧"}
        ]
        
        # 构造筛选器（所有分类共用同一套筛选）
        filters = {}
        for cls in classes:
            filters[cls["type_id"]] = [
                common_filters["class"],
                common_filters["area"],
                common_filters["year"],
                common_filters["sort_field"]
            ]
        
        return {
            "class": classes,
            "filters": filters
        }

    def homeVideoContent(self):
        """获取首页视频内容"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            html = response.text
            
            # 提取各个分类容器的内容
            containers = ['//div[@id="dianying"]', '//div[@id="dianshiju"]', '//div[@id="zongyi"]', 
                          '//div[@id="dongman"]', '//div[@id="duanju"]']
            all_list = []
            
            for container in containers:
                part = self.extract_list_from_container(html, container)
                all_list.extend(part)
            
            return {"list": all_list}
        except Exception as e:
            return {"error": str(e), "list": []}

    def categoryContent(self, tid, pg, filter_data, extend):
        """获取分类内容"""
        try:
            p = int(pg) if pg else 1
            page = p - 1
            ext = extend or {}
            
            # 构造请求URL
            url = f"{self.base_url}/{tid}.html?page={page}"
            if ext.get("class"):
                url += f'&class={urllib.parse.quote(ext["class"])}'
            if ext.get("area"):
                url += f'&area={urllib.parse.quote(ext["area"])}'
            if ext.get("year"):
                url += f'&year={urllib.parse.quote(ext["year"])}'
            if ext.get("sort_field"):
                url += f'&sort_field={urllib.parse.quote(ext["sort_field"])}'
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            html = response.text
            
            # 从分类页的image-grid提取列表
            list_data = self.extract_list_from_container(html, '//div[@id="image-grid"]')
            
            return {
                "page": p,
                "pagecount": 0,
                "list": list_data,
                "total": 0
            }
        except Exception as e:
            return {"error": str(e), "list": []}

    def detailContent(self, ids):
        """获取详情页内容"""
        try:
            id = ids[0] if isinstance(ids, list) else ids
            url = f"{self.base_url}{id}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            html = response.text
            tree = etree.HTML(html)
            
            # 提取基础信息
            title = self.safe_text(tree.xpath('//h1')[0] if tree.xpath('//h1') else "")
            
            # 年份提取
            year_selector1 = '//div[contains(@class, "text-gray-500") and contains(@class, "mb-4")]/span[2]'
            year_selector2 = '//div[contains(@class, "text-sm") and contains(@class, "px-2") and contains(@class, "bg-gray-100")][2]'
            year = self.safe_text(tree.xpath(year_selector1)[0] if tree.xpath(year_selector1) else "")
            if not year:
                year = self.safe_text(tree.xpath(year_selector2)[0] if tree.xpath(year_selector2) else "")
            
            # 地区提取
            area_selector = '//div[contains(@class, "text-gray-500") and contains(@class, "mb-4")]/span[3]'
            area = self.safe_text(tree.xpath(area_selector)[0] if tree.xpath(area_selector) else "")
            
            # 简介提取
            desc_selector1 = '//div[contains(@class, "text-sm") and contains(@class, "text-justify")]'
            desc_selector2 = '//div[@style="word-break: break-all"]'
            desc = self.safe_text(tree.xpath(desc_selector1)[0] if tree.xpath(desc_selector1) else "")
            if not desc:
                desc = self.safe_text(tree.xpath(desc_selector2)[0] if tree.xpath(desc_selector2) else "")
            
            # 导演提取
            director_selector = '//a[contains(@href, "director")]/span'
            director = self.safe_text(tree.xpath(director_selector)[0] if tree.xpath(director_selector) else "")
            
            # 演员提取
            actor_selector = '//a[contains(@href, "actor")]/span'
            actors = [self.safe_text(actor) for actor in tree.xpath(actor_selector)]
            
            # 播放源提取
            origin_btns = tree.xpath('//div[@id="originTabs"]//button | //div[@id="originTabs"]//a//button')
            origins = []
            for btn in origin_btns:
                origin = btn.get("data-origin", btn.get("id", self.safe_text(btn)))
                if origin and origin not in origins:
                    origins.append(origin)
            if not origins:
                origins = ["jsm3u8"]
            
            # 剧集提取
            ep_links = tree.xpath('//div[@id="episodeContent"]//div[contains(@class, "seqlist")]//a')
            eps = []
            for idx, ep in enumerate(ep_links):
                ep_name = self.safe_text(ep.xpath('.//button')[0] if ep.xpath('.//button') else "")
                if not ep_name:
                    ep_name = f"第{idx+1}集"
                href = ep.get("href", "")
                p = ""
                if "p=" in href:
                    match = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("p")
                    if match:
                        p = match[0]
                eps.append({"name": ep_name, "p": p})
            
            # 构造播放源和播放链接
            play_from = []
            play_url = []
            for origin in origins:
                play_from.append(origin)
                ep_parts = []
                for ep in eps:
                    link = f"{self.base_url}{id}?origin={origin}&p={ep['p']}"
                    ep_parts.append(f"{ep['name']}${link}")
                if not ep_parts:
                    ep_parts.append(f"正片${self.base_url}{id}?origin={origin}")
                play_url.append("#".join(ep_parts))
            
            # 封面图提取
            pic_selector1 = '//div[contains(@class, "poster")]//img'
            pic_selector2 = '//div[contains(@class, "aspect-[2/3]")]//img'
            pic_el = tree.xpath(pic_selector1)[0] if tree.xpath(pic_selector1) else (tree.xpath(pic_selector2)[0] if tree.xpath(pic_selector2) else None)
            
            vod_data = {
                "vod_id": id,
                "vod_name": title,
                "vod_pic": self.fix_img_url(pic_el),
                "vod_year": year,
                "vod_area": area,
                "vod_content": desc,
                "vod_director": director,
                "vod_actor": ",".join(actors),
                "vod_play_from": "$$$".join(play_from),
                "vod_play_url": "$$$".join(play_url)
            }
            
            return {"list": [vod_data]}
        except Exception as e:
            return {"error": str(e), "list": []}

    def searchContent(self, key, quick, pg):
        """搜索内容"""
        try:
            p = int(pg) if pg else 1
            page = p - 1
            url = f"{self.base_url}/s.html?name={urllib.parse.quote(key)}&page={page}&sort_field=_id"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            html = response.text
            
            list_data = self.extract_list_from_container(html, '//div[@id="image-grid"]')
            
            return {
                "page": p,
                "pagecount": 0,
                "list": list_data,
                "total": 0
            }
        except Exception as e:
            return {"error": str(e), "list": []}

    def playerContent(self, flag, id, vipFlags):
        """播放器内容"""
        return {
            "parse": 1,
            "url": id,
            "header": {"Referer": self.base_url}
        }

    def localProxy(self, param):
        pass

if __name__ == "__main__":
    # 测试用例
    spider = Spider()
    spider.init()
    # 测试首页分类
    print(json.dumps(spider.homeContent({}), ensure_ascii=False, indent=2))
    # 测试首页视频
    # print(json.dumps(spider.homeVideoContent(), ensure_ascii=False, indent=2))
    # 测试分类内容
    # print(json.dumps(spider.categoryContent("dianying", 1, {}, {}), ensure_ascii=False, indent=2))
    # 测试搜索
    # print(json.dumps(spider.searchContent("测试", 0, 1), ensure_ascii=False, indent=2))
