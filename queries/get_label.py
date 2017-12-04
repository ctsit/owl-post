from thing import Thing

def get_params(connection):
    thing = Thing(connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    subj = connection.vivo_url + params['Thing'].n_number

    q = """ SELECT ?label WHERE {{<{}> <http://www.w3.org/2000/01/rdf-schema#label> ?label .}} """.format(subj)

    print('=' * 20 + '\nFinding label\n' + '=' * 20)
    response = connection.run_query(q)
    print(response)

    #Navigate json
    finding = response.json()
    label = finding['results']['bindings'][0]['label']['value']

    return label