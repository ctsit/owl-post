from bibtexparser import loads
import os.path
import sys
import time
import yaml

from auth_match import Auth_Match
from owlery import Connection
import queries
import wos
from spiderowl import WOSnnection

ARTICLE_COUNT = 0
JOURNAL_COUNT = 0
PUBLISHER_COUNT = 0
AUTHOR_COUNT = 0

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except Exception, e:
        print("Error: Check config file")
        print(e)
        exit()
    return config

def bib2csv(bib_data):
    csv_data = {}
    row = 0
    col_names = set(y for x in bib_data.entries for y in x.keys())

    for x in bib_data.entries:
        row += 1
        csv_data[row] = {}

        for col_name in col_names:
            v = x.get(col_name, '')
            v = v.replace('\n', ' ')
            v = v.replace('\r', ' ')
            v = v.replace('\t', ' ')
            csv_data[row][col_name] = v.encode('utf-8').strip()
    return csv_data

def process(connection, data):
    global ARTICLE_COUNT
    params = queries.make_academic_article.get_params(connection)
    article = params['Article']
    journal = params['Journal']
    #TODO: make sure 'type' is Article

    #Fill out journal info and create journal if it does not exist
    try:
        #TODO (maybe): check if existing journal has publisher
        journal_name = data['journal']
        clean_jname = check_filter(journal_name.title(), 'journal')
        journal_n = match_input(connection, clean_jname, 'journal')

        if not journal_n:
            try:
                publisher_name = data['publisher']
            except KeyError as e:
                publisher_name = None
            journal_n = create_journal(connection, clean_jname, publisher_name)

        journal.n_number = journal_n
    except KeyError as e:
        journal.n_number = None

    title = data['title']
    article_n = match_input(connection, title, 'academic_article')

    if article_n:
        #article with same name already exists
        article.n_number = article_n
        if journal_name:
            pubs_journal = queries.get_journal_on_pub.run(connection, **params)
            try:
                pubs_j_n, pubs_j_name = pubs_journal
            except Exception, e:
                pass
            if not pubs_journal:
                #if article has no journal, add journal
                queries.add_journal_to_pub.run(connection, **params)
            if pubs_journal:
                #if journal on article does not match, create new article with this journal.
                if pubs_j_n != journal.n_number:
                    article_n = None
                    article.n_number = None

        add_authors(connection, article, data)
        return

    if not article_n:
        article.name = title
        #get article info for non-existant articles
        try:
            doi = data['doi']
            #match_input(connection, doi, 'doi')
            article.doi = doi
        except KeyError as e:
            pass

        try:
            keyword = data['keyword']
        except KeyError as e:
            pass

        try:
            pages = data['pages']
            try:
                start, end = pages.split('-')
            except ValueError as e:
                start = pages
                end = None
            article.start_page = start
            article.end_page = end
        except KeyError as e:
            pass

        try:
            volume = data['volume']
            article.volume = volume
        except KeyError as e:
            pass

        try:
            year = data['year']
            article.publication_year = year
        except KeyError as e:
            pass

        response = queries.make_academic_article.run(connection, **params)
        print(response)
        if response:
            ARTICLE_COUNT += 1     
        
    add_authors(connection, article, data)

def match_input(connection, label, obj_type):
    #TODO: special match function for doi
    deets = queries.find_n_for_label.get_params(connection)
    deets['Thing'].name = label
    deets['Thing'].category = obj_type

    current_list = queries.find_n_for_label.run(connection, **deets)
    choices = {}
    for key, val in current_list.items():
        if label.lower() == val.lower():
            choices[key] = val

    if len(choices) == 1:
        for key in choices:
            return key
    else:
        #TODO: deal with duplicates
        return None

def check_filter(label, category):
    cleanfig_path = os.path.join("filters", "extras.yaml")
    with open(cleanfig_path, 'r') as config_file:
        cleanfig = yaml.load(config_file.read())
    #primary cleaning
    abbrev_table = cleanfig.get('abbrev_table')
    label += " " #add trailing space in case abbreviation is end of string
    label = label.replace("  ", " ")
    label = label.replace("\\", "") #can not have escape character when using update api
    for abbrev in abbrev_table:
        label = label.replace(abbrev, abbrev_table[abbrev])
    if label[-1] == " ":
        label = label[:-1] #remove final space

    #match against filter
    filter_file = category + "_filter.txt"
    filter_path = os.path.join("filters", filter_file)
    pairs = {}
    with open(filter_path) as fil:
        content = fil.readlines()
        for line in content:
            key, val = line.split("|")
            pairs[key] = val

        for key, val in pairs.items():
            if label == key:
                label = val
                break
    
    #return clean_label
    return label

