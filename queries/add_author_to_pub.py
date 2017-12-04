from article import Article
from author import Author
from queries import make_person

def get_params(connection):
    article = Article(connection)
    author = Author(connection)
    params = {'Article': article, 'Author': author}
    return params

def run(connection, **params):
    if not params['Author'].n_number:
        make_person.run(connection, **params)
    relationship_id = connection.gen_n()
    relation_url = connection.vivo_url + relationship_id
    article_url = connection.vivo_url + params['Article'].n_number
    author_url = connection.vivo_url + params['Author'].n_number

    q = """
        INSERT DATA {{
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
            {{
                <{RELATION}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Authorship> .
                <{RELATION}> <http://vivoweb.org/ontology/core#relates> <{ARTICLE}> .
                <{RELATION}> <http://vivoweb.org/ontology/core#relates> <{AUTHOR}> .
                <{ARTICLE}> <http://vivoweb.org/ontology/core#relatedBy> <{RELATION}> .
            }}
        }}
    """.format(RELATION = relation_url, ARTICLE = article_url, AUTHOR = author_url)

    # send data to vivo
    print('=' * 20 + "\nAssociating author with pub\n" + '=' * 20)
    response = connection.run_update(q)
    return response