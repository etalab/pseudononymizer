FROM continuumio/miniconda3

COPY . /app

WORKDIR /app

RUN  conda env create --file environment.yml

# RUN  conda activate pseudonim_REST

ENTRYPOINT ["/opt/conda/envs/pseudonim_REST/bin/python"]

ENV PYTHONPATH "${PYTHONPATH}:/lib/custom/path"

CMD ["run_keras_server.py"]