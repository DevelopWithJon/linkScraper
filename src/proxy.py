import pandas as pd  
import requests

import time
from utils.configs import ROTATE_PROXY_OFFSET

class Proxy:

    def __init__(self) -> None:
        self.proxy_list = []
        self.last_rotate_time = None
        self.offset = ROTATE_PROXY_OFFSET

    def rotate_proxies(self) -> None:
        """
        """
        print("Checking if proxies need to rotate...")
        if self._check_time() or len(self.proxy_list) < 5:
            print("Rotating proxies")
            r = requests.get("https://free-proxy-list.net/")
            table = pd.read_html(r.content)[0]
            self.proxy_list = list(table[table["Country"] == "United States"][["IP Address", "Port"]].values.tolist())
            self.last_rotate_time = time.time()

    def _check_time(self) -> bool:
        """
        """
        current_time = time.time()
        if (self.last_rotate_time is None) or (current_time - self.last_rotate_time >= self.offset):
            return True
        else:
            return False
    
    def remove_bad_proxy(self, proxy) -> None:
        print("removing bad proxy...")
        self._remove_proxy(proxy)
    
    def _remove_proxy(self, proxy) -> None:
        print(proxy)
        print(self.proxy_list)
        if (self.proxy_list) and (proxy in self.proxy_list):
            self.proxy_list.remove(proxy)
            print("removed proxy from proxy list")
        else:
            print("proxy not in list")