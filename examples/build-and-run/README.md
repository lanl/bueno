# Build And Run

## Build
Previous examples used only bueno's `none` image activator. This example,
however, explores using bueno's `charliecloud` image activator. We will start by
building a container image using Charliecloud for `nbody`, our example MPI
application.
```
ch-build2dir --force -t nbody-img -f ./Dockerfile.mpich . .
```
Once completed, there will be a new directory named `nbody-img` in your working
directory. We will use the contents of this directory when executing the bueno
run script.

---

## Run
Instead of simply instructing bueno to execute our run script as we have in the
past, we will provide bueno with a container image to work with.
```
bueno run --do-not-stage -i nbody-img -p build-and-run.py
```

If successful, the terminal will fill with output from the containerized
application. If you encountered some errors, try following the workarounds
outlined in the following tip.

> Tip: If you encountered an error similar to this:
> ```
> What: run error encountered.
> Why:  Cannot determine the number of nodes in your job.
> ```
>
> or this:
> ```
> ch-run[251876]: join: no valid peer group size found (ch-run.c:382)
>
> ```
> Try the following:
> ```
> export SLURM_CPUS_ON_NODE=2
> ```
