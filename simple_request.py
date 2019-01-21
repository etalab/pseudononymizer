# USAGE
# python simple_request.py

# import the necessary packages
import requests

# initialize the Keras REST API endpoint URL along with the input
# image path
KERAS_REST_API_URL = "http://localhost:5001/tag"

# load the input image and construct the payload for the request
text = """
    M Soriano habite à Paris
"""

payload = {"text": text}

# submit the request
r = requests.post(KERAS_REST_API_URL, data={"tag": "PER,AUX"}, files=payload).json()

# ensure the request was sucessful
if r["success"]:
    # loop over the predictions and display them
    print(r["pseudonim_text"])

else:
    print("Request failed")
