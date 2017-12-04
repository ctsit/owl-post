import os
import os.path
import sys
import yaml

from owlery import Connection
import queries

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config

def prepare_query(connection):
    template_type = get_template_type('queries')

    head, sep, tail = template_type.partition('.')
    template_choice = head
    print(template_choice)

    template_mod = getattr(queries, template_choice)
    params = template_mod.get_params(connection)

    for key, val in params.items():
        fill_details(key, val, template_choice, connection)

    response = template_mod.run(connection, **params)
    print(response)

def get_template_type(folder):
    dir = os.getcwd()
    direc = os.path.join(dir, folder)

    template_options = {}
    count = 1
    for file in os.listdir(direc):
        if file.startswith('__init__') or file.endswith('.pyc'):
            pass
        else:
            template_options[count] = file
            count += 1

    for key, val in template_options.items():
        print(str(key) + ': ' + val + '\n')

    index = input("Enter number of query: ")
    return template_options.get(index)

def fill_details(key, item, task, connection):
    """
    Given an item, calls get_details and iterates through the list, prompting the user for the literal values.
    """
    print('*' * 20 + '\n' * 2 + "Working on " + key + '\n' * 2 + '*' * 20)
    sub_task = "make_" + item.type

    print("Fill in the values for the following (if you do not have a value, leave blank):")
    #Check if user knows n number
    obj_n = raw_input("N number: ")
    if obj_n:
        item.n_number = obj_n
        #TODO: add label check
    else:
        #For non-Thing objects, ask for further detail
        if key != 'Thing':
            #Ask for label
            if key == 'Author':
                first_name = raw_input("First name: ")
                if first_name:
                    item.first = first_name

                middle_name = raw_input("Middle name: ")
                if middle_name:
                    item.middle = middle_name

                last_name = raw_input("Last name: ")
                if last_name:
                    item.last = last_name
                obj_name = last_name + ", " + first_name + " " + middle_name

            else:
                obj_name = raw_input(key + " name/title: ")

            if obj_name:
                item.name = scrub(obj_name)
                #Check if label already exists
                deets = {}
                search_query = "get_" + item.type + "_list"
                try:
                    query_path = getattr(queries, search_query)

                    current_list = query_path.run(connection, **deets)
                    match = match_input(obj_name, current_list)
                except Exception as e:
                    print(e)
                    match = 'none'

                if match == 'none':
                    #temporary fix for other types of publciations
                    if task == 'make_letter':
                        task = 'make_academic_article'

                    if sub_task != task:
                        #If this entity is not the original query, make entity
                        create_obj = raw_input("This " + item.type + " is not in the database. Would you like to add it? (y/n) ")
                        if create_obj == 'y' or create_obj == 'Y':
                            try:
                                update_path = getattr(queries, sub_task)
                                params = {key: item}
                                response = update_path.run(connection, **params)
                                print(response)
                            except Exception as e:
                                print("Owl Post can not create a(n) " + item.type + " at this time. Please go to your vivo site and make it manually.")
                    else:
                        #Get additional details
                        details = item.get_details()
                        for feature in details:
                            item_info = raw_input(str(feature) + ": ")
                            setattr(item, feature, item_info)
                else:
                    item.n_number = match
                    print("The n number for this " + item.type + "is " + item.n_number)
            else:
                #TODO: Decide what to do if no name
                pass;
        else:
            print("Look up the n number and try again.")

def match_input(label, existing_options):
    choices = {}
    count = 1
    print(existing_options)
    for key, val in existing_options.items():
        if label.lower() in val.lower():
            choices[count] = (key, val)
            count += 1

    index = -1
    if choices:
        for key, val in choices.items():
            number, label = val
            print(str(key) + ': ' + label + '(' + number + ')\n')

        index = input("Do any of these match your input? (if none, write -1): ")
    if not index == -1:
        nnum, label = choices.get(index)
        match = nnum
    else:
        match = 'none'

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
    check_url = config.get('checking_url')

    connection = Connection(vivo_url, check_url, email, password, update_endpoint, query_endpoint)

    prepare_query(connection)

if __name__ == '__main__':
    main(sys.argv[1])