def create_journal(connection, journal_name, publisher_name):
    global PUBLISHER_COUNT
    global JOURNAL_COUNT
    clean_pname = check_filter(publisher_name.title(), 'publisher')
    publisher_n = match_input(connection, clean_pname, 'publisher')

    reqs = queries.make_journal.get_params(connection)
    reqs['Journal'].name = journal_name
    if publisher_n:
        reqs['Publisher'].n_number = publisher_n
    else:
        reqs['Publisher'].name = clean_pname
        PUBLISHER_COUNT += 1

    response = queries.make_journal.run(connection, **reqs)
    print(response)
    if response:
        JOURNAL_COUNT += 1
        return reqs['Journal'].n_number
    else:
        return None

def add_authors(connection, article, data):
    global AUTHOR_COUNT
    author_str = data['author']
    authors = author_str.split(" and ")
    for person in authors:
        args = queries.add_author_to_pub.get_params(connection)
        author_n = match_authors(connection, person, data)
        args['Author'].n_number = author_n
        args['Article'].n_number = article.n_number
        args['Author'].name = person

        old_author = False
        if author_n:
            old_author = queries.check_author_on_pub.run(connection, **args)
        if not old_author:
            response = queries.add_author_to_pub.run(connection, **args)
            print(response)
            if response:
                AUTHOR_COUNT += 1 

def match_authors(connection, label, data):
    deets = queries.find_n_for_label.get_params(connection)
    deets['Thing'].name = label
    deets['Thing'].category = 'person'

    current_list = queries.find_n_for_label.run(connection, **deets)
    print(current_list)
    choices = {}
    #perfect match
    for key, val in current_list.items():
        #Manually added names may end with a blank space
        if val.endswith(" "):
            val = val[:-1]
        if label.lower() == val.lower():
            choices[key] = val
            
    print(str(len(choices)) + " matches")
    if len(choices) == 1:
        for key in choices:
            return key

    #match contains label
    if len(choices) == 0:
        for key, val in current_list.items():
            if label.lower() in val.lower():
                choices[key] = val

        if len(choices) == 1:
            for key in choices:
                return key

    #check against wos
    if len(choices) > 1:
        #add to disambiguation file
        #TODO: create filter for uris of authors with same name
        author_uris = []
        for uri, name in choices.items():
            author_uris.append(connection.check_url + uri)

        with open("data_out/disambiguation_"+ time.strftime("%Y_%m_%d") +".txt", "a+") as disamb_file:
            disamb_file.write("{} has possible uris: \n{}\n".format(label, author_uris))

        try:
            category_str = data['web-of-science-categories']
            category_str = category_str.replace("\&", "")
            categories = category_str.split(", ")
        except KeyError as e:
            categories = None

        matches = []
        index = 0
        for choice_n, choice_name in choices.items():
            scoop = queries.get_articles_for_author.get_params(connection)
            scoop['Author'].n_number = choice_n
            pub_list = queries.get_articles_for_author.run(connection, **scoop)

            matches.append(Auth_Match())
            matches[index].n_number = choice_n
            matches[index].name = choice_name
            matches[index].pubs = pub_list

            index += 1

        wos_config = get_config('wos/wos_config.yaml')
        wosnnection = WOSnnection(wos_config)
        wos_pubs = wos.get_pubs.run(wosnnection, label, categories)

        best_match = None
        for match in matches:
            for title in wos_pubs:
                match.compare_pubs(title)
            if match.points > 0:
                if best_match:
                    if match.point > best_match.points:
                        best_match = match
                else:
                    best_match = match
        if best_match:
            print("Match found.")
            return best_match.n_number
        else:
            return None

def main(argv1):
    config_path = argv1
    config = get_config(config_path)

    email = config.get('email')
    password = config.get ('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')
    check_url = config.get('checking_url')
    input_file = config.get('input_file')

    connection = Connection(vivo_url, check_url, email, password, update_endpoint, query_endpoint)

    bib_str = ""
    with open (input_file, 'r') as bib:
        for line in bib:
            bib_str += line

    bib_data = loads(bib_str)
    csv_data = bib2csv(bib_data)

    for entry in csv_data.items():
        number, data = entry
        process(connection, data)

    print("Summary of new items:  >Articles: ", ARTICLE_COUNT, "  >Journals: ", JOURNAL_COUNT, "  >Publishers: ", PUBLISHER_COUNT, "  >People: ", AUTHOR_COUNT)
if __name__ == '__main__':
    main(sys.argv[1])