from queries import get_label
from thing import Thing
from queries import delete_entity
from queries import get_all_triples

def get_params(connection):
    thing1 = Thing(connection)
    thing2 = Thing(connection)
    params = {'Primary URI': thing1, 'Secondary URI': thing2}
    return params

def run(connection, **params):
    merge_params = {'Thing': params['Secondary URI']}
    final_uri = params['Primary URI'].n_number
    old_uri = params['Secondary URI'].n_number

    triples = get_all_triples.run(connection, **merge_params)
    label = get_label.run(connection, **merge_params)

    format_triples = ""
    for trip in triples:
        format_triples = format_triples + trip + " . \n"
    
    #Get new triples
    format_triples = format_triples.encode('utf-8')
    format_triples = str.replace(format_triples, old_uri + ">", final_uri + ">")
    format_triples = str.replace(format_triples, "<" + label + ">", "\"" + label + "\"")

    #Insert new triples
    q = """
    INSERT DATA {{
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2> {{
            {}
        }}
    }}
    """.format(format_triples)

    print('=' * 20 + "\nMerging\n" + '=' * 20)
    ins_response = connection.run_update(q)
    print(ins_response)

    #Delete if Insert is successful
    if ins_response == 200:
        del_response = delete_entity.run(connection, **merge_params)
        return del_response
    else:
        return ins_response