# Bueno: Extras Example
This example demonstrates how to use the --extras tag when executing a bueno
run script as well as how some of bueno's utils can test the validity of
import statements and give meaningful warnings instead of simply erroring out.

Try to run this the same way you did the other examples. That is to say, use:
```shell
bueno run -a none -p extras.py
```

If you review the information you'll find there are some warnings/notes left in 
the program output.
```
*** Note: mymod is not imported ***
*** Note: mypackmod not imported ***
```

This shows that without using the --extra tag when calling bueno we've not
correctly imported necessary libraries. Now try executing the run-example
bashfile instead.
```
./run-example
```

Notice that the warning notes that we saw earlier have been replaced with hello
statements from the properly included library. Examining the contents of the
run-example file you'll find that it's a modified version of the bueno run call
that we've been using for the last few examples with the --extras tag followed
by the relative name of the needed directory.
```shell
bueno run -a none --extras .:./mypackage -p ./extras.py
```
