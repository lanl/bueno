# Build And Run

## Build
Previous examples used only the bueno's `run` feature. This example, however,
explores bueno's `build` command. We will start by building a container image
for `nbody`, our example MPI application.
```
bueno build -s Dockerfile.mpich -t nbody
```
Once completed, there will be a new tarball in the working directory. We will
use this image when executing the bueno run script.

---

## Run
Instead of simply instructing bueno to execute our run script as we have in the
past, we will be providing bueno with a container to work with.
```
bueno run -i nbody.tar.gz -p build-and-run.py
```

If successful, the terminal will fill with output from the containerized
application. If however, you encountered some errors, try following the
workaround outlined in the following tip.

> Tip: If you encountered an error similar to this:
> ```
> What: run error encountered.
> Why:  Cannot determine the number of nodes in your job.
> ```
> There is likely a problem with your SLURM environment. There is a
> fairly simple workaround we can use to bypass this.
>
> ```
> export SLURM_CPUS_ON_NODE=2
> ```
