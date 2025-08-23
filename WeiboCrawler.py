import requests
import re
from urllib.parse import quote
from bs4 import BeautifulSoup

# TODO：需要手动填写微博Cookie
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0',
    'Cookie': '',
    'X-Requested-With': 'XMLHttpRequest'
}

# 获取微博完整热搜榜
def get_weibo_hot_search_full():
    """
    获取完整的微博实时热搜榜
    """
    print("正在获取微博热搜榜...")
    url = "https://s.weibo.com/top/summary"
    try:
        response = requests.get(url, headers={'User-Agent': HEADERS['User-Agent'], 'Cookie': HEADERS['Cookie']})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        hot_list = []
        table = soup.find('table')
        if not table:
            print("错误：未能找到热搜表格。可能是Cookie已失效或微博页面结构已更新。")
            return []

        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                rank = cells[0].text.strip()
                title_element = cells[1].find('a')
                title = title_element.text.strip()
                hot_list.append({"rank": rank, "title": title})

        print(f"成功获取 {len(hot_list)} 条热搜。")
        return hot_list

    except requests.RequestException as e:
        print(f"请求热搜榜失败: {e}")
        return []

# TODO: 等待寻找最优解
def get_top_post_id(keyword):
    """
    根据关键词搜索，同时获取热搜的首个微博的 mid 和其作者的 uid。
    """
    search_url = f"https://s.weibo.com/weibo?q={quote(keyword)}&xsort=hot"
    search_headers = {
        'User-Agent': HEADERS['User-Agent'],
        'Cookie': HEADERS['Cookie'],
        'Referer': 'https://s.weibo.com/top/summary'
    }
    try:
        response = requests.get(search_url, headers=search_headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        all_posts = soup.find_all('div', {'class': 'card-wrap', 'action-type': 'feed_list_item'})

        for post in all_posts:
            if 'mid' in post.attrs:
                post_id = post['mid']

                author_link = post.find('a', class_='name')
                if author_link and 'href' in author_link.attrs:
                    href = author_link['href']
                    uid_match = re.search(r'/(u/)?(\d+)', href)
                    if uid_match:
                        author_uid = uid_match.group(2)
                        return post_id, author_uid

        return None, None
    except Exception:
        return None, None

# TODO: 获取热搜评论（按照时间排序获取最新50条）、分析评论情绪并获取平均情绪分存入数据库


# 程序入口
if __name__ == "__main__":
    hot_list = get_weibo_hot_search_full()