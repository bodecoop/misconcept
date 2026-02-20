import oci
import os

CONFIG_PROFILE = os.environ.get("OCI_CONFIG_PROFILE", "DEFAULT")
CONFIG_PATH = os.environ.get("OCI_CONFIG_PATH", os.path.expanduser("~/.oci/config"))
ENDPOINT = os.environ.get("OCI_AI_ENDPOINT", "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com")
COMPARTMENT_ID = os.environ.get("OCI_COMPARTMENT_ID", "ocid1.tenancy.oc1..aaaaaaaawu6hkvowbuskgisv3ohg4d4qzr56zditstxhadzf7rexeeuaolba")
MODEL_ID = os.environ.get("OCI_MODEL_ID", "cohere.embed-english-light-v3.0")

config = oci.config.from_file(CONFIG_PATH, CONFIG_PROFILE)
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config,
    service_endpoint=ENDPOINT,
    retry_strategy=oci.retry.NoneRetryStrategy(),
    timeout=(10, 240)
)

def run_class_analysis(prompt: str) -> str:
    # Use CohereChatRequest and ChatDetails for LLM chat, matching model.py
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = prompt
    chat_request.max_tokens = 600
    chat_request.temperature = 1
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.75
    chat_request.top_k = 0
    chat_request.seed = 0
    chat_request.safety_mode = "CONTEXTUAL"
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=MODEL_ID)
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = COMPARTMENT_ID
    try:
        chat_response = generative_ai_inference_client.chat(chat_detail)
        print("[DEBUG] Oracle AI chat_response type:", type(chat_response))
        print("[DEBUG] Oracle AI chat_response:", chat_response)
        if hasattr(chat_response, "data"):
            data = chat_response.data
            print("[DEBUG] Oracle AI chat_response.data type:", type(data))
            print("[DEBUG] Oracle AI chat_response.data:", data)
            # If the data object has a 'chat_response' attribute (dict), extract it
            if hasattr(data, "chat_response") and data.chat_response:
                # If it's a dict-like object, convert to dict
                chat_response_obj = data.chat_response
                # If it's not a dict, try to convert
                if not isinstance(chat_response_obj, dict):
                    try:
                        import json
                        chat_response_obj = json.loads(str(chat_response_obj))
                    except Exception:
                        pass
                # Add the 'text' field if present at the top level
                if hasattr(data, "text") and data.text:
                    chat_response_obj["text"] = data.text
                return chat_response_obj
            # Fallback: just return the text field if present
            if hasattr(data, "text") and data.text:
                return {"text": data.text}
            # Fallback: return the whole data object as string
            return {"raw": str(data)}
        else:
            raise RuntimeError("Oracle AI chat response is None or missing 'data' attribute.")
    except Exception as e:
        import traceback
        print("[DEBUG] Exception in run_class_analysis:")
        print(traceback.format_exc())
        raise
