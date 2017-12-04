from thing import Thing

def get_params(connection):
    thing = Thing(connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    subj = connection.vivo_url + params['Thing'].n_number

    q = """ SELECT ?s ?p ?o WHERE{{<{}> ?p ?o .}} """.format(subj)

    print('=' * 20 + '\nGenerating triples\n' + '=' * 20)
    response = connection.run_query(q)
    print(response)

    #Navigate json
    triple_dump = response.json()
    triples = []
    for listing in triple_dump['results']['bindings']:
        pred = listing['p']['value']
        obj = listing['o']['value']
        trip = "<" + subj + "> <" + pred + "> <" + obj + ">"
        triples.append(trip)

    return triples