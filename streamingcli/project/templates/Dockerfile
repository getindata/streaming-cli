FROM centos:centos8
RUN groupadd -r flink \
    && adduser -r -g flink flink -d /flink
RUN yum -y install java-11-openjdk
ENV PATH=/flink/bin:$PATH
COPY --from=registry.ververica.com/v2.5/flink:1.13.1-stream1-scala_2.12-java11 --chown=flink:flink /flink /flink
USER flink:flink
WORKDIR /flink/bin
COPY ./src /flink/python_src
COPY ./.vvp/python-java-runner.jar /flink/usrlib
ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 6123 8081

