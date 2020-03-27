# Dockerfile

#ARG BASE_IMAGE=''
#FROM ${BASE_IMAGE}
FROM gcr.io/deeplearning-platform-release/tf2-cpu.2-1

WORKDIR /root

RUN mkdir /root/models
RUN mkdir /root/gcp_runner
COPY gcp_runner/* /root/gcp_runner/

# Sets up the entry point to invoke the trainer.
# ENTRYPOINT ["python", "trainer/trainer.py", "/root/model"]