# Extras

This example demonstrates how to use bueno's `--extras` feature when executing a
bueno run script. Additionally, it demonstrates how bueno utilities can test the
validity of import statements to give meaningful warnings instead of simply
terminating with a run-time error.

Try to run this example, execute the following:
```shell
bueno run -a none -p extras.py
```

When reviewing the output, you will find there are warnings emitted during its
execution:
```
*** Note: mymod is not imported ***
*** Note: mypackmod not imported ***
```

This shows that without using the `--extras` feature in this
particular case we have not correctly imported necessary libraries. Now, try
executing the `run-example` script instead:
```
./run-example
```

Please notice that the prior warnings have been replaced with hello statements
from the newly imported library. Examining the contents of the `run-example`
script, you will find that it is a modified version of the `bueno run` command
that we have been using for the last few examples:
```shell
bueno run -a none --extras .:./mypackage -p ./extras.py
```
