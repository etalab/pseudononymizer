FROM continuumio/miniconda3

COPY . /app

WORKDIR /app

RUN  conda env create --file environment.yml

RUN wget https://github.com/psorianom/emnlp2017-bilstm-cnn-crf/archive/master.zip

RUN unzip master.zip 

# RUN  conda activate pseudonim_REST

ENTRYPOINT ["/opt/conda/envs/pseudonim_REST/bin/python"]

ENV PYTHONPATH "${PYTHONPATH}:/emnlp2017-bilstm-cnn-crf-master/"

CMD ["run_keras_server.py"]