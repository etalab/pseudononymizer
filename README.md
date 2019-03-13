# A Simple Keras (UKP BiLSTM + CRF) pseudonymization REST 'API'

## Description
This repository contains the code for starting a REST PoC pseudonymizing service. 

Pseudonymization here means finding certain identifiying entities within a text and replacing them with a token. For example, we may replace first and last names with a chain of characters ("..." or "XXXXX") such that *Mr. Jean PARMENTIER* becomes *Mr. ... ...* 

In order to find said entities, we train a supervised structured model. This task is more generally known as named entity recognition. 

This project is based on two main building blocks:
1.  The algorithm used to train the supervised model is the now classic biLSTM+CRF. The implementation used is that from [the UKP lab](https://github.com/UKPLab/emnlp2017-bilstm-cnn-crf). To train your own model for this application, you may  employ the fork created [here](https://github.com/psorianom/emnlp2017-bilstm-cnn-crf). 

2. Once the model trained, we base our REST service on the code from [*Building a simple Keras + deep learning REST API*](https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html).

This code is absolutely _not_ meant to be production-level and capable of scaling under heavy load.

## Getting started

The easiest way to start this service is by using docker and the associated Dockerfile in this repo. Assuming docker is installed, the only thing to do is:

Building the docker image:
```sh
$ docker build -t pseudonym_api:latest .
```

Next, initializing said image:

```sh
$ docker run -d -p 5001:5001 pseudonym_api:latest
```


## Submitting requests to the Keras server

Requests can be submitted via cURL:

```sh
$ curl -X POST -F text='M Soriano habite à Paris' 'http://localhost:5001/tag'
{
   "pseudonim_text":"M \u2026 habite \u00e0 Paris",
   "success":true,
   "tagged_text":"M [B-PER]Soriano[/B-PER] habite \u00e0 Paris"
}
```

Programmatically:

```sh
$ python simple_request.py 
M … habite à Paris
```

Or as a test, via the web page ```example_form.html``` in the site/ folder.
