import requests
import config
from typing import List
from json.decoder import JSONDecodeError


class CFAPI:
    def __init__(self) -> None:
        self.endpoint: str = 'https://api.cloudflare.com/client/v4/zones/{zone}/'
        self.domains: List[str] = config.DOMAINS

    def certificate_packs_list_certificate_packs(self, domain: str) -> dict:
        url = self.endpoint + 'ssl/certificate_packs'
        r = requests.get(url)
        if not r.ok:
            print('list cert error')
            print(r.text)
            return
        try:
            return r.json()
        except JSONDecodeError:
            print('list cert parse JSON err')
            
