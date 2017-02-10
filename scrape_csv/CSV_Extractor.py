import re
import os
import sys
from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import csv


def get_search_results_count(page_url):
    conn = urlopen(page_url)
    html = conn.read()
    soup = BeautifulSoup(html, "lxml")
    div = soup.find("div", {"class": "alert alert-info result-message"})
    return re.findall(r'\d+', str(div))


def fetch_calorie_links(total, page_url):
    calorie_links = []
    append_flag = True
    for page_index in range(0, int(total/50) + 1):
        page_results = page_index * 50
        page = page_url + str(page_results) + "&order=asc"
        conn = urlopen(page)
        html = conn.read()
        soup = BeautifulSoup(html, "lxml")
        links = soup.find_all('a')
        for tag in links:
            link = tag.get('href', None)
            if link is not None:
                if "/ndb/foods/show/" not in link:
                    continue
                if append_flag:
                    calorie_links.append(link)
                    append_flag = False
                else:
                    append_flag = True
    return calorie_links


def download_csv(food_pages, category):
    os.makedirs(str(category).lower(), exist_ok=True)
    os.chdir(str(category).lower())
    print("Preparing downloads for category: " + str(category).lower())
    for link in food_pages:
        conn = urlopen("https://ndb.nal.usda.gov" + link)
        html = conn.read()
        soup = BeautifulSoup(html, "lxml")
        csv_tag = soup.find("a", {"title": "Download As CSV"})
        csv_link = str(csv_tag).split("href=")[1].split(" ")[0]
        if csv_link.startswith('"') and csv_link.endswith('"'):
            csv_link = csv_link[1:-1]
        div = soup.find("div", {"id": "view-name"})
        filename = str(div).split(',', 1)[1].split('\n')[0]
        print("********")
        print(filename, "https://ndb.nal.usda.gov" + csv_link)
        print("********")
        urlretrieve("https://ndb.nal.usda.gov" + csv_link.replace(';', '&'), filename + ".csv")


def main():
    page_url = sys.argv[1]
    total = get_search_results_count(page_url)
    food_pages = fetch_calorie_links(int(total[0]), page_url)
    download_csv(food_pages, sys.argv[2])


main()

