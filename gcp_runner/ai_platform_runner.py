# AUTOGENERATED! DO NOT EDIT! File to edit: ai_platform_runner.ipynb (unless otherwise specified).

__all__ = ['run_docker_image', 'run_package']

# Cell
import inspect
from enum import Enum
from .ai_platform_constants import *

def _get_not_none(arg, default):
    return default if arg is None else arg

def _format_arg(key, value):
    return "--%s=%s" % (key.replace('_', '-'), value)

def _append_arg(args, key, value):
    if value is not None:
        if issubclass(type(value), Enum):
            value = value.value
        if issubclass(type(value), int) and value == 0:
            return

        args.append(_format_arg(key, value))

def _get_common_args(
    job_dir,
    job_name=None,
    region=None,
    scale_tier: ScaleTier = ScaleTier.CUSTOM,
    master_machine_type: MachineType = None,
    master_image_uri=None,
    master_accelerator_type: AcceleratorType = None,
    master_accelerator_count=None,
    parameter_machine_type: MachineType = None,
    parameter_machine_count=None,
    parameter_image_uri=None,
    parameter_accelerator_type: AcceleratorType = None,
    parameter_accelerator_count=None,
    worker_machine_type: MachineType = None,
    worker_machine_count=None,
    worker_image_uri=None,
    worker_accelerator_type: AcceleratorType = None,
    worker_accelerator_count=None,
    use_chief_in_tf_config=True,
    distribution_strategy_type: DistributionStrategyType = None):
    args = []

    if distribution_strategy_type and scale_tier == ScaleTier.CUSTOM:
        master_machine_type = _get_not_none(master_machine_type, MachineType.N1_STANDARD_4)
        if distribution_strategy_type == DistributionStrategyType.MIRRORED_STRATEGY:
            master_accelerator_type = _get_not_none (master_accelerator_type, AcceleratorType.NVIDIA_TESLA_K80)
            master_accelerator_count = _get_not_none(master_accelerator_count, 2)
            worker_machine_count = _get_not_none(worker_machine_count, 0)
        elif distribution_strategy_type == DistributionStrategyType.CENTRAL_STORAGE_STRATEGY:
            master_accelerator_type = _get_not_none (master_accelerator_type, AcceleratorType.NVIDIA_TESLA_K80)
            master_accelerator_count = _get_not_none(master_accelerator_count, 2)
            worker_machine_count = _get_not_none(worker_machine_count, 0)
        elif distribution_strategy_type == DistributionStrategyType.PARAMETER_SERVERSTRATEGY:
            parameter_machine_type = _get_not_none(parameter_machine_type, MachineType.N1_STANDARD_4)
            parameter_machine_count = _get_not_none(parameter_machine_count, 1)
            worker_machine_count = _get_not_none(worker_machine_count, 2)
            worker_machine_type = _get_not_none(worker_machine_type, MachineType.N1_STANDARD_4)
        elif distribution_strategy_type == DistributionStrategyType.MULTI_WORKER_MIRRORED_STRATEGY:
            master_accelerator_type = _get_not_none (master_accelerator_type, AcceleratorType.NVIDIA_TESLA_K80)
            master_accelerator_count = _get_not_none(master_accelerator_count, 2)
            worker_machine_count = _get_not_none(worker_machine_count, 2)
            worker_accelerator_type = _get_not_none (worker_accelerator_type, AcceleratorType.NVIDIA_TESLA_K80)
            worker_machine_type = _get_not_none(worker_machine_type, MachineType.N1_STANDARD_4)

    if distribution_strategy_type == DistributionStrategyType.TPU_STRATEGY and \
        (master_accelerator_count == 0 or master_accelerator_type is None):
        print('changing scale_tier to BASIC_TPU to run with TPU_STRATEGY')
        scale_tier = ScaleTier.BASIC_TPU

