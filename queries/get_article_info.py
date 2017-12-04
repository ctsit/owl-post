from article import Article

def get_params(connection):
    article = Article(connection)
    params = {'Article': article}
    return params

def run(connection, **params):
    subj = connection.vivo_url + params['Article'].n_number

    q = """ SELECT ?title ?volume ?issue ?start ?finish ?year ?doi ?pmid ?journal ?journal_name ?author
            WHERE {{
                OPTIONAL {{ <{subj}> <http://www.w3.org/2000/01/rdf-schema#label> ?title . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/volume> ?volume . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/issue> ?issue . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/pageStart> ?start . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/pageEnd> ?finish . }}
                OPTIONAL {{ <{subj}> <http://vivoweb.org/ontology/core#dateTimeValue> ?duri . ?duri <http://vivoweb.org/ontology/core#dateTime> ?year . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/doi> ?doi . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/pmid> ?pmid . }}
                OPTIONAL {{ <{subj}>  <http://vivoweb.org/ontology/core#hasPublicationVenue> ?journal . ?journal <http://www.w3.org/2000/01/rdf-schema#label> ?journal_name .}}
            }}""".format(subj = subj)
    response = connection.run_query(q)
    print(response)
    finding = response.json()
    print(finding)

    title = finding['results']['bindings'][0]['title']['value']
    volume = finding['results']['bindings'][0]['volume']['value']
    issue = finding['results']['bindings'][0]['issue']['value']
    start = finding['results']['bindings'][0]['start']['value']
    finish = finding['results']['bindings'][0]['finish']['value']
    year = finding['results']['bindings'][0]['year']['value']
    doi = finding['results']['bindings'][0]['doi']['value']
    pmid = finding['results']['bindings'][0]['pmid']['value']
    journal_id = finding['results']['bindings'][0]['journal']['value']
    journal_name = finding['results']['bindings'][0]['journal_name']['value']

    info = {'title': title, 'volume': volume, 'issue': issue, 'start page': start, 'end page': finish, 'year': year, 'doi': doi, 'pmid': pmid, 'journal': journal_name, 'journal_n': journal_id}
    return info

