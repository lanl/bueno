# bueno: Metadata Example
This is an overview of the metadata aquisition and recording tools provided by
bueno. This example will record the application being executed by the run script
and some information about the system it's being run on. In the metadata.py
runscript, you'll find that a dictionary is created and populated with
information before lastly being written to a file.
```
adict = dict()

# collect metadata
adict['Application'] = {'argv': argv}
adict['System'] = {
    'whoami': host.whoami(),
    'hostname': host.hostname()
}
# save metadata to file
metadata.add_asset(metadata.YAMLDictAsset(adict, 'yaml-metadata'))
```

To illustrate this for yourself, execute the runscript with the ususal
```
bueno run -a none -p metadata.py
```
In the terminal there will be some notes about the kind of information gathered
and where it was saved. Several files are generated each time the run script is
executed. Information about the environment, bueno's terminal log, the run
configuration are all stored in their respective files. Additionally there is an
arbitrary ```some-metadata.txt``` file.

In the same way that ```yaml-metadata``` was added as a metadata asset, bueno
supports the creation of any number of arbitrary metadata files.