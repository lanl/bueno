# bueno: A Software Framework for Automated, Reproducible Benchmarking and Analysis

System benchmarking provides a means to compare or assess the performance of
hardware or software against a point of reference. Because of the multitude of
factors that ultimately influence a benchmark’s results, reproducibility is
challenging. To aid in this, we present an extensible software framework named
bueno that provides mechanisms to record and automate many arduous, error-prone
benchmarking tasks: environmental discovery, environmental setup, program
compilation, program execution, data storage, and analysis. In this report, we
summarize bueno’s software architecture, current feature set, and methodology
for supporting automated, reproducible benchmarking and analysis.

## User Installation with pip
```
python3 -m pip install --user .
```

## User Uninstallation with pip
```
python3 -m pip uninstall bueno
```

## Building an RPM
```
python3 setup.py bdist_rpm
```
