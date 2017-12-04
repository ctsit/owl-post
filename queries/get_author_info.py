from author import Author
from queries import get_vcard

def get_params(connection):
    author = Author(connection)
    params = {'Author': author}
    return params

def run(connection, **params):
    subj = connection.vivo_url + params['Author'].n_number
    vcard = get_vcard.run(connection, **params)
    #response = {'phone': , 'email': , 'title': }

    q = """ SELECT ?fullname ?given ?middle ?last ?phone ?email ?title ?overview ?geofocus
            WHERE {{
                OPTIONAL {{ <{subj}> <http://www.w3.org/2000/01/rdf-schema#label> ?fullname . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#givenName> ?given . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#middleName> ?middle . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#lastName> ?last . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#hasTelephone> ?puri . ?puri <http://www.w3.org/2006/vcard/ns#telephone> ?phone . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#hasEmail> ?euri . ?euri <http://www.w3.org/2006/vcard/ns#email> ?email . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#hasTitle> ?turi . ?turi <http://www.w3.org/2006/vcard/ns#title> ?title . }}
                OPTIONAL {{ <{subj}> <http://vivoweb.org/ontology/core#overview> ?overview . }}
                OPTIONAL {{ <{subj}> <http://vivoweb.org/ontology/core#geographicFocus> ?geofocus . }}                
            }}""".format(subj = subj, vcard = vcard)
    response = connection.run_query(q)
    print(response)
    finding = response.json()
    print(finding)

    #TODO: should all be try/except
    full_name = finding['results']['bindings'][0]['fullname']['value']
    given_name = finding['results']['bindings'][0]['given']['value']
    middle_name = finding['results']['bindings'][0]['middle']['value']
    last_name = finding['results']['bindings'][0]['last']['value']
    phone = finding['results']['bindings'][0]['phone']['value']
    email = finding['results']['bindings'][0]['email']['value']
    title = finding['results']['bindings'][0]['title']['value']
    overview = finding['results']['bindings'][0]['overview']['value']
    geofocus = finding['results']['bindings'][0]['geofocus']['value']

    info = {'full name': full_name, 'given name': given_name, 'middle name': middle_name, 'last name': last_name, 'phone': phone, 'email': email, 'title': title, 'overview': overview, 'geographic focus': geofocus}
    return info