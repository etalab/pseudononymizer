FROM continuumio/miniconda3

COPY . /app

WORKDIR /app

RUN  apt-get update -y

RUN  apt-get install build-essential -y

RUN  apt-get install unzip

RUN  conda env update --file environment.yml

RUN wget https://github.com/psorianom/emnlp2017-bilstm-cnn-crf/archive/master.zip

RUN unzip master.zip

EXPOSE 5001

ENTRYPOINT ["/opt/conda/envs/pseudonym_api/bin/python"]

ENV PYTHONPATH ./emnlp2017-bilstm-cnn-crf-master/

CMD ["run_keras_server.py"]
