from jinja2 import Environment

from author import Author

def get_params(connection):
    author = Author(connection)
    params = {'Author': author}
    return params

def run(connection, **params):
    params['Author'].create_n()
    
    params['upload_url'] = connection.vivo_url

    params['vcard'] = connection.gen_n()
    while (params['vcard'] == params['Author'].n_number):
        params['vcard'] = connection.gen_n()

    if params['Author'].name:
        params['name_id'] = connection.gen_n()
        while (params['name_id'] in {params['Author'].n_number, params['vcard']}):
            params['name_id'] = connection.gen_n()

    if params['Author'].email:
        params['email_id'] = connection.gen_n()
        while (params['email_id'] in {params['Author'].n_number, params['vcard'], params['name_id']}):
            params['email_id'] = connection.gen_n()

    if params['Author'].phone:
        params['phone_id'] = connection.gen_n()
        while (params['phone_id'] in {params['Author'].n_number, params['vcard'], params['name_id'], params['email_id']}):
            params['phone_id'] = connection.gen_n()

    if params['Author'].title:
        params['title_id'] = connection.gen_n()
        while (params['title_id'] in {params['Author'].n_number, params['vcard'], params['name_id'], params['email_id'], params['phone_id']}):
            params['title_id'] = connection.gen_n()

    q = Environment().from_string("""\
        INSERT DATA {
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
            {
                <{{upload_url}}{{Author.n_number}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
                <{{upload_url}}{{Author.n_number}}> <http://www.w3.org/2000/01/rdf-schema#label> "{{Author.name}}" .
                <{{upload_url}}{{Author.n_number}}> <http://purl.obolibrary.org/obo/ARG_2000028> <{{upload_url}}{{vcard}}> .
                <{{upload_url}}{{vcard}}> <http://purl.obolibrary.org/obo/ARG_2000029> <{{upload_url}}{{Author.n_number}}> .
                <{{upload_url}}{{vcard}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2006/vcard/ns#Individual> .
                
              {%- if Author.name %}
                <{{upload_url}}{{vcard}}> <http://www.w3.org/2006/vcard/ns#hasName> <{{upload_url}}{{name_id}}> .
                <{{upload_url}}{{name_id}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2006/vcard/ns#Name> .
              {%- endif -%}

              {%- if Author.first %}
                <{{upload_url}}{{name_id}}> <http://www.w3.org/2006/vcard/ns#givenName> "{{Author.first}}" .
              {%- endif -%}

              {%- if Author.middle %}
                <{{upload_url}}{{name_id}}> <http://vivoweb.org/ontology/core#middleName> "{{Author.middle}}" .
              {%- endif -%}

              {%- if Author.last %}
                <{{upload_url}}{{name_id}}> <http://www.w3.org/2006/vcard/ns#familyName> "{{Author.last}}" .
              {%- endif -%}

              {%- if Author.email %}
                <{{upload_url}}{{vcard}}> <http://www.w3.org/2006/vcard/ns#hasEmail> <{{upload_url}}{{email_id}}> .
                <{{upload_url}}{{email_id}}> <http://www.w3.org/2006/vcard/ns#email> "{{Author.email}}" .
                <{{upload_url}}{{email_id}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2006/vcard/ns#Email> .
                <{{upload_url}}{{email_id}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2006/vcard/ns#Work> .
              {%- endif -%}

              {%- if Author.phone %}
                <{{upload_url}}{{vcard}}> <http://www.w3.org/2006/vcard/ns#hasTelephone> <{{upload_url}}{{phone_id}}> .
                <{{upload_url}}{{phone_id}}> <http://www.w3.org/2006/vcard/ns#telephone> "{{Author.phone}}" .
                <{{upload_url}}{{phone_id}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2006/vcard/ns#Telephone> .
              {%- endif -%}

              {%- if Author.title %}
                <{{upload_url}}{{vcard}}> <http://www.w3.org/2006/vcard/ns#hasTitle> <{{upload_url}}{{title_id}}> .
                <{{upload_url}}{{title_id}}> <http://www.w3.org/2006/vcard/ns#title> "{{Author.title}}" .
                <{{upload_url}}{{title_id}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2006/vcard/ns#Title> .
              {%- endif %}
            }
        }
        """)

    print('=' * 20 + "\nCreating new person\n" + '=' * 20)
    response = connection.run_update(q.render(**params))
    return response