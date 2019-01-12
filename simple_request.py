# USAGE
# python simple_request.py

# import the necessary packages
import requests

# initialize the Keras REST API endpoint URL along with the input
# image path
KERAS_REST_API_URL = "http://localhost:5001/tag"

# load the input image and construct the payload for the request
text = """
Caractère communicable des documents relatifs à une enquête administrative interne effectuée au sein du service à la population : 1) le rapport de la directrice des ressources humaines au maire du 11 juillet 2017 ; 2) le rapport de la directrice des ressources humaines au maire du 20 juillet 2017 ; 3) le rapport de la directrice générale adjointe du pôle administration générale au maire du 21 juillet 2017 ; 4) la réponse en date du 7 août 2017 du maire à Madame Xsuite au signalement par cette dernière d'une souffrance au travail ; 5) la réponse en date du 7 août 2017 du maire à Madame X suite au signalement par cette dernière d'une souffrance au travail ; 6) la réponse de la chef de service Madame X du 17 août 2017 ; 7) le courrier de Madame Xdu 28 août 2017 ; 8) les témoignages des agents dans le cadre de l'enquête administrative interne ; 9) le rapport de la directrice des ressources humaines au maire du 13 septembre 2017 ; 10) le rapport du directeur du pôle administration générale au maire du du 13 septembre 2017.
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
