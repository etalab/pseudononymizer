# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F text=@dog.jpg 'http://localhost:5000/predict'
# Submita a request via Python:
#	python simple_request.py

# import the necessary packages
from itertools import groupby

import flask
from flask_cors import CORS, cross_origin
# import sys
# sys.path.append("/home/pavel/temp/ukp_forks/emnlp2017-bilstm-cnn-crf")
from flask import request
# from nltk import sent_tokenize, RegexpTokenizer
from sentence_splitter import split_text_into_sentences
from neuralnets.BiLSTM import BiLSTM
from util.preprocessing import load_names, FR_NAMES_PATH, addCharInformation, addCasingInformation, \
    addIsNameInformation, createMatrices
import re
import logging
from sacremoses.tokenize import MosesTokenizer, MosesDetokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)
CORS(app)
model = None
keyword_processor = None
training_tags = None
moses_tokenizer = MosesTokenizer(lang="fr")
moses_detokenizer = MosesDetokenizer(lang="fr")


# pattern = r"\@-\@|\w+['´`]|\w+|\S+"
# regex_tokenizer = RegexpTokenizer(pattern, flags=re.UNICODE | re.IGNORECASE)


def load_names_processor():
    # :: Load vocabulary for is_name features ::

    global keyword_processor
    from flashtext import KeywordProcessor
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_list(list(load_names(FR_NAMES_PATH).keys()))
    logging.info("Loaded french proper names...")
    return keyword_processor


def get_model_tags(model):
    """
    Get the tags of the trained model and return them as a list
    :param model:
    :return:
    """
    model_name = list(model.idx2Labels.keys())[0]
    tags = list(model.idx2Labels[model_name].values())
    # Keep
    tags = list(set([t[2:] if len(t) > 1 else t for t in tags]))
    return tags


def load_model():
    # load the pre-trained Keras model
    global model
    global training_tags

    model = BiLSTM.loadModel("./model/model_jurica_rest")
    model.models["jurica_enriched"]._make_predict_function()  # This is to avoid troubles with  Flask's threads
    training_tags = get_model_tags(model)
    logging.info("Loaded NER model...")


def pre_treat_text(raw_text):
    # TODO: We should really use the same tokenizer used to generate the train.iob file (moses) as doctrine did
    # pre_treat_text = re.sub(r"(\w{2,})-(\w+)", r"\1@-@\2", raw_text, flags=re.IGNORECASE)  # Add @ to dashes
    pre_treat_text = re.sub(r"\n{2,}", r"\n", raw_text)  # Replace two or more lines by a single line
    pre_treat_text = re.sub(r"\xa0", r" ", pre_treat_text)  # Replace this new line symbol by a space
    pre_treat_text = re.sub(r"_+", r"", pre_treat_text)  # Underscore kills Tagger training :/
    pre_treat_text = re.sub(r"’", r"'", pre_treat_text)
    pre_treat_text = re.sub(r"^\s+$", r"", pre_treat_text,
                            flags=re.MULTILINE)  # Remove empty lines only containing spaces

    pre_treated_lines = pre_treat_text.split("\n")

    return pre_treated_lines, pre_treat_text


def post_treat_text(text):
    post_treat_text = re.sub(r"(\.\.\.\s?){2,}", r"...", text)
    post_treat_text = re.sub(r"(…\s?)+", r"… ", text)
    post_treat_text = re.sub(r"(\s\w')\s(.)", r"\1\2", post_treat_text)  # Remove space after apostrophe
    post_treat_text = re.sub(r"(\()\s+(\w)", r"\1\2", post_treat_text)  # Space after left parenthesis
    post_treat_text = re.sub(r"(.)\s@\s?-\s?@\s(.)", r"\1-\2", post_treat_text)  # Remove Moses tokenizer dash @ symbol
    # post_treat_text = re.sub(r"\w(\.)(\.{2,})", r"\1 \2", post_treat_text)  # Fix Moses pasting three dots together with precedent token
    return post_treat_text


def tokenize_text(text_lines):
    sentences_tokens = []

    if not isinstance(text_lines, list):
        text_lines = [text_lines]

    for line in text_lines:
        sentences = split_text_into_sentences(line, language="fr")
        for sentence in sentences:
            tokens = moses_tokenizer.tokenize(sentence, aggressive_dash_splits=True, escape=False)
            sentences_tokens.append(tokens)

    return sentences_tokens


def prepare_input(text):
    text = text.strip()
    pre_treated_lines, _ = pre_treat_text(text)
    tokenized_sentences = tokenize_text(pre_treated_lines)
    sentences = [{'tokens': sent} for sent in tokenized_sentences]
    addCharInformation(sentences)
    addCasingInformation(sentences)
    addIsNameInformation(sentences, keyword_processor=keyword_processor)
    data_matrix = createMatrices(sentences, model.mappings, True)
    return data_matrix, sentences


