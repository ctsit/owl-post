from thing import Thing

def get_params(connection):
    thing = Thing(connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    print('=' * 20 + "\nRunning n check\n" + '=' * 20)
    uri = connection.vivo_url + params['Thing'].n_number

    q = """SELECT ?u WHERE{{?u <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Thing> . FILTER (?u=<{}>)}}""".format(uri)

    response = connection.run_query(q)

    n_check = response.json()
    try: 
        if n_check['results']['bindings'][0]['u']:
            return True
    except IndexError as e:
        if e.message != "list index out of range":
            raise
        else:
            return False
