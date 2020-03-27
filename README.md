# Google Cloud Platform notebook runner for [nbdev](https://github.com/fastai/nbdev/tree/master/nbdev)
> Allows running any Jupyter notebook function on Google Cloud Platform.


This file will become your README and also the index of your documentation.

## Install

`pip install gcp_runner`

## How to use

Let's define some function that we want to run in notebook as well as on Google Cloud.
Note that cell has to be marked with export attribute:

```python
#export
import time

def some_function_to_run_on_cloud():
    print('running some_function_to_run_on_cloud')
    print('in main before sleep 1')
    time.sleep(2)
    print('in main after sleep 2')
    time.sleep(5)
    print('in main after sleep 3')
    time.sleep(5)
    print('in main after sleep 4')
```

Running it in notebook as usual:

```python
some_function_to_run_on_cloud()
```

    running some_function_to_run_on_cloud
    in main before sleep 1
    in main after sleep 2
    in main after sleep 3
    in main after sleep 4


If you do any changes, call `gcp_runner.core.export_and_reload_all` to convert all notebooks to python, and reload all modules.

```python
from gcp_runner.core import export_and_reload_all
export_and_reload_all(silent=True)
```

    in gcp_runner entry point
    running entrypoint function: gcp_runner.index.some_function_to_run_on_cloud
    running some_function_to_run_on_cloud
    in main before sleep 1
    in main after sleep 2
    in main after sleep 3
    in main after sleep 4


Test that code can be executed locally as a Python script:

```python
import gcp_runner.local_runner
gcp_runner.local_runner.run_python(some_function_to_run_on_cloud)
```

    in gcp_runner entry point
    running entrypoint function: gcp_runner.index.some_function_to_run_on_cloud
    running some_function_to_run_on_cloud
    in main before sleep 1
    in main after sleep 2
    in main after sleep 3
    in main after sleep 4