def tag_text(text):
    # preprocess the image and prepare it for classification
    data_matrix, sentences = prepare_input(text)

    # classify the input text and then initialize the list
    # of predictions to return to the client
    tags = model.tagSentences(data_matrix)
    tagged_conll_sequences = []

    # loop over the results and add them to the list of
    # returned predictions

    for sentenceIdx in range(len(sentences)):
        tokens = sentences[sentenceIdx]['tokens']

        for tokenIdx in range(len(tokens)):
            tokenTags = []
            for modelName in sorted(tags.keys()):
                tokenTags.append(tags[modelName][sentenceIdx][tokenIdx])
            tagged_conll_sequences.append((tokens[tokenIdx], "\t".join(tokenTags)))
        tagged_conll_sequences.append(("new_line", "new_line"))
    pass
    return tagged_conll_sequences


def prepare_output(tagged_conll_sequences, tags_to_use, replacement_token="…"):
    """
    Replace found tags with the chosen replacement token
    TODO: Deal with replacing with XXX or somethingg like that, deal with repetitions, etc
    TODO: Also, I very lazily replaced all tokens of a named entity with the replacement token, and in post-processing
    TODO: only one is left :)
    :param tagged_conll_sequences:
    :param tags_to_use:
    :return:
    """

    phrases = [list(group) for key, group in groupby(tagged_conll_sequences, lambda x: x[0] == "new_line") if not key]

    pseudonim_phrases = []
    tagged_phrases = []
    for phrase in phrases:
        tokens_tagged = []
        tokens_pseudonim = []
        for tok, tag in phrase:
            pseudonim_tok = tok
            tagged_tok = tok
            re_finder = re.findall('\w-({})'.format("|".join(tags_to_use)), tag)
            if re_finder:
                pseudonim_tok = replacement_token
                tagged_tok = "[{0}]{1}[/{2}]".format(tag, tok, tag)
                logger.info("Replaced token {0} with replacement-token {1}".format(tok, replacement_token))
            tokens_tagged.append(tagged_tok)
            tokens_pseudonim.append(pseudonim_tok)
        pseudonim_phrases.append(tokens_pseudonim)
        tagged_phrases.append(tokens_tagged)

    # detokenize = lambda x: "\n\n".join([" ".join(f) for f in x])
    moses_detok = lambda x: "\n\n".join([moses_detokenizer.detokenize(f, unescape=False) for f in x])
    pseudonim_text = moses_detok(pseudonim_phrases)
    tagged_text = moses_detok(tagged_phrases)

    # Post-process text
    pseudonim_text = post_treat_text(pseudonim_text)
    tagged_text = post_treat_text(tagged_text)

    return pseudonim_text, tagged_text


@app.route("/tag", methods=["POST"])
@cross_origin()
def tag():
    # initialize the data dictionary that will be returned from the
    # view

    data = {"success": False}
    if request.method == "POST":
        try:
            tags_to_use = []
            if not request.form.get("tag"):
                #  Use all tags possible
                logging.info("No tags were indicated. Using all the training tags {}.".format(
                    training_tags))
                tags_to_use = training_tags
            else:
                tags_param = request.form.get("tag").split(",")

                for t in tags_param:
                    for g in training_tags:
                        if t in g:
                            tags_to_use.append(g)

            if not tags_to_use:
                logging.info(
                    "The desired tags were not found in the trained model {}. Using all the training tags.".format(
                        training_tags))
                tags_to_use = training_tags

            if request.files.get("text"):
                text = request.files["text"].read().decode("utf-8")
                logging.info("Tagging text with model...")
                conll_tagged_text = tag_text(text)
                logging.info("Preparing text as output...")
                data["pseudonim_text"], data["tagged_text"] = prepare_output(conll_tagged_text, tags_to_use)

            elif request.form.get("text"):
                text = request.form.get("text")
                logging.info("Tagging text with model...")
                conll_tagged_text = tag_text(text)
                logging.info("Preparing text as output...")
                data["pseudonim_text"], data["tagged_text"] = prepare_output(conll_tagged_text, tags_to_use)

            # indicate that the request was a success
            data["success"] = True

        except Exception as e:
            logger.error(e)
        finally:
            # return the data dictionary as a JSON response
            return flask.jsonify(data)


@app.after_request
def after_request(response):
    # response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    logger.info(
        "* Loading Keras (UKP EMNLP BiLSTM+CRF) model and Flask starting server...\n\tplease wait until server has fully started")

    load_names_processor()
    load_model()
    app.run(port=5001, host="0.0.0.0")
