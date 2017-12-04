from article import Article
from author import Author

def get_params(connection):
    article = Article(connection)
    author = Author(connection)
    params = {'Article': article, 'Author': author}
    return params

def run(connection, **params):
    author_url = connection.vivo_url + params['Author'].n_number
    article_url = connection.vivo_url + params['Article'].n_number

    q = """SELECT ?relation WHERE{{ ?relation <http://vivoweb.org/ontology/core#relates> <{}> . ?relation <http://vivoweb.org/ontology/core#relates> <{}> . }}""".format(author_url, article_url)
    
    print('=' * 20 + "\nChecking for author\n" + '=' * 20)
    response = connection.run_query(q)

    n_check = response.json()
    try: 
        if n_check['results']['bindings'][0]['relation']:
            return True
    except IndexError as e:
        if e.message != "list index out of range":
            raise
        else:
            return False
