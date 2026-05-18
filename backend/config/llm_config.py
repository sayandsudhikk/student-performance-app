# Configuration for Google Cloud Vertex AI
PROJECT_ID = '<your-gcp-project-id>'
LOCATION = 'us-central1'
# model_name template & id (used when not calling generative language API)
MODEL_NAME = 'projects/{project}/locations/{location}/models/{model_id}'  # format with model_id
MODEL_ID = '<your-model-id>'  # set to the deployed model identifier

# GENERATIVE LANGUAGE API specific settings
# if USE_GEN_API is True, requests will be sent to generativelanguage.googleapis.com
# using the simpler model identifier (e.g. 'gemini-flash-latest') and API key header.
USE_GEN_API = True  # using the Generative Language API with API key
GEN_MODEL = 'gemini-2.0-flash'  # stable free-tier model from AI Studio

# Option 1: use application default credentials (service account JSON)
#     set GOOGLE_APPLICATION_CREDENTIALS env variable before running.
# Option 2: supply an API key from AI Studio and enable REST calls below.
# IMPORTANT: The previous API key was committed to git and was automatically
# revoked by Google ("reported as leaked"). You MUST create a NEW key.
# Steps: go to https://aistudio.google.com/app/apikey -> "Create API key"
# Then paste the new key below (NEVER commit it to git again).
API_KEY = 'PASTE_YOUR_NEW_API_KEY_HERE'  # replace this!
