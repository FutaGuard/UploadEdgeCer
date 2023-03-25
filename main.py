from requests import Session
import config
from typing import List
from json.decoder import JSONDecodeError


class Notify:
    def __init__(self) -> None:
        self.endpoint = f'https://api.telegram.org/bot{config}/'
        self.client: Session = Session()

    def send_message(self, chat_id: int, text: str):
        payload = {'chat_id': chat_id, 'text': text}
        url = self.endpoint + 'sendMessage'
        self.client.post(url, json=payload)


class CFAPI:
    def __init__(self, client: Session) -> None:
        self.endpoint: str = 'https://api.cloudflare.com/client/v4/zones/{zone}/'
        self.domains: List[str] = config.DOMAINS
        self.client = client

    def certificate_packs_list_certificate_packs(self, zoneid: str) -> dict:
        """_summary_

        Args:
            domain (str): _description_

        Returns:
            dict: _description_
        """
        url = self.endpoint + 'ssl/certificate_packs'
        r = self.client.get(url.format(zone=zoneid))
        if not r.ok:
            print('list cert error')
            print(r.text)
            return
        try:
            return r.json()
        except JSONDecodeError:
            print('list cert parse JSON err')

    def create_ssl(self, zoneid: str, domain: str) -> dict:
        url = self.endpoint + 'custom_certificates'
        prikey = open(
            f'/home/ubuntu/.acme.sh/*.{domain}/*.{domain}.key', 'r').read()
        cert = open(
            f'/home/ubuntu/.acme.sh/*.{domain}/fullchain.cer', 'r').read()

        payload = {
            'certificate': cert,
            'private_key': prikey,
            'bundle_method': 'ubiquitous',
            'type': 'sni_custom'
        }
        r = self.client.post(url.format(zone=zoneid), json=payload)
        if not r.ok:
            print('create ssl failed')
            print(r.text)
            return

        try:
            return r.json()
        except JSONDecodeError:
            print('create ssl JSON parse error')
            print(r.text)

    def edit_ssl(self, zoneid: str, domain: str, certid: str) -> dict:
        url = self.endpoint + 'custom_certificates/{certid}'
        prikey = open(
            f'/home/ubuntu/.acme.sh/*.{domain}/*.{domain}.key', 'r').read()
        cert = open(
            f'/home/ubuntu/.acme.sh/*.{domain}/fullchain.cer', 'r').read()

        payload = {
            'certificate': cert,
            'private_key': prikey,
            'bundle_method': 'ubiquitous',
            'type': 'sni_custom'
        }
        r = self.client.patch(url.format(
            zone=zoneid, certid=certid), json=payload)
        if not r.ok:
            print('edit ssl error')
            print(r.text)
            return

        try:
            return r.json()
        except JSONDecodeError:
            print('edit ssl parse JSON err')


if __name__ == '__main__':
    client = Session()
    client.headers = {
        'Authorization': config.CF_TOKEN}
    cf = CFAPI(client)
    bot = Notify()

    for domain in config.DOMAINS:
        zoneid = config.DOMAINS[domain]
        result = cf.certificate_packs_list_certificate_packs(zoneid)

        certlist = list(
            filter(lambda x: x['type'] == 'legacy_custom', result['result']))
        if len(certlist) != 1:
            r = cf.create_ssl(zoneid=zoneid, domain=domain)
            if not r:
                text = '❌ SSL 上傳失敗\n' \
                       '域名：{domain}'.format(domain=domain)
                bot.send_message(config.CHAT_ID, text)
        else:
            certid = certlist[0]['id']
            r = cf.edit_ssl(zoneid=zoneid, certid=certid, domain=domain)
            if not r:
                text = '❌ SSL 上傳失敗\n' \
                       '域名：{domain}'.format(domain=domain)
                bot.send_message(config.CHAT_ID, text)
