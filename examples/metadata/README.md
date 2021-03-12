# bueno: Metadata Example

This is an overview of some of the metadata acquisition and recording tools
provided by bueno. This example will record the executed application's output
and some additional information about the system on which it was executed.  In
the `metadata.py` run script, you will find that a dictionary is created and
populated with information before being written to a file.

## Exploring the code:
The following lines in the example run script setup two additional metadata
assets. The first is called `some-metadata.txt`. Because there is no information
assigned to this asset, it will simply generate an empty file.  The file will be
written to a subdirectory, illustrating that the relative location and depth of
saved data are also user-definable.

The second asset is based on a run-time populated dictionary, and will contain
information acquired about the user executing the script and the host on which
it was run.

```python
logger.log('Adding a file asset...')
# Add an arbitrary metadata file to a subdirectory.
metadata.add_asset(
    metadata.FileAsset('some-metadata.txt', 'subdir-a/subdir-b')
)

logger.log('Adding a YAML dict asset...')
adict = dict()
# Populate the dictionary with relevant metadata.
adict['Application'] = {'argv': argv}
adict['System'] = {
    'whoami': host.whoami(),
    'hostname': host.hostname()
}
# Save the metadata to a file.
metadata.add_asset(
    metadata.YAMLDictAsset(adict, 'yaml-metadata')
)
```

## Trying it Out
To test this for yourself, execute the following command:

```shell
bueno run -a none -p metadata.py
```

In the terminal output, you will find notes about the kind of information
gathered and where it was saved. Several files are generated each time the run
script is executed. Information about the host environment can be found in
`environment.yaml`. For example,

```yaml
Host:
  hostname: localhost.localdomain
  kernel: Linux
  kernel_release: 5.6.6-300.fc32.x86_64
  os_release: Fedora 32 (Workstation Edition)
  whoami: user
```
the run configuration stored in `run.yaml`:
```yaml
Configuration:
  do_not_stage: false
  extras: null
  image: null
  image_activator: none
  output_path: /home/user/bueno/examples/metadata
```
and you will find that the second asset defined in the run script created a file
with a similar format to the others. Additionally, there is a record of the
run script executed and the output sent to the terminal at run-time.

The empty `some-metadata.txt` asset is also present two levels down in a
subdirectory. This illustrates how bueno supports the creation of any
number of metadata assets as well as quite a few formats. Please consult
[this](https://github.com/lanl/bueno/blob/master/bueno/public/metadata.py).  for
a full list.
