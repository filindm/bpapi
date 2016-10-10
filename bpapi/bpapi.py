import requests
from requests.auth import HTTPDigestAuth
import json
import logging
import time


logger = logging.getLogger(__name__)

_verify = True


''' 
    Class representing the BrightPattern List API
'''
class BpListApi:


    def __init__(self, hostname, tenant, login, password, ssl=False):
        self.auth = HTTPDigestAuth(login, password)
        proto = 'https' if ssl else 'http'
        port = 8443 if ssl else 88
        self.base_url = u'{proto}://{hostname}:{port}/admin/ws/t/{tenant}'.format(
            'utf-8',
            proto=proto, 
            hostname=hostname, 
            port=port, 
            tenant=tenant)


    def get_campaigns(self):
        url = u'{base_url}/campaign/getAll'.format('utf-8', base_url=self.base_url)
        r = requests.get(url, auth=self.auth, verify=_verify)
        r.raise_for_status()
        return [Campaign(self, **x) for x in r.json()]


    def get_list(self, name):
        return List(self, name)


'''
    Outbound Campaign
'''
class Campaign(object):

    def __init__(self, api, name, lists, state):
        self.api = api
        self.name = unicode(name)
        self.lists = [List(api, x) for x in lists]
        self.state = state

    def __str__(self):
        return u'<Campaign {}>'.format(self.name).encode('utf-8')

    def __repr__(self):
        return self.__str__()


'''
    Outbound Call List
'''
class List(object):

    def __init__(self, api, name):
        self.api = api
        self.name = unicode(name)


    def add_record(self, record):
        pass


    def add_records(self, records):
        url = u'{base_url}/callinglist/addAll/{list_name}'.format(base_url=self.api.base_url, list_name=self.name)
        logger.debug(u'url: {}'.format(url))
        headers = {
            'Content-type': 'application/json'
        }
        r = requests.post(url, 
            data=json.dumps(records),
            headers=headers, 
            auth=self.api.auth, 
            timeout=15,
            verify=_verify)
        r.raise_for_status()
        return r.json()


    def update_record(self, record):
        pass

    def query_record(self, keys):
        pass


    def delete_all_records(self):
        url = u'{base_url}/callinglist/deleteAll/{list_name}'.format(base_url=self.api.base_url, list_name=self.name)
        logger.debug(u'url: {}'.format(url))
        r = requests.post(url, auth=self.api.auth, timeout=15, verify=False)
        r.raise_for_status()


    def get_completed_records(self):
        pass

    def get_updated_records(self):
        pass


    def get_records(self, campaign_name):
        url = u'{base_url}/callinglist/getAll/{list_name}/{campaign_name}'.format(
            base_url=self.api.base_url,
            list_name=self.name,
            campaign_name=campaign_name)
        logger.debug(u'url: {}'.format(url))
        auth = self.api.auth
        idx = 0
        bufsize = 1000
        while True:
            data = {
                'fromIndex': idx,
                'maxSize': bufsize
            }
            headers = {
                'Content-type': 'application/json'
            }
            logger.debug('performing http request')
            try:
                r = requests.post(url, 
                    data=json.dumps(data), 
                    headers=headers, 
                    auth=auth, 
                    verify=_verify, 
                    timeout=15)
                r.raise_for_status()
                results = r.json()
                logger.debug(u'got results: {} rows'.format(len(results)))
                # if not results:
                #     logger.debug('empty results, finishing')
                #     break
                for result in results:
                    idx = max(idx, result['index'])
                    yield result['entry']
                if len(results) < bufsize:
                    break
                idx += 1
            except requests.exceptions.Timeout:
                logger.info('Timed out, reconnecting')
            except requests.exceptions.ConnectionError:
                logger.info('Connection error, reconnecting')
            time.sleep(1)

    
    def __str__(self):
        print 'before'
        s = u'<List {}>'.format(self.name).encode('utf-8')
        print s
        print 'after'
        return s

    
    def __repr__(self):
        return self.__str__()

