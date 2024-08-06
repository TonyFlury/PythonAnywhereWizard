from wizard_logging import logging, WizardLogger

logger:WizardLogger = logging.getLogger('PyAnywhereAccess')

import requests

class PyAnywhere:
    """Basic class to allow PythonAnywhere access"""
    def __init__(self, **kwargs):
        self.username: str = ''
        self.token : str = ''
        self.host: str = ''

        for data_item in {'username', 'token', 'host'}:
            if data_item not in kwargs:
                logger.critical(f'Missing \'{data_item}\' from configuration')
                raise AttributeError(f'Missing PythonAnywhere \'{data_item}\' from configuration data')

            setattr(self, data_item, kwargs[data_item])

        # Apps are optional but useful if defined
        if 'apps' in kwargs:
            self._apps = [app.strip() for app in kwargs['apps'].split(',')]
        else:
            self._apps = []

    def _url(self, endpoint):
        return f'https://{self.host}/api/v0/user/{self.username}/{endpoint}/'

    def _get(self, endpoint):
        return requests.get( self._url(endpoint),
                             headers={'Authorization': f'Token {self.token}'}
                             )

    def _post(self, endpoint, data):
        return requests.post(self._url(endpoint),
                            headers={'Authorization': f'Token {self.token}'},
                            data = {'input': data}
                            )

    def verify(self):
        """Simply get the CPU time from the server to verify the data
           Returns true if the connection worked - otherwise raise an exception
        """
        response = self._get('cpu')
        if response.status_code == 200:
            return True
        else:
            raise ConnectionRefusedError(f'Unable to connect to PythonAnywhere - status code {response.status_code}')

    def consoles(self, console_type: str = '', name_match: str = ''):
        """Enumerate the consoles available on this connection"""
        response = self._get('consoles')
        if response.status_code != 200:
            raise ConnectionError(f'Unable to fetch console list from PythonAnywhere - status code {response.status_code}')

        for console in response.json():
            if (console_type and console['executable'] == console_type) or (console_type == ''):
                if (name_match == '') or (name_match and name_match in console['name']):
                    yield console['name'], console['id']

    def consoles_for_apps(self, console_type: str = ''):
        """Yield a dictionary of console ids for each defined app"""
        if not self._apps:
            return None

        for name, id in self.consoles():
            for app in self._apps:
                if app in name:
                    yield app, id

    def send_to_console(self, console_type:str='', console_name:str=None, commands:list[str]=''):
        if self._apps :
            consoles = self.consoles_for_apps( console_type=console_type)
        else:
            consoles = self.consoles(console_type=console_type)

        found_id = None
        for console, console_id in consoles:
            if console_name not in console:
                continue
            else:
                if found_id is None:
                    found_id = console_id
                else:
                    raise AttributeError('More than one console with matched names')

        for command in commands:
            resp = self._post( endpoint= f'consoles/{found_id}/send_input', data=command+'\n')
            if resp.status_code != 200:
                print(resp.content)
                continue

            resp = self._get( endpoint=f'consoles/{found_id}/get_latest_output')
            print(resp.status_code)
            yield resp.json()['output']



