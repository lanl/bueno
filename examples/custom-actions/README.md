# bueno: Custom Actions Example

In this example, we consider a straightforward bueno run script with both pre-
and post-experiment actions. These custom actions are implemented as separate,
user-defined methods provided as callback functions to bueno that are
automatically invoked at appropriate times before and after experiment
execution, respectively.

## Setup
As the name implies, a `pre-action` occurs before the application is executed.
This action provides an opportunity to perform any setup needed to run the
application.

## Gathering information
In the definition for our post-action callback function, you will find that the
variable number of arguments passed in `kwargs` is broken down into specific,
meaningful values. They are:
```python
cmd = kwargs.pop('command')    # The command used to execute the experiment.
out = kwargs.pop('output')     # The captured output (new-line delimited).
stm = kwargs.pop('start_time') # The start time of the provided command.
etm = kwargs.pop('end_time')   # The end time of the provided command.
tet = kwargs.pop('exectime')   # The execution time (in seconds) of the command.
```

In this example, `cmd` is the command string that was issued to the terminal
emulator to run our bash script. `out` is a new-line delimited list containing
`stdout` and `stderr` text emitted from our script. The last three variables
contain timing information gathered from the execution of our test application.
All of these values are used within the `post_action` scope to record
experiment-specific data.
