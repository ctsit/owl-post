import pprint
import sys
import yaml

from vivo_queries import catalog
from vivo_queries.vivo_connect import Connection
from vivo_queries.vdos.author import Author
from vivo_queries import queries


def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config


def prepare_query(connection):
    template_choice = get_template_type('queries')

    # head, sep, tail = template_type.partition('.')
    # template_choice = head
    print(template_choice)

    template_mod = getattr(queries, template_choice)
    params = template_mod.get_params(connection)

    for key, val in params.items():
        fill_details(connection, key, val, template_choice)

    response = template_mod.run(connection, **params)
    pprint.pprint(response)


def get_template_type(folder):
    available_queries = catalog.list_queries()
    template_options = {}

    for c, query in enumerate(available_queries, 1):
        template_options[c] = query

    for key, val in template_options.items():
        print(str(key) + ': ' + val + '\n')

    index = int(input("Enter number of query: "))
    return template_options.get(index)


def fill_details(connection, key, item, task):
    """
    Given an item, calls get_details and iterates through the list, prompting the user for the literal values.
    """
    print('*' * 20 + '\n' * 2 + "Working on " + key + '\n' * 2 + '*' * 20)
    try:
        sub_task = "make_" + item.type
    except TypeError as e:
        sub_task = None   # Anything using a Thing will have a blank type

    sub_key = ''

    # For Grant
    if sub_task != task and task == 'make_grant':
        if key in ['AwardingDepartment', 'SubContractedThrough', 'AdministeredBy']:
            sub_task = 'make_organization'
            sub_key = 'Organization'
        elif key == 'SupportedWork':
            sub_task = 'make_academic_article'
            sub_key = 'Article'
        elif key == 'Contributor_PI' or key == 'Contributor_CoPI':
            sub_task = 'make_contributor'
            sub_key = 'Contributor'

    print("Fill in the values for the following (if you do not have a value, leave blank):")
    # Check if user knows n number
    obj_n = input("N number: ")
    if obj_n:
        item.n_number = obj_n
        # TODO: add label check
    else:
        # For non-Thing objects, ask for further detail
        if key != 'Thing':
            obj_name=''
            # Ask for label
            if key == 'Author':
                first_name = input("First name: ")
                if first_name:
                    item.first = first_name

                middle_name = input("Middle name: ")
                if middle_name:
                    item.middle = middle_name

                last_name = input("Last name: ")
                if last_name:
                    item.last = last_name

                if last_name:
                    obj_name = last_name
                    if first_name:
                        obj_name = obj_name + ", " + first_name
                        if middle_name:
                            obj_name = obj_name + " " + middle_name
                    elif middle_name:
                        obj_name = obj_name + ", " + middle_name
                elif first_name:
                    if middle_name:
                        obj_name = first_name + " " + middle_name
                    else:
                        obj_name = first_name
                elif middle_name:
                    obj_name = middle_name

            else:
                obj_name = input(key + " name/title: ")

            if obj_name:
                item.name = scrub(obj_name)

                # Contributor for Grants
                if item.type == 'contributor' and key == 'Contributor_PI':
                    item.type = 'contributor_pi'
                elif item.type == 'contributor' and key == 'Contributor_CoPI':
                    item.type = 'contributor_copi'

                # Check if label already exists
                match = match_input(connection, item.name, item.type, True)
                if not match:
                    if sub_task != task:
                        # If this entity is not the original query, make entity
                        create_obj = input("This " + item.type + " is not in the database. Would you like to add it? (y/n) ")
                        if create_obj == 'y' or create_obj == 'Y':
                            try:
                                details = item.get_details()
                                for feature in details:
                                    item_info = input(str(feature) + ": ")
                                    setattr(item, feature, item_info)

                                update_path = getattr(queries, sub_task)
                                sub_params = update_path.get_params(connection)
                                if sub_key == '':
                                    sub_params[key] = item
                                else:
                                    sub_params[sub_key] = item

                                response = update_path.run(connection, **sub_params)
                                print(response)
                            except Exception as e:
                                print(e)
                                print("Owl Post can not create a(n) " + item.type + " at this time. Please go to your vivo site and make it manually.")
                            return
                else:
                    item.n_number = match
                    print("The n number for this " + item.type + " is " + item.n_number)
                    return
            else:
                # TODO: Decide what to do if no name
                pass

        if key == 'Thing' or obj_name:
            details = item.get_details()
            for feature in details:
                item_info = input(str(feature) + ": ")
                setattr(item, feature, item_info)


def match_input(connection, label, category, exact_match):

    details = queries.find_n_for_label.get_params(connection)
    details['Thing'].extra = label
    details['Thing'].type = category

    print(category)

    matches = queries.find_n_for_label.run(connection, **details)

    choices = {}
    count = 1
    for key, val in matches.items():
        choices[count] = (key, val)
        count += 1

    if exact_match:
        if choices:
            for key, val in choices.items():
                number, lab = val
                if lab.lower() == label.lower():
                    match = number
                    return match
        match = None
        return None

    index = -1
    if choices:
        for key, val in choices.items():
            number, label = val
            print(str(key) + ': ' + label + ' (' + number +')\n')

        index = int(input("Do any of these match your input? (if none, write -1): "))

    if not index == -1:
        nnum, label = choices.get(index)
        match = nnum
    else:
        match = None

    return match


def scrub(label):
    clean_label = label.replace('"', '\\"')
    return clean_label


def main(argv1):
    config_path = argv1
    config = get_config(config_path)

    email = config.get('email')
    password = config.get ('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')

    connection = Connection(vivo_url, email, password, update_endpoint, query_endpoint)

    prepare_query(connection)


if __name__ == '__main__':
    main(sys.argv[1])
