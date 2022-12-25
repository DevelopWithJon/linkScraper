from scraper import Scraper
import requests
from utils.path_utils import determine_folder

class Exporter:

    def __init__(self, scraper, folder_name):

        self.scraper = scraper
        self.directory = self.create_export_directory()
        self.folder_name = folder_name
        
    def collect_pages(self, site, url, locations):
        self.scraper.navigate(site, url, locations)
        self.download_and_save_page()

    def download_and_save_page(self):

        headers = requests.utils.default_headers()

        headers.update( {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
            }
        )
        print(len(self.scraper.urls))
        for url in self.scraper.urls:
            file = determine_folder(self.folder_name) / url.split("/")[-1]
            str_file = str(file) + ".html"
            html_code = requests.get(url, headers=headers).text
            f = open(str_file, 'w')
            f.write(html_code)
            f.close()
            
    def create_export_directory(self):
        """check if directory exists, if not create it"""
        return determine_folder("test_data")

scraper = Scraper(20)
e = Exporter(scraper=scraper, folder_name="test_data")
e.collect_pages("realtor.com", "https://www.realtor.com/realestateandhomes-search/{}", ["Orlando_FL", "Nashville_TN"])