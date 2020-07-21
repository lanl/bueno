# TODO Items

* Add post-run action hook.
* Add bueno version (and git hash?) to stored metadata.
* Consider the use of client-side git hooks.
* Favor use of named tuples.
* Merge common run script code into an public, importable thing.
* Automate generation of documentation.
* Add experiment host name setter/getter. Fixes potential back-end node naming
* problems.
* Add compiler, etc. to build metadata.
* Fix run-time issue where failures occur if non-container mpiexec is in PATH.
* Add environmental push/pop.
* Document how relative paths work in bueno run scripts. Note
* that paths are relative to the run script.
* Automate the running of pylint for development purposes.
  (e.g., ```python3 -m pylint bueno```)
* Consider the use of bandit and automate its use for development purposes.
* Automate bumpversion actions.
