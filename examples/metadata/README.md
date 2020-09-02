# bueno: Metadata Example
This is an overview of the metadata aquisition and recording tools provided
by bueno. This example will record the application being executed by the
run script and some information about the system it's being run on.

In the metadata.py runscript, you'll find that a dictionary is created and
populated with information before lastly being written to a file.
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
In the terminal there will be some notes about the kind of information
gathered and where it was saved. If you then explore the destination
folder and open yaml-metadata.yaml. You'll find a simple, easy to read
version of the recorded data.

Something similar to this:
```
Application:
  argv:
  - /home/user/bueno/examples/metadata/metadata.py
System:
  hostname: localhost.localdomain
  whoami: user
```