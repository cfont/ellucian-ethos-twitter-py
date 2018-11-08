# Written for Python 3
#
# pip install of "requests" is required
# 
#
import requests

class Ethos:
    auth_url = "https://integrate.elluciancloud.com"
    ethos_integration_url = "https://integrate.elluciancloud.com"

    # initialize variables
    api_key = ''
    jwt = ''

    def __init__(self,api_key):
        self.api_key = api_key

    def get_jwt(self):
        if self.api_key:
            print('The Ethos API Key being used inside the get_jwt is: {}'.format(self.api_key))
            headers = { 'Authorization': "Bearer " + self.api_key}
            ### TODO: add try/except block here
            response = requests.request("POST", self.auth_url + "/auth", headers=headers)

            if response.status_code == 200:
                self.jwt = response.text
                print(self.jwt)
            elif response.status_code == 406:
                raise Exception('Api Key is invalid',response.status_code,response.text)
            else:
                raise Exception('Error calling Ethos Integration authorization endpoint',response.status_code,response.text)
        else:
            raise Exception('Api Key not defined')

    def get_change_notifications(self,retry=True):
        if not self.jwt:
            self.get_jwt()

        headers = {
            'Authorization': "Bearer " + self.jwt,
            'Accept': 'application/vnd.hedtech.change-notifications.v2+json'}
        ### TODO: add try/except block here
        response = requests.request("GET", self.ethos_integration_url + "/consume", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401 and retry:
            print('JWT has expired')
            self.get_jwt()
            return self.get_change_notifications(retry=False)
        else:
            raise Exception('Error calling Ethos Integration consume endpoint',response.status_code,response.text)