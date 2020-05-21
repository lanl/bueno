# TODO Items
- Add experiment host name setter/getter. Fixes potential back-end node naming
  problems.
- Add compiler, etc. to build metadata.
- Fix run-time issue where failures occur if non-container mpiexec is in PATH.
  See: https://hpc.github.io/charliecloud/command-usage.html
- Add environmental push/pop.
- Document how to use mypy: ```mypy --strict .```
- Automate the running of mypy for development purposes.
- Automate the running of flake8 for development purposes.
- Automate the running of pylint for development purposes.
  (e.g., ```python3 -m pylint bueno```)
- Consider the use of bandit and automate its use for development purposes.
- Automate bumpversion actions.
