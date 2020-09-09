# bueno: Metadata Example
This is an overview of the metadata aquisition and recording tools provided by
bueno. This example will record the application being executed by the run script
and some information about the system it's being run on. In the metadata.py
runscript, you'll find that a dictionary is created and populated with
information before lastly being written to a file.

## Exploring the code:
You'll find the following lines in the example runscript that setup two
additional metadata assets. The first of which is called ```some-metadata.txt```
as there is no information assigned to this asset, it will simply generate an
empty file. However, it will be saved in a "sub-sub-directory"; illustrating
that the depth of the subdirectory is also arbitrary.

However, the second asset is based around a populated dictionary variable and
will contain information acquired about the user executing the script and the
host script.
```python
logger.log('adding a file asset...')
# adds an arbitrary metadata file to a subfolder
metadata.add_asset(metadata.FileAsset('some-metadata.txt', 'subdir-a/subdir-b'))

logger.log('adding a yaml dict asset...')
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

## Trying it out:
To illustrate this for yourself, execute the runscript with the ususal
```shell
bueno run -a none -p metadata.py
```

In the terminal you'll find notes about the kind of information gathered
and where it was saved. Several files are generated each time the run script is
executed. Information about the host environment can be found in
environment.yaml,
```yaml
Host:
  hostname: localhost.localdomain
  kernel: Linux
  kernel_release: 5.6.6-300.fc32.x86_64
  os_release: Fedora 32 (Workstation Edition)
  whoami: user
```
the run configuration is stored in run.yaml,
```yaml
Configuration:
  do_not_stage: false
  extras: null
  image: null
  image_activator: none
  output_path: /home/user/bueno/examples/metadata
```

and you'll find that the second asset defined in the run script created a file
with a similar format to the others. Additionally there is a record of the
runscript that was executed and the output sent to the terminal at runtime.

The arbitrary ```some-metadata.txt``` asset is also present two levels down in
a subdirectory, although it is empty. That said, it illustrates how bueno
supports the creation of any number of metadata assets as well as quite a few
formats. Check
[here](https://github.com/lanl/bueno/blob/master/bueno/public/metadata.py).
for a full list.