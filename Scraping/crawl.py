from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import re
import pandas as pd
from bs4 import BeautifulSoup

browser = webdriver.Chrome()
browser.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
elements = browser.find_elements(By.XPATH, '//li//a[@class="ipc-title-link-wrapper"]')
links = [link.get_attribute('href') for link in elements]
browser.quit()

movies_data =[]

browser = webdriver.Chrome()
for link in links:
    browser.get(link)
    wait = WebDriverWait(browser, 40)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
#movie_id
    movie_id = re.search(r"tt(\d+)", link).group(1)

#title
    title = browser.find_element(By.XPATH, '//h1').text

#year    
    try:
        year = browser.find_element(By.XPATH, '//div[contains(@class, "iOkLEK")]//li[text()[contains(.,"h")]]').text
    except:
        year = None
#parental guid    
    try:
        parental_guid = browser.find_element(By.CSS_SELECTOR, '.aFhKV .ipc-inline-list__item+ .ipc-inline-list__item .ipc-link--inherit-color').text
    except:
        parental_guid = None
#runtime    
    try:
        runtime = browser.find_element(By.XPATH,'//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[3]').text
    except:
        runtime = None
#genre    
    try:
        genre_list = browser.find_elements(By.XPATH, '//section//a//span[@class="ipc-chip__text"]')
        genre = [genre.text for genre in genre_list]
    except:
        genre = None
#director
    ul = soup.select("div.knNUTS > ul")[0]
    li_tags = ul.find_all("li", recursive=False)
    directors = [item.get_text(strip=True) for item in li_tags[0].find_all('li')]
    directors_id = []
    directors_links = li_tags[0].find_all('a')
    for i in directors_links:
        match = re.search(r"nm(\d{7,})", i.get('href'))
        if match:
            directors_id.append(match.group(1))

#writers    
    writers = [item.get_text(strip=True) for item in li_tags[1].find_all('li')]
    writers_id = []
    writers_links = li_tags[1].find_all('a')
    for i in writers_links:
        match = re.search(r"nm(\d{7,})", i.get('href'))
        if match:
            writers_id.append(match.group(1))

#stars
    stars = [item.get_text(strip=True) for item in li_tags[2].find_all('li')]
    stars_id = []
    stars_link = li_tags[2].find_all('a')
    for i in stars_link:
        match = re.search(r"nm(\d{7,})", i.get('href'))
        if match:
            stars_id.append(match.group(1))     

#sell in us & canada
    try:
        gross_us_canada = browser.find_element(By.XPATH,'//li[span[text()="Gross US & Canada"]]/div').text
    except:
        gross_us_canada = None

    data = {
        'Movie ID' : movie_id,
        'Title': title,
        'Year' : year,
        'Parental Guid' : parental_guid,
        'Runtime' : runtime,
        'Genre' : genre,
        'Directors ID': directors_id,
        'Directors' : directors,
        'Writers ID': writers_id,
        'Writers' : writers,
        'Stars ID' : stars_id,
        'Stars': stars,
        'Gross US Canada' : gross_us_canada
    }

    movies_data.append(data)

browser.quit()

data = pd.DataFrame(movies_data)
data.to_csv('Top 250 IMDB.csv', index=False)