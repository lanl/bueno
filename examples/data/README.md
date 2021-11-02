# Data

This is an overview of some of the data acquisition and recording tools
provided by bueno. This example will record the executed application's output
and some additional information about the system on which it was executed.

## Exploring the code:
The following lines in the example run script setup two additional data
assets. The first is called `some-data.txt`. Because there is no information
assigned to this asset, it will simply generate an empty file.  The file will be
written to a subdirectory, illustrating that the relative location and depth of
saved data are also user-definable.

The second asset is based on a run-time populated dictionary, and will contain
information acquired about the user executing the script and the host on which
it was run.

```python
logger.log('Adding a file asset...')
# Add an arbitrary data file to a subdirectory.
data.add_asset(
    data.FileAsset('some-data.txt', 'subdir-a/subdir-b')
)

logger.log('Adding a YAML dictionary asset...')
adict = {}
# Populate the dictionary with relevant data.
adict['Application'] = {'argv': argv}
adict['System'] = {
    'whoami': host.whoami(),
    'hostname': host.hostname()
}
# Save the data to a file.
data.add_asset(
    data.YAMLDictAsset(adict, 'yaml-data')
)
```

## Trying it Out
To test this for yourself, execute the following command:

```shell
bueno run -a none -p data.py
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
  output_path: /home/user/bueno/examples/data
```
and you will find that the second asset defined in the run script created a file
with a similar format to the others. Additionally, there is a record of the
run script executed and the output sent to the terminal at run-time.

The `some-data.txt` file asset is also present two levels down in a
subdirectory. This illustrates how bueno supports the creation of any
number of data assets as well as quite a few formats. Please consult
[this](https://github.com/lanl/bueno/blob/master/bueno/public/data.py) for
a full list.
