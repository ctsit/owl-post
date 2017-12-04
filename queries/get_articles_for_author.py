from author import Author

def get_params(connection):
    author = Author(connection)
    params = {'Author': author}
    return params

def run(connection, **params):
    q = """ SELECT ?label ?article WHERE {{<{url}{Author_n}> <http://vivoweb.org/ontology/core#relatedBy> ?relation . ?relation <http://vivoweb.org/ontology/core#relates> ?article . ?article <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/AcademicArticle> . ?article <http://www.w3.org/2000/01/rdf-schema#label> ?label . }} """.format(url = connection.vivo_url, Author_n = params['Author'].n_number)

    print('=' * 20 + "\nGenerating Author's Article List\n" + '=' * 20)
    response = connection.run_query(q)
    print(response)

    article_dump = response.json()
    all_articles = {}
    for listing in article_dump['results']['bindings']:
        a_name = listing['label']['value']
        a_url = listing['article']['value']
        a_n = a_url.rsplit('/', 1)[-1]
        all_articles[a_n] = a_name

    return all_articles