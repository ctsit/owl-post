import mysql.connector
from time import localtime, strftime

from pubmed_connect import PUBnnection
from vivo_queries.name_cleaner import clean_name

class Citation(object):
    def __init__(self, data):
        self.data = data

    def check_key(self, paths, data=None):
        if not data:
            data = self.data
        if paths[0] in data:
            trail = data[paths[0]]
            if len(paths) > 1:
                trail = self.check_key(paths[1:], trail)
            return trail
        else:
            return ""

class PHandler(object):
    def __init__(self, email):
        self.pubnnection = PUBnnection(email)

    def get_data(self, query, log_file=None):
        id_list = self.pubnnection.get_id_list(query)
        if log_file:
            with open(log_file, 'a+') as log:
                log.write("\n" + '=' * 10 + "Articles found: " + str(len(id_list)) + '\n')
        results = self.pubnnection.get_details(id_list)
        return results

    def parse_api(self, pm_dump):
        pubs = []
        pub_auth = {}
        authors = []
        journals = {}
        pub_journ = {}

        for citing in pm_dump['PubmedArticle']:
            citation = Citation(citing['MedlineCitation'])
            pub_title = clean_name(citation.check_key(['Article', 'ArticleTitle']))
            try:
                count = 0
                proto_doi = citation.check_key(['Article', 'ELocationID'])[count]
                while proto_doi.attributes['EIdType'] != 'doi':
                    count += 1
                    proto_doi = citation.check_key(['Article', 'ELocationID'])[count]
                doi = str(proto_doi)
            except IndexError as e:
                doi = ""
            year = str(citation.check_key(['Article', 'Journal', 'JournalIssue', 'PubDate', 'Year']))
            volume = str(citation.check_key(['Article', 'Journal', 'JournalIssue', 'Volume']))
            issue = str(citation.check_key(['Article', 'Journal', 'JournalIssue', 'Issue']))
            pages = str(citation.check_key(['Article', 'Pagination', 'MedlinePgn']))
            try:
                start, end = pages.split('-')
            except ValueError as e:
                start = pages
                end = ''
            try:
                pub_type = str(citation.check_key(['Article', 'PublicationTypeList'])[0])
            except IndexError as e:
                pub_type = ""
            pmid = str(citation.check_key(['PMID']))
            issn = str(citation.check_key(['Article', 'Journal', 'ISSN']))
            journ_name = clean_name(citation.check_key(['Article', 'Journal', 'Title']))

            author_dump = citation.check_key(['Article', 'AuthorList'])
            for person in author_dump:
                author = Citation(person)
                lname = clean_name(author.check_key(['LastName']))
                fname = clean_name(author.check_key(['ForeName']))
                if lname or fname:
                    name = lname + ', ' + fname

                    if name not in authors:
                        authors.append(name)

                    if pmid not in pub_auth.keys():
                        pub_auth[pmid] = [name]
                    else:
                        #pubmed does not have an id for authors
                        pub_auth[pmid].append(name)

            pubs.append({'doi': doi, 'title': pub_title, 'year': year,
                        'volume': volume, 'issue': issue, 'start': start,
                        'end': end, 'type': pub_type, 'pmid': pmid})
            if issn not in journals.keys():
                journals[issn] = journ_name
            pub_journ[pmid] = issn

        return (pubs, pub_auth, authors, journals, pub_journ)

    def prepare_tables(self, c):
        print("Making tables")
        c.execute('''create table if not exists pubmed_pubs
                        (doi text, title text, year text, volume text, issue text, pages text, type text, pmid varchar(15) unique, created_dt text not null, modified_dt text not null, written_by text not null)''')

        c.execute('''create table if not exists pubmed_authors
                        (author varchar(40) unique)''')

        c.execute('''create table if not exists pubmed_journals
                        (issn varchar(30) unique, title text, created_dt text not null, modified_dt text not null, written_by text not null)''')

        c.execute('''create table if not exists pubmed_pub_auth
                        (pmid varchar(15), auth varchar(40), unique (pmid, auth))''')

        c.execute('''create table if not exists pubmed_pub_journ
                        (pmid varchar(15), issn varchar(30), unique (pmid, issn))''')

    def local_add_pubs(self, c, pubs, source):
        print("Adding publications")
        timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for pub in pubs:
            pmid = pub[7]
            c.execute('SELECT * FROM pubmed_pubs WHERE pmid=%s', (pmid,))
            rows = c.fetchall()

            if len(rows)==0:
                dataset = (pub + (timestamp, timestamp, source))
		        #import pdb
                #pdb.set_trace()
                c.execute('INSERT INTO pubmed_pubs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', dataset)
            else:
                for row in rows:
                    if row[0:8] != pub:
                        with open('log.txt', 'a+') as log:
                            log.write(timestamp + ' -- ' + 'pubmed_pubs' + '\n' + str(row) + '\n')
                        sql = '''UPDATE pubmed_pubs
                                    SET doi = %s ,
                                        title = %s ,
                                        year = %s ,
                                        volume = %s ,
                                        issue = %s ,
                                        pages = %s ,
                                        type = %s ,
                                        modified_dt = %s ,
                                        written_by = %s
                                    WHERE pmid = %s'''
                        c.execute(sql, (pub[0:7] + (timestamp, source, pub[7])))

    def local_add_authors(self, c, authors):
        print("Adding authors")
        for auth in authors:
            try:
                c.execute('INSERT INTO pubmed_authors VALUES(%s)', (auth,))
            except mysql.connector.errors.IntegrityError as e:
                pass

    def local_add_journals(self, c, journals, source):
        print("Adding journals")
        timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for issn, title in journals.items():
            c.execute('SELECT * FROM pubmed_journals WHERE issn=%s', (issn,))
            rows = c.fetchall()

            if len(rows)==0:
                c.execute('INSERT INTO pubmed_journals VALUES (%s, %s, %s, %s, %s)', (issn, title, timestamp, timestamp, source))
            else:
                for row in rows:
                    if row[0:2] != (issn, title):
                        with open('log.txt', 'a+') as log:
                            log.write(timestamp + ' -- ' + 'pubmed_journals' + '\n' + str(row) + '\n')
                        sql = '''UPDATE wos_journals
                                SET title = %s ,
                                    modified_dt = %s ,
                                    written_by = %s
                                WHERE issn = %s'''
                        c.execute(sql, (title, timestamp, source, issn))

    def local_add_pub_auth(self, c, pub_auth):
        print("Adding publication-author linkages")
        for pmid, auth_list in pub_auth.items():
            for auth in auth_list:
                try:
                    c.execute('INSERT INTO pubmed_pub_auth VALUES(%s, %s)', (pmid, auth))
                except mysql.connector.errors.IntegrityError as e:
                    pass

    def local_add_pub_journ(self, c, pub_journ):
        print("Adding publication-journal linkages")
        for pmid, issn in pub_journ.items():
            try:
                c.execute('INSERT INTO pubmed_pub_journ VALUES(%s, %s)', (pmid, issn))
            except mysql.connector.errors.IntegrityError as e:
                pass
