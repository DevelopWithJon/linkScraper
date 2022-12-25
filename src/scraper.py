from utils.configs import BASE_URL_MAP, CITY_LIST, TODAY
from utils.path_utils import determine_folder
from utils.string_utils import format_cities
from utils.request_utils import APIRateLimiter, get
from utils.proxy_utils import format_proxy

from tenacity import retry, retry_if_exception_type, wait_random_exponential

import requests

from bs4 import BeautifulSoup as bs
from proxy import Proxy
import random 

class Scraper():

    RATE_LIMIT = 10
    RATE_SECOND_DELTA = 1

    def __init__(self, depth) -> None:
        self.urls = []
        self.visited = set()
        self.current_page = 1
        self.current_counter = 0
        self.depth = depth
        self.proxy_obj = Proxy()

        self._rate_limiter = APIRateLimiter(
            self.RATE_LIMIT, self.RATE_SECOND_DELTA
        )

    def _next_page(self, site, location, url) -> None:
        if site == "realtor.com":
            url = url.format(location) + "/pg-" + str(self.current_page)
            print(f"went to page #{self.current_page}")
            print(f"current url count: {len(self.urls)}")
            resp = self._make_request(url, use_proxy=True)
            soup = bs(resp.text, 'html.parser')
            self.current_page+=1

            if not soup.find(id="error-404"):
                return soup
        return None

    def _increment_current_counter(self):
        self.current_counter +=1

    def _request(self, site, url, location):

        resp = self._make_request(url, location, use_proxy=True)
        soup = bs(resp.text, 'html.parser')
        previous_url_count = len(self.urls)

        while True:
            if (site == "realtor.com"):

                self._collect_urls(soup, site)
                soup = self._next_page(site, location, url)

                if (self.current_counter < self.depth) and (resp) and (len(self.urls) > previous_url_count):
                    previous_url_count = len(self.urls)

                else:
                    if (len(self.urls) <= previous_url_count):  # checking for error
                        print("something went wrong")
                        print(soup)
                        return False

                    print("depth limite reached")
                    print(self.current_counter)
                    self.current_counter = 0
                    self.current_page = 2
                    break

            return True


    @retry(
    retry=retry_if_exception_type(requests.exceptions.Timeout),
    wait=wait_random_exponential(multiplier=0.5, max=10)
    stop=stop_after_attempt(3)
)
    def _make_request(self, url, location=None, use_proxy=False):
        """
        """
        headers = requests.utils.default_headers()

        headers.update( {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
            }
        )
        current_url = url

        if location:
            current_url = url.format(location)
        
        # try to rotate proxies
        if use_proxy:
            self.proxy_obj.rotate_proxies()
            proxy_choice = list(random.choice(self.proxy_obj.proxy_list))

            formatted_proxy = format_proxy(proxy_choice)
            print(f"Using proxy={formatted_proxy['http']}")
            try:
                with self._rate_limiter:
                    return get(current_url, headers=headers, proxies=formatted_proxy, timeout=2)

            except requests.exceptions.Timeout as e:
                # Maybe set up for a retry, or continue in a retry loop
                print(f"Timeout Error\n Bad proxies found={formatted_proxy['http']}")
                print(f"Removing proxy and trying a new proxy...")
                self.proxy_obj.remove_bad_proxy(proxy_choice)
                print(f"Retrying request for url={current_url}...")
                raise requests.exceptions.Timeout
            except requests.exceptions.TooManyRedirects:
                # Tell the user their URL was bad and try a different one
                pass
            except requests.exceptions.RequestException as e:
                # catastrophic error. bail.
                print(e)
        else:
            try:
                with self._rate_limiter:
                    return get(current_url, headers=headers, timeout=2)
            except Exception as e:
                print(e)

    def _collect_urls(self, soup, site) -> None:
        """
        """
        links = soup.find_all('a', href=True)
        for link in links:
            if self.current_counter >= self.depth:
                break

            href = link['href']
            if href.startswith("/realestateandhomes-detail/"):
                self.urls.append(BASE_URL_MAP[site] + href)
                self._increment_current_counter()

    def _save_pages(self, pages):
        """"""
        for ind, page in enumerate(pages):
            file_name = "real_estate_listing_data_" + TODAY + "_" + str(ind+1) + ".html"
            path = determine_folder("data") / file_name
            with open(path, 'w') as f:
                f.write(page)
            print("Done")

    def navigate(self, site, url, locations) -> None:

        for location in locations:
            print(f"starting scrape for {location}")
            request_status = self._request(site, url, location)
            if request_status == False:
                break
        print(f"collected {len(self.urls)} urls")
        
    def scrape(self):

        pages = []
        for url in self.urls:
            resp = self._make_request(url, use_proxy=True)
            pages.append(resp.text)
        print(f"saving {len(pages)} pages")
        self._save_pages(pages)

    def save_urls(self):
        with open("urls.txt", 'w') as f:
            for url in self.urls:
                f.write(f"{url}\n")
    

s = Scraper(50)
cities = format_cities("realtor.com", CITY_LIST)
s.navigate("realtor.com", "http://www.realtor.com/realestateandhomes-search/{}", ["Orlando_FL"])
s.save_urls()