from thing import Thing

def get_params(connection):
    thing = Thing (connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    thing = params['Thing']
    identity = ""
    if thing.category == 'academic_article':
        identity = 'http://purl.org/ontology/bibo/AcademicArticle'
    if thing.category == 'journal':
        identity = 'http://purl.org/ontology/bibo/Journal'
    if thing.category == 'person':
        identity = 'http://xmlns.com/foaf/0.1/Person'
    if thing.category == 'publisher':
        identity = 'http://vivoweb.org/ontology/core#Publisher'

    q = """SELECT ?uri ?label WHERE {{?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{}> . ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER (regex (?label, "{}", "i")) }}""".format(identity, thing.name)

    print('=' * 20 + "\nFinding n number\n" + '=' * 20)
    response = connection.run_query(q)

    lookup = response.json()
    matches = {}
    for listing in lookup['results']['bindings']:
        name = listing['label']['value']
        url = listing['uri']['value']
        url_n = url.rsplit('/', 1)[-1]
        matches[url_n] = name

    return matches