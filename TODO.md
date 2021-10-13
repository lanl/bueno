# TODO Items

* Add module load example.
* Automate testing of user API usage and exported APIs:
  For example, do type checking across bueno and bueno-run-proxies.
* Add post-run action hook.
* Consider the use of client-side git hooks.
* Favor use of named tuples.
* Merge common run script code into an public, importable thing.
* Add experiment host name setter/getter. Fixes potential back-end node naming
  problems.
* Fix run-time issue where failures occur if non-container mpiexec is in PATH.
* Add environmental push/pop.
* Document how relative paths work in bueno run scripts. Note
  that paths are relative to the run script.
* Automate bumpversion actions.
