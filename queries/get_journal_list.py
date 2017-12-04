def get_params(connection):
    params = {}
    return params

def run(connection, **params):
    q = """ select ?label ?u where { ?u <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/Journal> . ?u <http://www.w3.org/2000/01/rdf-schema#label> ?label . } """

    print('=' * 20 + '\nGenerating journal list\n' + '=' * 20)
    response = connection.run_query(q)
    print(response)

    journal_dump = response.json()
    all_journals = {}
    for listing in journal_dump['results']['bindings']:
        j_name = listing['label']['value']
        j_url = listing['u']['value']
        j_n = j_url.rsplit('/', 1)[-1]
        all_journals[j_n] = j_name       

    return all_journals