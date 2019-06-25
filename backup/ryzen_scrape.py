import bs4
from bs4 import BeautifulSoup
import datetime
import os
import sys
import re
from urllib import urlopen

# for weird " ascii issue"
reload(sys)
sys.setdefaultencoding('utf8')

deals = set()

fileLength = 0
if os.path.isfile('laptops.csv'):
    f = open("laptops.csv", "r")
    fileContent = f.readlines()
    fileLength = len(fileContent)
    for line in fileContent:
        print line
        deals.add(line[0:line.index(',')])

if fileLength == 0:
    f = open("laptops.csv", "w")
    f.write("title,price,date\n")

f.close()

print "\n\n!!!!end of previous deals!!!\n\n"

f = open("laptops.csv", "a")
for n in range(1, 11):
    ryzen_url = "https://slickdeals.net/newsearch.php?page=" + str(n) + "&q=ryzen%20laptop"
    url_client = urlopen(ryzen_url)
    page_html = url_client.read()
    url_client.close()
    # html parsing
    page_soup = BeautifulSoup(page_html, "html.parser")
    containers = page_soup.findAll("div", {"class":"resultRow"});
    for container in containers:
        isExpired = len(container.findAll("div", {"class":"expired"}))  # is 1 if expired
        if isExpired:
            continue
        title = container.findAll("a", {"class":"dealTitle"})[0].text.strip().replace(",", " ")
        title = re.sub(r'[^\x00-\x7F]+','', title)
        if title in deals:
            continue
        print title
        price = container.findAll("span", {"class":"price"})[0].text.strip().replace(",", " ")
        if price == "":
            searchObj = re.search(r'\$\d*\.?\d*', title)
            if searchObj:
                price = searchObj.group()
            else:
                price = "price NOT found!"
        print price
        date = "date NOT found"
        date_today = datetime.date.today()
        date_text = container.findAll("div", {"class":"dealInfo"})[0].div.text.replace("Today", date_today.strftime("%-m/%d/%Y"))
        searchObj = re.search(r'\d+/\d+/\d+ \d+:\d+ [AP]M', date_text)
        if searchObj:
            date = searchObj.group()
        print date
        f.write(title + "," + price + "," + date + "\n")
f.close()


