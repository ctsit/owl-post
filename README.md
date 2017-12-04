# owl-post
Send data back and forth from Vivo

The goal of owl-post is to allow users to interact with Vivo without having to learn the ontology, SPARQL, or anything about rdf. The list of available queries can be found in the queries directory.

### Before You Begin
Make sure to edit the example config file and rename it to `config.yaml`. If you do not update it, you will not be able to communicate with your Vivo. The email and password must be for a vivo account with admin rights. Note that your checking_url and upload_url may be the same, but you must fill in both. The input_file is only necessary for automated processes, like hedwig.

## owls.py
```python owls.py my/path/to/config/file```

owls is the command line version of manually adding or querying data to or from Vivo through the web interface. Simply run the program, and then select the query you would like by number from the list. Then follow the instructions (make sure to leave inputs blank for information you do not know). 

## hedwig.py
```python hedwig.py my/path/to/config/file```

hedwig takes bibtex files from `webofknowledge.com/wos` and converts them into triples which it then uploads. Search the webofknowledge site with your desired query and save the results as a bibtex file (optionally to the data_in folder). Then update the config file with the bibtex file location.
