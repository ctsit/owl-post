from author import Author

def get_params(connection):
    author = Author(connection)
    params = {'Author': author,}
    return params

def run(connection, **params):
    subj = connection.vivo_url + params['Author'].n_number

    q = """ SELECT ?vcard WHERE {{<{}> <http://purl.obolibrary.org/obo/ARG_2000028> ?vcard .}} LIMIT 1 """.format(subj)

    print('=' * 20 + '\nFinding vcard\n' + '=' * 20)
    response = connection.run_query(q)
    print(response)

    #Navigate json
    finding = response.json()
    vcard = finding['results']['bindings'][0]['vcard']['value']

    return vcard