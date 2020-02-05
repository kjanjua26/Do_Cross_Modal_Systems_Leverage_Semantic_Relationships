from bs4 import BeautifulSoup
import requests, re, time
from urllib.request import Request, urlopen
import os
from selenium import webdriver

driver = webdriver.Chrome()

def page(url, header):
    req = Request(url, headers=header)
    webpage = urlopen(req).read()
    driver.get(url)
    for i in range(1, 3):  # scrolling for n times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # infinite scrolling issue.
        time.sleep(4)
    page = driver.page_source
    driver.quit()
    print("Done scrolling!")
    return BeautifulSoup(page, 'html.parser')

query = 'a man surfing on beach'
query = query.split()
query = '+'.join(query)
toCreate = "/Users/Janjua/Desktop/FYP/SoftwareShit/Do_Cross_Modal_Systems_Leverage_Semantic_Relationships/Demo/downloads/{}/".format(query)
if not os.path.exists(toCreate):
    os.makedirs(toCreate)
url = "https://www.google.co.in/search?q="+ query +"&source=lnms&tbm=isch"
print("URL to fetch from: ", url)
header = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
soup = page(url, header)

imgs = soup.find_all('img', attrs={'class': 'rg_i Q4LuWd tx8vtf'})
print("Len: ", len(imgs))
count = 0
for img in imgs:
    count += 1
    img = str(img)
    imgUrl = img.split('src="')[-1].replace('"', '').replace('/>', '').split(' ')[0]
    try:
        with open(toCreate + "{}.jpg".format(count), 'wb') as f:
            response = requests.get(imgUrl)
            f.write(response.content)
    except:
        print("Failed")
    print(imgUrl)
    print()
