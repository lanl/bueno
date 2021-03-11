# bueno: Build And Run Example

## Build
Previous examples only used the run feature of bueno, however, this example
explores bueno's build command. We'll start by building a container application
for nbody, our example application.
```
bueno build -s Dockerfile.mpich -t nbody
```
Once completed, there will be a new tarball in the acting directory. We'll use
this when executing the bueno run script.

---

## Run
Instead of simply ordering bueno to execute our run script as we have in the
past, we'll be providing bueno with a container to work with.
```
bueno run -i nbody.tar.gz -p build-and-run.py
```

If successful, the terminal will fill with output from the containerized
application. If however, you encountered some errors, try following the fix
outlined in the following tip.


> Tip: If you encountered an error similar to this:
> ```
> What: run error encountered.
> Why:  Cannot determine the number of nodes in your job.
> ```
> There is likely a problem with your Slurm installation. However, there's a
> fairly simple work around we can use to bypass this. First, to get an idea of
> what variables aren't being set properly, visit the
> [slurm configuration tool](https://slurm.schedmd.com/configurator.html) and
> fill it out.
>
> You can find some answers specific to you your setup with
> ```shell
> slurmd -C
> ```
> Once you're done filling out and submitting the form, you'll have a list of
> slurm variables. Now it's just a matter of finding the relevant variable from
> the list and creating an environment variable to fulfill the demand. For
> example:
> ```
> SLURM_CPUS_ON_NODE=2
> ```
> will solve the error message described above.

