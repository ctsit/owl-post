from queries import get_label
from thing import Thing
from queries import get_all_triples

def get_params(connection):
    thing = Thing(connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    triples = get_all_triples.run(connection, **params)
    label = get_label.run(connection, **params)

    format_triples = ""
    for trip in triples:
        format_triples = format_triples + trip + " . \n"

    #Fix label
    format_triples = format_triples.encode('utf-8')
    format_triples = str.replace(format_triples, "<" + label + ">", "\"" + label + "\"")

    q = """
    DELETE DATA {{
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2> {{
            {}
        }}
    }}
    """.format(format_triples)

    print('=' * 20 + "\nDeleting\n" + '=' * 20)
    response = connection.run_update(q)
    return response