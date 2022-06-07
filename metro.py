import selenium.common.exceptions
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


##ФУНКЦИИ##

def getcatalogItems(items, city):
    for item in items:

        #имя
        name = item.find('a', class_='catalog-item_name').get_text().strip()

        #картинка
        imgurl = item.find('div', class_='catalog-item_defaut-image')
        if imgurl is None:
            imgurl = "No image"
        else:
            imgurl = imgurl.a['data-src']

        #цена
        pricewrp = item.find('div', class_='catalog-item_price-current')
        if pricewrp is None:
            pricewrp = item.find('div', class_='catalog-item_price-lvl_current')
        price = ' '.join(re.findall('\d+\.*\d*', pricewrp.text))

        #ед.изм
        try:
            measure = pricewrp.span.get_text()[1:]
        except AttributeError:
            price = "Нет в наличии"
            measure = ""

        appendChanges(city, name, imgurl, price, measure)


def updateRow(init_row, changes):
    for i in range(0, len(init_row)):
        if changes[i] != "":
            init_row[i] = changes[i]
    return init_row

def appendChanges(city, name, imgurl, price, measure):

    pricearr = ["", "", ""]
    for i in range(0, len(cities)):
        if city == cities[i]:
            pricearr[i] = price.replace(".", ",")

    index_list = df[(df['Название'] == name)].index.tolist()

    if len(index_list) > 0:
        df.loc[index_list[0]] = updateRow(df.loc[index_list[0]], ["", *pricearr, "", ""])
    else:
        df.loc[df.shape[0]] = [name, *pricearr, measure, imgurl]

def getproductItems(items, city):
    for item in items:

        #имя
        name = item.find('a', class_='base-product-name').get_text().strip()

        #картинка
        imgurl = item.find('img', class_='base-product-photo__image')
        if imgurl is None:
            imgurl = "No image"
        else:
            imgurl = imgurl['src']

        #цена
        pricewrp = item.select('.base-product-prices__actual > span')
        price = pricewrp[0].get_text()

        # ед.изм
        try:
            measure = pricewrp[2].get_text()[1:]
        except AttributeError:
            price = "Нет в наличии"
            measure = ""

        appendChanges(city, name, imgurl, price, measure)


def startParsing(soup, city):
    items = soup.select('.catalog-list__wrapper > .catalog-item')
    if len(items) == 0:
        items = soup.select('.base-product-item')
        getproductItems(items, city)
    else:
        getcatalogItems(items, city)

def changeCity(city):
    driver.get("https://online.metro-cc.ru/category/myasnye/myaso")
    try:
        driver.find_elements(By.CLASS_NAME, "header__tradecenter_question-btn")[1].click()
    except IndexError:
        print("No popup window, continuing")
    try:
        elem = driver.find_element(By.CLASS_NAME, "header-delivery-info__icon-wrapper")
    except selenium.common.exceptions.NoSuchElementException:
        elem = driver.find_element(By.CLASS_NAME, "header-address__receive-button")
    elem.click()
    driver.find_element(By.XPATH, '//div[@class="obtainments-list"]/label[2]').click()
    driver.find_element(By.XPATH, '//div[@class="pickup__select"]/div[@class="select-item"][1]/div').click()
    select = driver.find_element(By.XPATH, '//div[@class="pickup__select"]/div[@class="select-item"][1]//input')
    select.send_keys(city)
    select.send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, '//div[@class="pickup__apply-btn-desk"]/button').click()
##КОНЕЦ ФУНКЦИЙ##

cities = ["Москва", "Томск", "Иркутск"]

df = pd.DataFrame({"Название": [],
                   "Цена "+cities[0]: [],
                   "Цена "+cities[1]: [],
                   "Цена "+cities[2]: [],
                   "Ед. изм": [],
                   "Картинка": []})
url = "https://online.metro-cc.ru/category/myasnye/myaso?page="
driver = webdriver.Chrome()
for i in range(0, 3):
    changeCity(cities[i])
    for j in range(1, 11):
        driver.get(url + str(j))
        soup = BeautifulSoup(driver.page_source, "lxml")
        startParsing(soup, cities[i])

df.to_excel('metro.xlsx', sheet_name='metro', index=False)
