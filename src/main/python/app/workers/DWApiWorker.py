# Doomworld idgames public api worker wrapper.
# Documentation: https://www.doomworld.com/idgames/api/
import requests, enum, re

from PyQt5.QtCore import QThread, pyqtSignal
from app.workers.WorkerPool import *

SEARCH_TYPES = ['filename', 'title', 'author', 'email', 'description', 'credits', 'editors', 'textfile']

class DWApiMethod(enum.Enum):
    IS_ALIVE = 1
    SEARCH = 2
    ABOUT = 3
    GET = 4
    RANDOM = 5

def api_worker_wrapper(method, done_handlers=[], *api_args):
    worker = DWApiWorker(method, *api_args)
    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class DWApiWorker(QThread):
    done = pyqtSignal(object)

    def __init__(self, api_method, *api_args):
        super(DWApiWorker, self).__init__()

        api_calls = dict((data, getattr(self, data.name.lower())) for data in DWApiMethod)

        self.api_call = api_calls[api_method]
        self.api_args = api_args

    def run(self):
        result = None
        err = None

        try:
            result = self.api_call(*self.api_args)
        except Exception as e:
            err = e
        except requests.exceptions.HTTPError as e:
            err = e
        except requests.exceptions.ConnectionError as e:
            err = e
        except requests.exceptions.Timeout as e:
            err = e
        except requests.exceptions.RequestException as e:
            err = e

        self.done.emit((result, err))

    def req(self, query):
        url = 'https://www.doomworld.com/idgames/api/api.php?{}&out=json'
        response = requests.get(url.format(query))
        response.raise_for_status()

        result = response.json()
        content = result.get('content', False)
        if content:
            result.pop('content')
            return {**content, **result}

        response.close()
        return result

    def is_alive(self):
        result = self.req('action=ping')
        return result['status'] == 'true'

    def about(self):
        result = self.req('action=about')
        return result

    # type = 'file' or 'id'
    def get(self, key, get_type):
        result = self.req('action=get&{type}={key}'.format(type=get_type, key=key))
        error = result.get('error', False)

        if error:
            raise Exception(error)

        return result

    def search(self, query, search_by='filename'):
        # search query demands at least 3 chars, and uses '_' as an 'any' type char
        # 'gd'.ljust(3, '_') -> 'gd_'
        # 'doom'.ljust(3, '_') -> 'doom'
        query = query.ljust(3, '_')

        result = self.req('action=search&query={}&type={}'.format(query, search_by))
        error = result.get('error', False)

        if error:
            raise Exception(error)

        return result
    
    def random(self):
        url = 'https://www.doomworld.com/idgames/?random'

        random_response = requests.get(url)
        random_response.raise_for_status()

        # parsing html with regex... lol.
        # Its probably fine, since we are only looking for the idgamesprotocol attribute
        idgamesprotocol = re.search('idgames:\/\/\d+', random_response.text)
        idgames_id = idgamesprotocol.group().replace('idgames://', '')

        random_response.close()
        return self.get(idgames_id, 'id')