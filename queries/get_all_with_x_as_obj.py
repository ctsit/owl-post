from thing import Thing

def get_params(connection):
    thing = Thing(connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    obj = connection.vivo_url + params['Thing'].n_number

    q = """ SELECT ?s ?p ?o WHERE{{?s ?p <{}> .}} """.format(obj)

    print('=' * 20 + '\nGenerating triples\n' + '=' * 20)
    response = connection.run_query(q)
    print(response)

    #Navigate json
    triple_dump = response.json()
    triples = []
    for listing in triple_dump['results']['bindings']:
        subj = listing['s']['value']
        pred = listing['p']['value']
        trip = "<" + subj + "> <" + pred + "> <" + obj + ">"
        triples.append(trip)

    return triples