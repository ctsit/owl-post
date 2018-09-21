docstr = """
Hedwig
Usage:
    hedwig.py (-h | --help)
    hedwig.py (-q | -b) (-a | -r) <config_file>

Options:
-h --help        Show this message and exit
-q --query       Use the WOS api to get new publication data
-b --bibtex      Get new publication data from bibtex file (path in config file)
-a --api         Use VIVO update api to upload data immediately
-r --rdf         Produce rdf files with new data
"""

from docopt import docopt
import os.path
import datetime
import yaml

from vivo_queries import queries
from vivo_queries.vdos.auth_match import Auth_Match
from vivo_queries.vivo_connect import Connection
from vivo_queries.triple_handler import TripleHandler
from vivo_queries.update_log import UpdateLog

import wos
from wos_connect import WOSnnection
from wos_handler import WHandler
import daily_prophet

CONFIG_PATH = '<config_file>'
_query = '--query'
_bibtex = '--bibtex'
_api = '--api'
_rdf = '--rdf'

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except Exception as e:
        print("Error: Check config file")
        print(e)
        exit()
    return config

def make_folders(top_folder, sub_folders=None):
    if not os.path.isdir(top_folder):
        os.mkdir(top_folder)

    if sub_folders:
        sub_top_folder = os.path.join(top_folder, sub_folders[0])
        top_folder = make_folders(sub_top_folder, sub_folders[1:])

    return top_folder

def add_authors(connection, authors, tripler, ulog, disam_file):
    #get n_numbers for all authors included in batch. make authors that don't already exist.
    vivo_authors = {}
    for author in authors:
        if author not in vivo_authors.keys():
            author_n = match_input(connection, author, 'person', True, disamb_file)
            if not author_n:
                first = middle = last = ""
                try:
                    last, rest = author.split(", ")
                    try:
                        first, middle = rest.split(" ", 1)
                    except ValueError as e:
                        first = rest
                except ValueError as e:
                    last = author
                auth_params = queries.make_person.get_params(connection)
                auth_params['Author'].name = author
                auth_params['Author'].last = last
                if first:
                    auth_params['Author'].first = first
                if middle:
                    auth_params['Author'].middle = middle

                result = tripler.update(queries.make_person, **auth_params)
                author_n = auth_params['Author'].n_number
                ulog.add_to_log('authors', author, (connection.vivo_url + author_n))

            vivo_authors[author] = author_n
    return vivo_authors

def add_journals(connection, journals, tripler, ulog, disamb_file):
    #get n_numbers for all journals included in batch. make journals that don't already exist.
    vivo_journals = {}
    for issn, journal in journals.items():
        if issn not in vivo_journals.keys():
            journal_n = match_input(connection, journal, 'journal', True, disamb_file)
            if not journal_n:
                journal_n = match_input(connection, issn, 'journal', False, disamb_file)
                if not journal_n:
                    journal_params = queries.make_journal.get_params(connection)
                    journal_params['Journal'].name = journal
                    journal_params['Journal'].issn = issn

                    result = tripler.update(queries.make_journal, **journal_params)
                    #result = queries.make_journal.run(connection, **journal_params)
                    journal_n = journal_params['Journal'].n_number
                    ulog.add_to_log('journals', journal, (connection.vivo_url + journal_n))

            vivo_journals[issn] = journal_n

    return vivo_journals

def add_articles(connection, pubs, pub_journ, vivo_journals, tripler, ulog, disamb_file):
    #get n_numbers for all articles in batch. make pubs that don't already exist.
    vivo_pubs = {}

    for pub in pubs:
        pub_type = None
        query_type = None
        if pub['type'] == 'Journal Article':
            pub_type = 'academic_article'
            query_type = getattr(queries, 'make_academic_article')
        elif pub['type'] == 'Letter':
            pub_type = 'letter'
            query_type = getattr(queries, 'make_letter')
        elif pub['type'] == 'Editorial' or pub['type'] == 'Comment':
            pub_type = 'editorial'
            query_type = getattr(queries, 'make_editorial_article')
        else:
            query_type = 'pass'

        if pub['title'] not in vivo_pubs.values():
            pub_n = match_input(connection, pub['title'], pub_type, True, disamb_file)
            if not pub_n:
                pub_n = match_input(connection, pub['doi'], pub_type, False, disamb_file)
                if not pub_n:
                    wosid = pub['wosid']
                    pub_params = queries.make_academic_article.get_params(connection)
                    pub_params['Article'].name = pub['title']
                    add_valid_data(pub_params['Article'], 'volume', pub['volume'])
                    add_valid_data(pub_params['Article'], 'issue', pub['issue'])
                    add_valid_data(pub_params['Article'], 'publication_year', pub['year'])
                    add_valid_data(pub_params['Article'], 'doi', pub['doi'])
                    add_valid_data(pub_params['Article'], 'start_page', pub['start'])
                    add_valid_data(pub_params['Article'], 'end_page', pub['end'])

                    issn = pub_journ[wosid]
                    journal_n = vivo_journals[issn]
                    pub_params['Journal'].n_number = journal_n 
                    
                    if query_type=='pass':
                        ulog.track_skips(pub['type'], **pub_params)
                    else:
                        result = tripler.update(query_type, **pub_params)
                        pub_n = pub_params['Article'].n_number
                        ulog.add_to_log('articles', pub['title'], (connection.vivo_url + pub_n))
                
            vivo_pubs[pub['wosid']] = pub_n
    return vivo_pubs

