from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from config import FREENOM_PASSWORD, FREENOM_USERNAME, MAIN_DOMAIN_ID, MAIN_DOMAIN_NAME

LOGIN_PAGE_URL = 'https://my.freenom.com/clientarea.php'
LOGIN_API_URL = 'https://my.freenom.com/dologin.php'
MANAGE_DNS_PAGE_URL = 'https://my.freenom.com/clientarea.php'
MANAGE_DNS_API_URL = 'https://my.freenom.com/clientarea.php'

TTL = 300

headers = {
    'Host': 'my.freenom.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '103',
    'Origin': 'https://my.freenom.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://my.freenom.com/clientarea.php',
    'Upgrade-Insecure-Requests': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}


class FreenomInterface:

    def __init__(self):
        self.session = requests.Session()
        self.login()

    def login(self):
        login_page_response = self.session.get(LOGIN_PAGE_URL)
        login_page_soup = BeautifulSoup(login_page_response.text, 'html.parser')
        token = login_page_soup.select_one('form input').attrs['value']
        self.session.post(LOGIN_API_URL, headers=headers, data=urlencode({'token': token,
                                                                          'username': FREENOM_USERNAME,
                                                                          'password': FREENOM_PASSWORD}))

    def change_dns_targer(self, domain_name, domain_id, ip):
        manage_dns_page_response = self.session.get(MANAGE_DNS_PAGE_URL, params={'managedns': domain_name,
                                                                                 'domainid': domain_id})
        login_page_soup = BeautifulSoup(manage_dns_page_response.text, 'html.parser')
        records_list_form = login_page_soup.select_one('form#recordslistform')
        token = records_list_form.find('input', {'name': 'token'}).attrs['value']
        response = self.session.post(
            MANAGE_DNS_API_URL,
            headers=headers,
            params={'managedns': domain_name, 'domainid': domain_id},
            data=urlencode({'token': token,
                            'dnsaction': 'modify',
                            'records[0][line]': '',
                            'records[0][type]': 'A',
                            'records[0][name]': '',
                            'records[0][ttl]': str(TTL),
                            'records[0][value]': ip,
                            'records[1][line]': '',
                            'records[1][type]': 'A',
                            'records[1][name]': 'WWW',
                            'records[1][ttl]': str(TTL),
                            'records[1][value]': ip,
                            })
        )


if __name__ == '__main__':
    fi = FreenomInterface()
    fi.change_dns_targer(MAIN_DOMAIN_NAME, MAIN_DOMAIN_ID, '3.11.11.111')