# Nice way ot automatically setting flags, keeping for now for future reference
#     for key, value in locals().items():
#         # print(key + '=' + str(value))
#         if key != 'args' and key != 'distribution_strategy_type' and value:
#             if key.endswith('_type') or key == 'scale_tier':
#                 args.append("--%s=%s" % (key.replace('_', '-'), value.value))
#             else:
#                 args.append("--%s=%s" % (key.replace('_', '-'), value))

    # For flags overview refer to
    # https://cloud.google.com/sdk/gcloud/reference/ai-platform/jobs/submit/training
    accelerator_format = 'count=%d,type=%s'
    _append_arg(args, 'job-dir', job_dir)
    _append_arg(args, 'job-name', job_name)
    _append_arg(args, 'region', region)
    _append_arg(args, 'scale-tier', scale_tier)

    _append_arg(args, 'master-machine-type', master_machine_type)
    _append_arg(args, 'master-image-uri', master_image_uri)
    if master_accelerator_count is not None and master_accelerator_count > 0:
        _append_arg(args, 'master-accelerator', 'count=%d,type=%s' % (master_accelerator_count, master_accelerator_type.value))

    _append_arg(args, 'parameter-server-machine-type', parameter_machine_type)
    _append_arg(args, 'parameter-server-count', parameter_machine_count)
    _append_arg(args, 'parameter-server-image-uri', parameter_image_uri)
    if parameter_accelerator_count is not None and parameter_accelerator_count > 0:
        _append_arg(args, 'parameter-server-accelerator', 'count=%d,type=%s' % (parameter_accelerator_count, parameter_accelerator_type.value))

    _append_arg(args, 'worker-machine-type', worker_machine_type)
    _append_arg(args, 'worker-count', worker_machine_count)
    _append_arg(args, 'worker-image-uri', worker_image_uri)
    if worker_accelerator_count is not None and worker_accelerator_count > 0:
        _append_arg(args, 'worker-accelerator', 'count=%d,type=%s' % (worker_accelerator_count, worker_accelerator_type.value))

    _append_arg(args, 'use-chief-in-tf-config', use_chief_in_tf_config)
    return args

# Cell
def _get_ai_platform_run_args(func, job_dir, distribution_strategy_type, use_distribution_strategy_scope):
    args.append("--job-dir=%s" % job_dir)
    if distribution_strategy_type:
        args.append("--distribution-strategy-type=%s" % distribution_strategy_type)
        if use_distribution_strategy_scope:
            args.append("--use-distribution-strategy-scope")


# Cell
import datetime
from .core import build_and_push_docker_image, run_process, get_run_python_args, format_job_dir, print_tensorboard_command
from gcp_runner import ai_platform_constants

def run_docker_image(
    func,
    job_dir,
    build_docker_file=None,
    dry_run=False,
    job_name=None,
    region=None,
    scale_tier: ai_platform_constants.ScaleTier =  ai_platform_constants.ScaleTier.CUSTOM,
    master_machine_type: ai_platform_constants.MachineType = None,
    master_image_uri=None,
    master_accelerator_type: ai_platform_constants.AcceleratorType = None,
    master_accelerator_count=None,
    parameter_machine_type: ai_platform_constants.MachineType = None,
    parameter_machine_count=None,
    parameter_image_uri=None,
    parameter_accelerator_type: ai_platform_constants.AcceleratorType = None,
    parameter_accelerator_count=None,
    worker_machine_type: ai_platform_constants.MachineType = None,
    worker_machine_count=None,
    worker_image_uri=None,
    worker_accelerator_type: ai_platform_constants.AcceleratorType = None,
    worker_accelerator_count=None,
    use_chief_in_tf_config=True,
    distribution_strategy_type: ai_platform_constants.DistributionStrategyType = None,
    use_distribution_strategy_scope: bool = None,
    **kwargs):

    if not master_image_uri:
        raise ValueError('master_image_uri argument is required')

    date_time = datetime.datetime.now()
    if not job_name:
        job_name = 'ai_platform_runner_train_docker_' + date_time.strftime('%Y%m%d_%H%M%S')
    job_dir = format_job_dir(job_dir, date_time=date_time)
    print_tensorboard_command(job_dir)

    if build_docker_file is not None:
        result = build_and_push_docker_image(build_docker_file, master_image_uri, dry_run=dry_run)
        if result:
            return result

    # see https://cloud.google.com/sdk/gcloud/reference/ai-platform/jobs/submit/training
    args = ['gcloud', 'ai-platform', 'jobs', 'submit', 'training', job_name,
           "--stream-logs"]

    common_args = _get_common_args(
        job_dir,
        region = region,
        scale_tier = scale_tier,
        master_machine_type = master_machine_type,
        master_image_uri = master_image_uri,
        master_accelerator_type = master_accelerator_type,
        master_accelerator_count = master_accelerator_count,
        parameter_machine_type = parameter_machine_type,
        parameter_machine_count = parameter_machine_count,
        parameter_image_uri = parameter_image_uri,
        parameter_accelerator_type = parameter_accelerator_type,
        parameter_accelerator_count = parameter_accelerator_count,
        worker_machine_type = worker_machine_type,
        worker_machine_count = worker_machine_count,
        worker_image_uri = worker_image_uri,
        worker_accelerator_type = worker_accelerator_type,
        worker_accelerator_count = worker_accelerator_count,
        use_chief_in_tf_config = use_chief_in_tf_config,
        distribution_strategy_type = distribution_strategy_type)
    args.extend(common_args)
    print(common_args)
    print(master_image_uri)

    args.append('--')

    args.extend(get_run_python_args(func, **kwargs))
    args.extend(_get_ai_platform_run_args(job_dir, distribution_strategy_type, use_distribution_strategy_scope))

    print('running training job using Docker image Google Cloud Platform AI:')
    print(' '.join(args).replace(' --', '\n --').replace('\n', ' \\ \n'))
    if not dry_run:
        return run_process(args)