def add_authors_to_pubs(connection, pub_auth, vivo_pubs, vivo_authors, tripler, ulog):
    for pub, auth_list in pub_auth.items():
        for author in auth_list:
            params = queries.add_author_to_pub.get_params(connection)
            params['Article'].n_number = vivo_pubs[pub]
            params['Author'].n_number = vivo_authors[author]

            if pub in ulog.skips.keys():
                ulog.add_author_to_skips(pub, author)
            else:
                old_author = queries.check_author_on_pub.run(connection, **params)
                if not old_author:
                    result = tripler.update(queries.add_author_to_pub, **params)
                    #result = queries.add_author_to_pub.run(connection, **params)

def add_valid_data(article, feature, value):
    if value:
        setattr(article, feature, value)

def match_input(connection, label, category, name, disamb_file):
    details = queries.find_n_for_label.get_params(connection)
    details['Thing'].extra = label
    details['Thing'].type = category
    choices = {}
    match = None

    if not name:
        if category == 'journal':
            choices = queries.find_n_for_issn.run(connection, **details)
            if len(choices) == 1:
                match = list(choices.keys())[0]

        if category == 'academic_article':
            choices = queries.find_n_for_doi.run(connection, **details)
            if len(choices) == 1:
                match = list(choices.keys())[0]

    else:
        matches = queries.find_n_for_label.run(connection, **details)
        for key, val in matches.items():
            val = val.rstrip()
            val = val.lstrip()
            if label.lower() == val.lower():
                choices[key] = val

        #perfect match
        if len(choices) == 1:
            match = list(choices.keys())[0]

        #inclusive perfect match
        if len(choices) == 0:
            for key, val in matches.items():
                if label.lower() in val.lower():
                    choices[key] = val

            if len(choices) == 1:
                match = list(choices.keys())[0]

        if len(choices) > 1:
            with open(disamb_file, "a+") as dis_file:
                #TODO: this won't contain the about-to-be-newly added uri
                dis_file.write("{} has possible uris: \n{}\n".format(label, list(choices.keys())))
    return match

def main(argv1):
    config = get_config(args[CONFIG_PATH])

    email = config.get('email')
    password = config.get ('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')
    wos_login = config.get('wos_credentials')

    connection = Connection(vivo_url, email, password, update_endpoint, query_endpoint)
    whandler = WHandler(wos_login)
    now = datetime.datetime.now()

    if args[_bibtex]:
        input_file = config.get('input_file')
        csv_data = whandler.bib2csv(input_file)
        pubs, pub_auth, authors, journals, pub_journ = whandler.parse_csv(csv_data)
    elif args[_query]:
        query = 'AD=(University Florida OR Univ Florida OR UFL OR UF)'
        end = now.strftime("%Y-%m-%d")
        then = now - datetime.timedelta(days=1)
        start = then.strftime("%Y-%m-%d")
        results = whandler.get_data(query, start, end)
        pubs, pub_auth, authors, journals, pub_journ = whandler.parse_api(results)

    timestamp = now.strftime("%Y_%m_%d")
    full_path = make_folders(log_folder, [now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")])

    disam_file = os.path.join(full_path, (timestamp + '_wos_disambiguation.txt'))
    output_file = os.path.join(full_path, (timestamp + '_wos_output_file.txt'))
    upload_file = os.path.join(full_path, (timestamp + '_wos_upload_log.txt'))
    skips_file = os.path.join(full_path, (timestamp + '_wos_skips_.txt'))
    
    tripler = TripleHandler(args[_api], connection, output_file)
    ulog = UpdateLog()

    try:
        vivo_authors = add_authors(connection, authors, tripler, ulog, disam_file)
        vivo_journals = add_journals(connection, journals, tripler, ulog, disam_file)
        vivo_articles = add_articles(connection, pubs, pub_journ, vivo_journals, tripler, ulog, disam_file)
        add_authors_to_pubs(connection, pub_auth, vivo_articles, vivo_authors, tripler, ulog)
    except Exception as e:
        print('Error')
        raise(e)
        with open(output_file, 'a+') as log:
            log.write("Error\n")
            log.write(str(e))

    are_uploads = ulog.create_file(upload_file)
    ulog.write_skips(skips_file)

    if args[_rdf]:
        rdf_file = timestamp + '_upload.rdf'
        rdf_filepath = os.path.join(uploads, rdf_file)
        tripler.print_rdf(rdf_filepath)

    # if are_uploads and args[_api]:
    #     emailnnection = daily_prophet.connect_to_smtp(config.get('host'), config.get('port'))
    #     msg = daily_prophet.create_email(full_summary['Articles'], config, upload_file)
    #     daily_prophet.send_message(msg, emailnnection, config)

if __name__ == '__main__':
    args = docopt(docstr)
    main(args)