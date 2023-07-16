import requests
import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
from tqdm import tqdm


caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"
option = Options()
driver = webdriver.Chrome(options=option)
driver.get('https://auth.danawa.com/login?url=https%3A%2F%2Fdpg.danawa.com%2Fnews%2Flist%3FboardSeq%3D60%26page%3D2')

NEWS_NAV_URL = 'https://dpg.danawa.com/news/list?boardSeq=60,61,62,63,64,65,66,67,68,130&page=%d'
BBS_NAV_URL = 'https://dpg.danawa.com/bbs/list?boardSeq=%d&page=%d&past=Y'
BBS_20 = [11, 129, 175, 264]
BBS_5 = [31, 32, 190, 230, 231, 233, 235, 236, 238, 244, 270, 275, 280, 281, 282]
GALLERY_20 = 28
GALLERY_5 = [219, 220]

#BBS_20 : 자유게시판 = 11, 입소문 = 129, 유머 = 175, 체험단 264
#BBS_5 : 쇼핑몰후기 31 bbs_table, AS 후기 32, 게임 190, 키덜트 202, CPU/ram 229, VGA 230, SSD/HDD 231, 모니터 233, 조립피시 235, 노트북 236, 케이스/파워 238, 키보드/마우스 244, 당첨후기 270, 엄근진 275, 스마트IT 280, 여행 281, 바퀴 282
#갤러리20 -> 소비자이용기 28
#갤러리5 -> 반려동물 219 먹거리 220

USER_AGENT = {'User-Agent' : driver.execute_script("return navigator.userAgent")}

for _ in tqdm(range(10), desc='로그인 대기'): sleep(1)

s = requests.Session()
s.headers.update(USER_AGENT)
for cookie in driver.get_cookies():
    c = {cookie['name'] : cookie['value']}
    s.cookies.update(c)

data_dicts = []

def make_dict(link:str):
    boardSeq = re.search(r'boardSeq=(\d+)', link).group(1)
    listSeq = re.search(r'listSeq=(\d+)', link).group(1)
    data = {
    'boardSeq': boardSeq,
    'listSeq': listSeq,
    'depth': 1,
    'content': '%EC%9E%98%20%EB%B4%A4%EC%8A%B5%EB%8B%88%EB%8B%A4.',
    'file': None,
    }
    return data

#뉴스
for i in range(100,104):
    document = s.get(NEWS_NAV_URL %i, params={'user-agent': USER_AGENT}).text
    content = BeautifulSoup(document, "html.parser")
    links = content.find_all('a', attrs={'class':'thumb_link'})[3:]
    data_dicts += [make_dict(link.get('href')) for link in links]

for data_dict in tqdm(data_dicts, desc='뉴스 댓글 달기'):
    s.post('https://dpg.danawa.com/news/rest/news/setComment', data=data_dict)
    sleep(3)

data_dicts = []

    
#이미지
document = s.get(BBS_NAV_URL %(GALLERY_20, 30), params={'user-agent': USER_AGENT}).text
content = BeautifulSoup(document, "html.parser")
links = content.find_all('a', attrs={'class':'gall_thumb_link thumb_area'})
data_dicts += [make_dict(link.get('href')) for link in links]

for i in GALLERY_5:
    document = s.get(BBS_NAV_URL %(i, 30), params={'user-agent': USER_AGENT}).text
    content = BeautifulSoup(document, "html.parser")
    links = content.find_all('a', attrs={'class':'gall_thumb_link thumb_area'})[3:8]
    data_dicts += [make_dict(link.get('href')) for link in links]

#BBS
for i in BBS_20:
    document = s.get(BBS_NAV_URL %(i, 30), params={'user-agent': USER_AGENT}).text
    content = BeautifulSoup(document, "html.parser")
    links = content.find_all('a', attrs={'class':'title_link'})[3:23]
    if i == 264:
        links = content.find_all('a', attrs={'class':'thumb_link'})[3:23]
    data_dicts += [make_dict(link.get('href')) for link in links]
for i in BBS_5:
    document = s.get(BBS_NAV_URL %(i, 10), params={'user-agent': USER_AGENT}).text
    content = BeautifulSoup(document, "html.parser")
    links = content.find_all('a', attrs={'class':'title_link'})[3:8]
    data_dicts += [make_dict(link.get('href')) for link in links]

for data_dict in tqdm(data_dicts, desc='게시글 댓글 달기'):
    s.post('https://dpg.danawa.com/news/rest/news/setComment', data=data_dict)
    sleep(3)