# A Simple Keras (UKP BiLSTM + CRF) pseudonymization REST 'API'

This repository contains the code for starting a REST PoC pseudonymizing service. It is based on [*Building a simple Keras + deep learning REST API*](https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html), and the biLSTM code from [the UKP lab](https://github.com/UKPLab/emnlp2017-bilstm-cnn-crf).

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
