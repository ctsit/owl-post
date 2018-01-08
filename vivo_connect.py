import random
import requests

from queries import check_n_value
from thing import Thing

class Connection(object):
    def __init__(self, vivo_url, user, password, u_endpoint, q_endpoint):
        self.user = user
        self.password = password
        self.update_endpoint = u_endpoint
        self.query_endpoint = q_endpoint
        self.vivo_url = vivo_url

    def check_n(self, n):
        #create a Thing to test n number
        thing_check = Thing(self)
        thing_check.n_number = n
        params = {'Thing': thing_check}
        #use query to check if n number exists
        response = check_n_value.run(self, **params)
        return response

    def gen_n(self):
        bad_n = True
        while bad_n:
            # get an n
            n = "n" + str(random.randint(1,9999999999))
            # check if n is taken
            bad_n = self.check_n(n)
        return n

    def run_update(self, template):
        print("Query:\n" + template)
        payload = {
            'email': self.user,
            'password': self.password,
            'update': template
        }
        url = self.update_endpoint
        response = requests.post(url, params=payload)
        return response

    def run_query(self, template):
        print("Query:\n" + template)
        payload = {
            'email': self.user,
            'password': self.password,
            'query': template
        }
        url = self.query_endpoint
        headers = {'Accept': 'application/sparql-results+json'}
        response = requests.get(url, params=payload, headers=headers)
        return response
