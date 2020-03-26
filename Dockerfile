# Dockerfile

#ARG BASE_IMAGE=''
#FROM ${BASE_IMAGE}
FROM gcr.io/deeplearning-platform-release/tf2-cpu.2-1

# python is python3.7 and pip is pip3.7 in gcr.io/deeplearning-platform-release/tf2-gpu.2-1

WORKDIR /root

RUN pip install google-cloud-bigquery
RUN pip install google-cloud-bigquery-storage
RUN pip install google-cloud-logging
#RUN pip install intel-tensorflow==2.1.0


ENV PROJECT_ID=alekseyv-scalableai-dev
ENV GOOGLE_APPLICATION_CREDENTIALS=/root/alekseyv-scalableai-dev-077efe757ef6.json

#ENV KMP_AFFINITY=""
#ENV TF_DISABLE_MKL=1
#ENV OMP_NUM_THREADS=1
#RUN echo ${OMP_NUM_THREADS}
#ENV NUM_INTER_THREADS=2
#ENV NUM_INTRA_THREADS=1
#ENV OMP_NUM_THREADS=6
#RUN python --version
#RUN pip --version
# TF built with avx512 optimization
#COPY dependencies/tensorflow-2.1.0-cp37-cp37m-linux_x86_64.whl /root/
#RUN pip install --upgrade /root/tensorflow-2.1.0-cp37-cp37m-linux_x86_64.whl
RUN pip install tensorboardX
RUN pip install --no-deps tensorflow-io==0.7.2
RUN pip install pandas

RUN mkdir /root/model
COPY alekseyv-scalableai-dev-077efe757ef6.json /root/
COPY gcp_runner/* /root/

# Sets up the entry point to invoke the trainer.
# ENTRYPOINT ["python", "trainer/trainer.py", "/root/model"]