# Google Cloud Platform notebook runner for [nbdev](https://github.com/fastai/nbdev/tree/master/nbdev)
> Allows running any Jupyter notebook function on Google Cloud Platform.


## Install

```sh
git clone https://github.com/vlasenkoalexey/gcp_runner
pip install -e gcp_runner

#TODO: upload to pypi
```

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


### Updating project
If you do any changes, call `gcp_runner.core.export_and_reload_all` to convert all notebooks to python, and reload all modules. Note that modules are reloaded in an order defined by notebook names to make sure that dependencies are processed correctly. If there are errors in one of the modules, you can ignore them by setting ignore_errors=True. Or just restart Kernel.

```python
from gcp_runner.core import export_and_reload_all
export_and_reload_all(silent=True, ignore_errors=False)
```

### Testing code locally
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


Or you can test that code can be executed locally as a docker container.
In order to build your own Docker file, set `build_docker_file` argument:

```python
import gcp_runner.local_runner
gcp_runner.local_runner.run_docker(
    some_function_to_run_on_cloud,
    'gcr.io/deeplearning-platform-release/tf2-cpu.2-1',
    build_docker_file=None)
```

<pre>
Running in Docker container:  
docker run -v /usr/local/google/home/alekseyv/vlasenkoalexey/gcp_runner/gcp_runner:/gcp_runner gcr.io/deeplearning-platform-release/tf2-cpu.2-1 python -u -m gcp_runner.entry_point --module-name=gcp_runner.index --function-name=some_function_to_run_on_cloud
in gcp_runner entry point  
running entrypoint function: gcp_runner.index.some_function_to_run_on_cloud  
running some_function_to_run_on_cloud  
in main before sleep 1  
in main after sleep 2  
in main after sleep 3  
in main after sleep 4 
</pre>

For simple use cases you might be able to use existing images.
In order bo build your own, set `build_docker_file` parameter.

In order to authenticate your project with gcr.io container registry, run following command once:

```sh
gcloud auth configure-docker
```

### Running on Google Cloud AI Platform

TODO: describe google cloud sdk setup

Running as a package on Google Cloud AI Platform:

```python
import gcp_runner.ai_platform_runner

gcp_runner.ai_platform_runner.run_package(
     some_function_to_run_on_cloud, 
     'gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir')
```

<pre>
Trimmed output:  
Running training job using package on Google Cloud Platform AI:  
gcloud ai-platform jobs submit training ai_platform_runner_train_package_20200327_131147 \\  
 --runtime-version=2.1 \\   
 --python-version=3.7 \\   
 --stream-logs \\   
 --module-name=gcp_runner.entry_point \\   
 --package-path=/usr/local/google/home/alekseyv/vlasenkoalexey/gcp_runner/gcp_runner \\  
 --job-dir=gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir \\  
 --scale-tier=basic \\  
 --use-chief-in-tf-config=True \\  
 -- \\  
 --job-dir=gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir \\  
 --module-name=gcp_runner.index \\  
 --function-name=some_function_to_run_on_cloud  
        
Job [ai_platform_runner_train_package_20200327_131147] submitted successfully.  
INFO	2020-03-27 13:11:51 -0700	service		Validating job requirements...  
INFO	2020-03-27 13:11:51 -0700	service		Job creation request has been successfully validated.  
INFO	2020-03-27 13:11:51 -0700	service		Job ai_platform_runner_train_package_20200327_131147 is queued.  
INFO	2020-03-27 13:11:51 -0700	service		Waiting for job to be provisioned.  
INFO	2020-03-27 13:11:53 -0700	service		Waiting for training program to start.  
...  
INFO	2020-03-27 13:13:23 -0700	master-replica-0		Running command: python3 -m gcp_runner.entry_point --job-dir=gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir --module-name=gcp_runner.index --function-name=some_function_to_run_on_cloud --job-dir gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		in gcp_runner entry point  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		running entrypoint function: gcp_runner.index.some_function_to_run_on_cloud  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		additional args: ['--job-dir=gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir', '--job-dir', 'gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir']  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		running some_function_to_run_on_cloud  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		in main before sleep 1  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		in main after sleep 2  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		in main after sleep 3  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		in main after sleep 4  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		Module completed; cleaning up.  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		Clean up finished.  
INFO	2020-03-27 13:13:35 -0700	master-replica-0		Task completed successfully.  
state: SUCCEEDED 
</pre>

Running as a custom Docker container on Google Cloud AI Platform:

```python
import gcp_runner.ai_platform_runner

gcp_runner.ai_platform_runner.run_docker_image(
    some_function_to_run_on_cloud,
    'gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir',
    build_docker_file='Dockerfile',
    master_image_uri='gcr.io/alekseyv-scalableai-dev/tf2-cpu.2-1')
```

<pre>
Trimmed output:  
INFO	2020-03-27 13:01:57 -0700	master-replica-0		running some_function_to_run_on_cloud  
INFO	2020-03-27 13:01:57 -0700	master-replica-0		in main before sleep 1  
INFO	2020-03-27 13:01:59 -0700	master-replica-0		in main after sleep 2  
INFO	2020-03-27 13:02:04 -0700	master-replica-0		in main after sleep 3  
INFO	2020-03-27 13:02:09 -0700	master-replica-0		in main after sleep 4  
</pre>

TODO: example how to run distributed training
TODO: example how to run distributed hyper parameter tuner

### Running Google Cloud Kubernetes

- TODO: describe how to setup and configure Kubernetes
- TODO: describe that it is faster to use Kubernetes for iterative work
- TODO: distributed training
- TODO: distributed HP tuning

Note that Kubernetes doesn't offer convenient way of streaming logs, so currently script is going to keep pulling logs until you terminate it.

```python
import gcp_runner.kubernetes_runner

gcp_runner.kubernetes_runner.run_docker_image(
    some_function_to_run_on_cloud,
    'gs://alekseyv-scalableai-dev-criteo-model-bucket/test-job-dir',
    build_docker_file='Dockerfile',
    image_uri='gcr.io/alekseyv-scalableai-dev/tf2-cpu.2-1')
```

<pre>
Trimmed output:  
kubernetes-runner-train-docker-chief-0		running some_function_to_run_on_cloud  
kubernetes-runner-train-docker-chief-0		in main before sleep 1  
kubernetes-runner-train-docker-chief-0		in main after sleep 2  
kubernetes-runner-train-docker-chief-0		in main after sleep 3  
kubernetes-runner-train-docker-chief-0		in main after sleep 4  
</pre>

## Worklog/Ideas

- Review and normalize API names
  - Provide 2 APIs, one for running everything as a package, one as a container and specify where to run it as an argument. So moving from local environment to remote environment is just a matter of a flag switch
- Fix packages setup for Linux
- Add tests
- Either add a function to show inline tensorboard, or a callback to show training/validation graphs for remote runs
- Collecting usage stats basing on job name
- Add callbacks/functionality to bring model/environment variables back to notebook instance
- Explore magics instead of function calls for running code in the cloud
- Only reload updated modules
- Try to update globals, or at least show warnings when reloaded module has global variables
- Make logic for pulling Kubernetes logs better
- Jupyter lab/notebook extension to run any command when some button is pressed, and attach code for notebook conversions
- Add function to setup service account
- Add logic to download and configure service account from packages
- Support project_id replacement for docker container image uri
- Add function to install Video drivers on Kubernetes

