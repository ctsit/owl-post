from jinja2 import Environment

from journal import Journal
from publisher import Publisher

def get_params(connection):
    journal = Journal(connection)
    publisher = Publisher(connection)
    params = {'Journal': journal, 'Publisher': publisher}
    return params

def run(connection, **params):
    journal = params.get('Journal')
    params['upload_url'] = connection.vivo_url

    journal.create_n()
    if params['Publisher'].name:
        params['Publisher'].create_n()
        journal.final_check(params['Publisher'].n_number) 

    #template data into q
    q = Environment().from_string("""\
    INSERT DATA {
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
        {
            <{{upload_url}}{{Journal.n_number}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/Journal> .
            <{{upload_url}}{{Journal.n_number}}> <http://www.w3.org/2000/01/rdf-schema#label> "{{Journal.name}}" .

            {%- if Publisher.name %}
             <{{upload_url}}{{Publisher.n_number}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Thing> .
             <{{upload_url}}{{Publisher.n_number}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Publisher> .
             <{{upload_url}}{{Publisher.n_number}}> <http://www.w3.org/2000/01/rdf-schema#label> "{{Publisher.name}}" .
            {%- endif -%}

            {%- if Publisher.n_number %}
             <{{upload_url}}{{Publisher.n_number}}> <http://vivoweb.org/ontology/core#publisherOf> <{{upload_url}}{{Journal.n_number}}> .
             <{{upload_url}}{{Journal.n_number}}> <http://vivoweb.org/ontology/core#publisher> <{{upload_url}}{{Publisher.n_number}}> .
            {%- endif -%}         
        }
    }
    """)

    #send data to vivo
    print('=' * 20 + "\nCreating new journal\n" + '=' * 20)
    response = connection.run_update(q.render(**params))
    return response