# Cell

import os
import datetime
from .core import get_run_args, run_process, get_package_name, get_module_name, format_job_dir, print_tensorboard_command
from gcp_runner import ai_platform_constants

#IMPORTANT: we'll need to either copy entry_point.py to package,
# or tell user to declare it and call into similar entry_point logic manually.

def run_package(
    func,
    job_dir,
    job_name=None,
    runtime_version='2.1',
    python_version='3.7',
    dry_run=False,
    region=None,
    scale_tier: ai_platform_constants.ScaleTier =  ai_platform_constants.ScaleTier.CUSTOM,
    master_machine_type: ai_platform_constants.MachineType = None,
    master_image_uri=None,
    master_accelerator_type: ai_platform_constants.AcceleratorType = None,
    master_accelerator_count=None,
    parameter_machine_type: ai_platform_constants.MachineType = None,
    parameter_machine_count=None,
    parameter_image_uri=None,
    parameter_accelerator_type: ai_platform_constants.AcceleratorType = None,
    parameter_accelerator_count=None,
    worker_machine_type: ai_platform_constants.MachineType = None,
    worker_machine_count=None,
    worker_image_uri=None,
    worker_accelerator_type: ai_platform_constants.AcceleratorType = None,
    worker_accelerator_count=None,
    use_chief_in_tf_config=True,
    distribution_strategy_type: ai_platform_constants.DistributionStrategyType = None,
    use_distribution_strategy_scope: bool = None,
    **kwargs):

    date_time = datetime.datetime.now()
    if not job_name:
        job_name = 'ai_platform_runner_train_package_' + date_time.strftime('%Y%m%d_%H%M%S')

    job_dir = format_job_dir(job_dir, date_time=date_time)
    print_tensorboard_command(job_dir)

    # see https://cloud.google.com/sdk/gcloud/reference/ai-platform/jobs/submit/training
    package_name = get_package_name()
    module_name = get_module_name()
    function_name = func.__name__
    args = [
        'gcloud', 'ai-platform', 'jobs', 'submit', 'training', job_name,
        "--runtime-version=%s" % runtime_version,
        "--python-version=%s" % python_version,
        "--stream-logs",
        "--module-name=gcp_runner.entry_point",
        "--package-path=%s/%s" % (os.getcwd(), package_name)]

#        "--module-name=%s.entry_point" % package_name,

    common_args = _get_common_args(
        job_dir,
        region = region,
        scale_tier = scale_tier,
        master_machine_type = master_machine_type,
        master_image_uri = master_image_uri,
        master_accelerator_type = master_accelerator_type,
        master_accelerator_count = master_accelerator_count,
        parameter_machine_type = parameter_machine_type,
        parameter_machine_count = parameter_machine_count,
        parameter_image_uri = parameter_image_uri,
        parameter_accelerator_type = parameter_accelerator_type,
        parameter_accelerator_count = parameter_accelerator_count,
        worker_machine_type = worker_machine_type,
        worker_machine_count = worker_machine_count,
        worker_image_uri = worker_image_uri,
        worker_accelerator_type = worker_accelerator_type,
        worker_accelerator_count = worker_accelerator_count,
        use_chief_in_tf_config = use_chief_in_tf_config,
        distribution_strategy_type = distribution_strategy_type)
    args.extend(common_args)
    args.append("--")
    args.extend(get_run_args(func, **kwargs))
    args.extend(_get_ai_platform_run_args(job_dir, distribution_strategy_type, use_distribution_strategy_scope))

    if distribution_strategy_type:
        args.append("--distribution-strategy-type=%s" % distribution_strategy_type)
        if use_distribution_strategy_scope:
            args.append("--use-distribution-strategy-scope")

    print('running training job using package on Google Cloud Platform AI:')
    print(' '.join(args).replace(' --', '\n --').replace('\n', ' \\ \n'))

    if not dry_run:
        return run_process(args)
