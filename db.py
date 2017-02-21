import re
import os
import sys
from slugify import slugify
from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from pathlib import Path
from glob import glob
import pickle
from csv_data import CSVData


class DB:
    def __init__(self):
        self.category_dict = {}
        self._load_category_map()

    # Public methods

    def get_available_categories_list(self):
        print("The following food categories are available..")
        print("********")
        for category in self.category_dict:
            print(category)
        print("********")

    def update_db_full(self):
        print("Performing complete DB update..")
        for category in self.category_dict:
            self.update_db_category(category)
        print("Full DB update complete.")

    def update_db_category(self, category):
        category = str(category).lower()
        if str(category).lower() in self.category_dict:
            print("Starting update..")
            print("CATEGORY: {0}".format(category))
            print("TARGET URL: {0}".format(self.category_dict[category]))
            print("This may take some time, stay tuned...")
            total = self._get_search_results_count(self.category_dict[category])
            print("total : ",total)
            food_pages = self._fetch_calorie_links(int(total[0]), self.category_dict[category])
            script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
            execution_path = os.getcwd()
            os.makedirs('{0}/db/'.format(script_path) + category, exist_ok=True)
            os.chdir('{0}/db/'.format(script_path) + category)
            self._download_csv(food_pages, total)
            os.chdir(execution_path)
            print("DB update completed, for category: {0}".format(category))
        else:
            print("[ERROR]: Improper category specified, update failed!")

    def update_csv_objects_to_db(self):
        print('Begin dumping csv objects to db..')
        script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        execution_path = os.getcwd()
        os.chdir(script_path + '/db')
        os.makedirs('csv_objects', exist_ok=True)
        print('Dumping csv objects at: {0}'.format(script_path + '/db/csv_objects/'))
        for category in self.category_dict:
            csv_file_names = glob(category + '/*.csv')
            print(len(csv_file_names))
            ctr = 0
            for csv_file in csv_file_names:
                with open(script_path + '/db/csv_objects/' +
                                  csv_file.split('/')[1].split('.')[0] + '.pkl', 'wb') as outfile:
                    print('Dumping csv object to file: {0}'.format(script_path + '/db/csv_objects/' +
                          csv_file.split('/')[1].split('.')[0] + '.pkl'))
                    csv_obj = CSVData(script_path + '/db/' + csv_file)
                    ctr += 1
                    print('Completed processing {0}/{1} files in category {2} ..'
                          .format(ctr, len(csv_file_names), category))
                    pickle.dump(csv_obj, outfile, protocol=pickle.HIGHEST_PROTOCOL)
        print('CSV object update complete..')
        os.chdir(execution_path)

    def get_csv_objects_list(self):
        print("Loading csv objects to memory..")
        script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        execution_path = os.getcwd()
        os.chdir(script_path + '/db/csv_objects')
        objects_list = []
        pickles = glob(script_path + '/db/csv_objects' + '/*.pkl')
        for pkl in pickles:
            with open(pkl, 'rb') as infile:
                objects_list.append(pickle.load(infile))
        print("CSV objects load to list complete, total: {0}".format(len(objects_list)))
        os.chdir(execution_path)
        return objects_list

    # Protected methods follow

    def _load_category_map(self):
        try:
            with open('{0}/db/category_maps.txt'.format(os.path.dirname(os.path.realpath(sys.argv[0]))), 'r') as data:
                map_data = data.read()
                map_data = map_data.split('\n')
                for line in map_data:
                    self.category_dict[line.split('::')[0].lower()] = line.split('::')[1]
        except EnvironmentError:
            print("Could not load category map, abort!")
            sys.exit(2)

    def _get_search_results_count(self, page_url):
        conn = urlopen(page_url)
        html = conn.read()
        soup = BeautifulSoup(html, "lxml")
        div = soup.find("div", {"class": "alert alert-info result-message"})
        return re.findall(r'\d+', str(div))

    def _fetch_calorie_links(self, total, page_url):
        calorie_links = []
        append_flag = True
        root_page_nav = self._get_root_paginateURL(page_url)
        for page_index in range(0, int(total/50) + 1):
            page_results = page_index * 50
            page = root_page_nav + str(page_results) + "&amp;order=asc"
            page = page.replace("&amp;", "&")
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

    def _get_root_paginateURL(self, page_url):
        conn = urlopen(page_url)
        html = conn.read()
        soup = BeautifulSoup(html, "lxml")
        div = soup.find("a", {"class": "step"})
        return "https://ndb.nal.usda.gov" + str(div).split("href=\"")[1].split('>')[0].split("offset=")[0] + "offset="

    def _download_csv(self, food_pages, total_csv):
        csv_ct = 1
        for link in food_pages:
            conn = urlopen("https://ndb.nal.usda.gov" + link)
            html = conn.read()
            soup = BeautifulSoup(html, "lxml")
            csv_tag = soup.find("a", {"title": "Download As CSV"})
            csv_link = str(csv_tag).split("href=")[1].split(" ")[0]
            if csv_link.startswith('"') and csv_link.endswith('"'):
                csv_link = csv_link[1:-1]
            div = soup.find("div", {"id": "view-name"})
            filename = slugify(str(div).split(',', 1)[1].split('\n')[0]) + ".csv"
            print("********")
            print("Retrieving CSV: {0} of {1}".format(csv_ct, int(total_csv[0])))
            csv_ct += 1
            print(filename, "https://ndb.nal.usda.gov" + csv_link)
            if Path(filename).is_file():
                print("File already exists at the destination, skip retrieval..")
            else:
                print("Retrieving file..")
                urlretrieve("https://ndb.nal.usda.gov" + csv_link.replace("&amp;", "&"), filename)
                print("Successfully retrieved..")
            print("********")

#if __name__ == '__main__':
#     db_obj = DB()
#     db_obj.get_available_categories_list()
#     db_obj.update_db_full()
#     db_obj.update_csv_objects_to_db()
#     curr_list = db_obj.get_csv_objects_list()


