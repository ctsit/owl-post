from article import Article
from journal import Journal

def get_params(connection):
    article = Article(connection)
    journal = Journal(connection)
    params = {'Article': article, 'Journal': journal}
    return params

def run(connection, **params):
    journal_url = connection.vivo_url + params['Journal'].n_number
    article_url = connection.vivo_url + params['Article'].n_number

    q = """SELECT ?j ?label WHERE{{?j <http://vivoweb.org/ontology/core#publicationVenueFor> <{}> . <{}> <http://vivoweb.org/ontology/core#hasPublicationVenue> ?j . ?j <http://www.w3.org/2000/01/rdf-schema#label> ?label . }}""".format(article_url, article_url)
    
    print('=' * 20 + "\nChecking for journal\n" + '=' * 20)
    response = connection.run_query(q)

    j_check = response.json()
    for listing in j_check['results']['bindings']:
        try:
            j_name = listing['label']['value']
            j_url = listing['j']['value']
            j_n = j_url.rsplit('/', 1)[-1]
            pubs_journal = (j_n, j_name)
            return pubs_journal 
        except KeyError as e:
            return None

    