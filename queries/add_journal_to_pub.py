from article import Article
from journal import Journal
from queries import make_person

def get_params(connection):
    article = Article(connection)
    journal = Journal(connection)
    params = {'Article': article, 'Journal': journal}
    return params

def run(connection, **params):
    if not params['Journal'].n_number:
        make_publisher.run(connection, **params)
    article_url = connection.vivo_url + params['Article'].n_number
    journal_url = connection.vivo_url + params['Journal'].n_number

    q = """
        INSERT DATA {{
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
            {{
                <{ARTICLE}> <http://vivoweb.org/ontology/core#hasPublicationVenue> <{JOURNAL}> .
                <{JOURNAL}> <http://vivoweb.org/ontology/core#publicationVenueFor> <{ARTICLE}> .
            }}
        }}
    """.format(ARTICLE = article_url, JOURNAL = journal_url)

    # send data to vivo
    print('=' * 20 + "\nAssociating journal with pub\n" + '=' * 20)
    response = connection.run_update(q)
    return response