from article import Article
from author import Author
from queries import make_person

def get_params(connection):
    article = Article(connection)
    author = Author(connection)
    params = {'Article': article, 'Author': author}
    return params

def run(connection, **params):
    if not params['Publisher'].n_number:
        make_publisher.run(connection, **params)
    publisher_url = connection.vivo_url + params['Publisher'].n_number
    journal_url = connection.vivo_url + params['Journal'].n_number

    q = """
        INSERT DATA {{
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
            {{
                <{PUBLISHER}> <http://vivoweb.org/ontology/core#publisherOf> <{JOURNAL}> .
                <{JOURNAL}> <http://vivoweb.org/ontology/core#publisher> <{PUBLISHER}> .
            }}
        }}
    """.format(PUBLISHER = publisher_url, JOURNAL = journal_url)

    # send data to vivo
    print('=' * 20 + "\nAssociating author with pub\n" + '=' * 20)
    response = connection.run_update(q)
    return response