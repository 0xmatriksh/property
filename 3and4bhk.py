from selenium import webdriver
from time import sleep
import pandas as pd

# webdriver setup
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

# load the url
url = 'https://www.propertiesguru.com/residential-search/2bhk-residential_apartment_flat-for-sale-in-new_delhi'
driver.get(url)
sleep(2)

# to filter to choose 3 and 4bhk
driver.find_element_by_xpath('/html/body/nav[1]/div/ul[1]/li[3]/a').click()

for i in range(2,5):
    driver.find_element_by_xpath(f'/html/body/nav[1]/div/ul[1]/li[3]/ul/li/div/ul/li[{i}]').click()
    sleep(1)

sleep(1)
driver.find_element_by_xpath('/html/body/nav[1]/div/ul[1]/li[3]/a').click()
sleep(2)

# code to scroll the page to end to load all the properties.
l_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    sleep(2)
    n_height = driver.execute_script("return document.body.scrollHeight")

    if l_height == n_height:
        break
    l_height = n_height

#the logic to get text() with the help javascript [for name and address]
def getElementByXpath_Name(path) :
   return driver.execute_script(f'return document.evaluate({path}, document, null, XPathResult.STRING_TYPE, null ).stringValue; ')

def StringtoNumber(string):
    return ''.join(char for char in string if char.isdigit())

# to count the number of properties in search result
divs = '//*[@id="properties"]/div/div'
count = len(driver.find_elements_by_xpath(divs))

def listtoString(listA):
    strA = " , "
    return (strA.join(listA))

def Stringtolist(strB):
    listB = list(strB.split(","))
    return listB

#code to get all the data of particular property
total = []
for i in range(2, count+1):
    name_addr = getElementByXpath_Name(f'\'//*[@id=\"properties\"]/div/div[{i}]/div[1]/div/div[1]/a\'')
    nameloc = Stringtolist(name_addr)
    data = {
        'Name': nameloc[0],
        'BHK': driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[1]/div/div[1]/h1').text[:5],
        'Price': driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[1]/div/div[2]/div/span[2]').text,
        'Price/Unit': (driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[1]/div/div[2]/div/span[3]').text)[1:],
        'Area': StringtoNumber((driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/div[1]/div[1]').text)[5:9]),
        'Facing': (driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/div[1]/div[2]').text)[7:],
        'Status': (driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/div[1]/div[3]').text)[7:],
        'Details': listtoString([
            driver.find_element_by_xpath(
                f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/ul/li[1]').text,
            driver.find_element_by_xpath(
                f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/ul/li[2]').text,
            driver.find_element_by_xpath(
                f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/ul/li[3]').text,
            driver.find_element_by_xpath(
                f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/ul/li[4]').text,
        ]),
        'Person': driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/div[2]/div[2]/span[1]').text,
        'Posted': (driver.find_element_by_xpath(f'//*[@id="properties"]/div/div[{i}]/div[2]/div[2]/div[2]/div[2]/span[2]').text)[8:],
    }
    total.append(data)
sleep(2)
# print(total)

df = pd.DataFrame(total)

#column size formatting according to max width of content in it
writer = pd.ExcelWriter('./3and4bhk.xlsx') 
df.to_excel(writer, sheet_name='property', index=False, na_rep='NaN')

for column in df:
    column_length = max(df[column].astype(str).map(len).max(), len(column))
    col_idx = df.columns.get_loc(column)
    writer.sheets['property'].set_column(col_idx, col_idx, column_length)

writer.save()
# print(df)


driver.close()
