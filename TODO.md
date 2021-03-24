# TODO Items

* Restructure bueno build argument processing to handle forwarding of
  builder-specific arguments.
* Add post-run action hook.
* Add md5 of images, etc. to output data.
* Add bueno version (and git hash?) to stored metadata.
* Consider the use of client-side git hooks.
* Favor use of named tuples.
* Merge common run script code into an public, importable thing.
* Add experiment host name setter/getter. Fixes potential back-end node naming
  problems.
* Add compiler, etc. to build metadata.
* Fix run-time issue where failures occur if non-container mpiexec is in PATH.
* Add environmental push/pop.
* Document how relative paths work in bueno run scripts. Note
  that paths are relative to the run script.
* Automate bumpversion actions.
