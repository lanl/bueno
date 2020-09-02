# bueno: Custom Actions Example
This code demonstrates a simple bueno run script with pre and post experiment
actions. These custom actions are defined as separate methods and passed as
callback functions when running the application container.

There are several other parameters that can be given when running the
applicaiton container, but we'll be focusing on three for this example. Those
being: command (cmd), pre-action method (preaction) and, post-action method.
(postaction)

## Gathering information
In the definition for out postaction callback function you'll find that the
variable number of arguments passed in kwargs is broken down into specific,
meaningful values.
```
cmd = kwargs.pop('command')  # command sent to terminal
out = kwargs.pop('output')  # output from example-app
stm = kwargs.pop('start_time')  # timing values
etm = kwargs.pop('end_time')
tet = kwargs.pop('exectime')
```

cmd is the original command that was issued to the terminal to run our little
bash script. out is a list containing everything that was output from bash in
print statements. The last three variable pertain to the timing of the app's
execution.

As you can see, all of these values can be used within the post test namespace;
providing ample records with which to perform post action analysis.

## Setting up
As the name implies, preaction occurs before the application is executed. It's
an opporunity to perform any necessary setup needed to run the application or
perhaps gather user input.
