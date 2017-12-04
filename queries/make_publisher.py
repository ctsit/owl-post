from publisher import Publisher

def get_params(connection):
    publisher = Publisher(connection)
    params = {'Publisher': publisher}
    return params

def run(connection, **params):
    publisher.create_n()
    publisher_url = connection.vivo_url + params['Publisher'].n_number

    #template data into q
    q = """
    INSERT DATA {{
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
        {{
            <{PUBLISHER}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Thing> .
            <{PUBLISHER}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Publisher> .
            <{PUBLISHER}> <http://www.w3.org/2000/01/rdf-schema#label> "{NAME}" .      
        }}
    }}
    """.format(PUBLISHER = publisher_url, NAME = params['Publisher'].name)

    #send data to vivo
    print('=' * 20 + "\nCreating new publisher\n" + '=' * 20)
    response = connection.run_update(q)
    return response