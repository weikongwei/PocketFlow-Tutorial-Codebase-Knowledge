import os
import logging
import json
from datetime import datetime

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
)

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"


# By default, we Google Gemini 2.5 pro, as it shows great performance for code understanding
def call_llm(prompt: str, use_cache: bool = True) -> str:
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")

    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except:
                logger.warning(f"Failed to load cache, starting with empty cache")

        # Return from cache if exists
        if prompt in cache:
            logger.info(f"RESPONSE: {cache[prompt]}")
            return cache[prompt]

    # # Call the LLM if not in cache or cache disabled
    # client = genai.Client(
    #     vertexai=True,
    #     # TODO: change to your own project id and location
    #     project=os.getenv("GEMINI_PROJECT_ID", "your-project-id"),
    #     location=os.getenv("GEMINI_LOCATION", "us-central1")
    # )

    ######## For Gemini ########
    # You can comment the previous line and use the AI Studio key instead:
    # from google import genai
    # client = genai.Client(
    #     api_key=os.getenv("GEMINI_API_KEY", "your-api-key"),
    # )
    # model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    # # model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    # response = client.models.generate_content(model=model, contents=[prompt])
    # response_text = response.text


    # ######## For ChatGPT ########
    # from openai import OpenAI
    # client = OpenAI(api_key="your-api-key")
    # model = os.getenv("OPENAI_MODEL", "gpt-4o")
    # # response = client.responses.create(model="gpt-4o-mini", input=prompt, store=True)
    # # response_text = response.output_text
    # 
    # # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
    # estimated_tokens = len(prompt) // 4
    # print(f"Estimated prompt tokens: {estimated_tokens:,}")
    # 
    # if estimated_tokens > 50000:  # Conservative limit for rate limiting
    #     print("WARNING: Prompt may be too large. Consider using --max-size with smaller value.")
    # 
    # response = client.chat.completions.create(
    #     model=model,
    #     messages=[{"role": "user", "content": prompt}],
    #     max_tokens=50000
    # )
    # response_text = response.choices[0].message.content


    ######## For Anthropic Account API ########
    # from anthropic import Anthropic
    # client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", "your-api-key"))
    # response = client.messages.create(
    #     model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
    #     max_tokens=8192,
    #     messages=[
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # response_text = response.content[0].text


    ######## For Deepseek ########
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY", "your-api-key"),
        base_url="https://api.deepseek.com"
    )
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8192
    )
    response_text = response.choices[0].message.content



    # Log the response
    logger.info(f"RESPONSE: {response_text}")

    # Update cache if enabled
    if use_cache:
        # Load cache again to avoid overwrites
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except:
                pass

        # Add to cache and save
        cache[prompt] = response_text
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    return response_text


# # Use Azure OpenAI
# def call_llm(prompt, use_cache: bool = True):
#     from openai import AzureOpenAI

#     endpoint = "https://<azure openai name>.openai.azure.com/"
#     deployment = "<deployment name>"

#     subscription_key = "<azure openai key>"
#     api_version = "<api version>"

#     client = AzureOpenAI(
#         api_version=api_version,
#         azure_endpoint=endpoint,
#         api_key=subscription_key,
#     )

#     r = client.chat.completions.create(
#         model=deployment,
#         messages=[{"role": "user", "content": prompt}],
#         response_format={
#             "type": "text"
#         },
#         max_completion_tokens=40000,
#         reasoning_effort="medium",
#         store=False
#     )
#     return r.choices[0].message.content

# # Use Anthropic Claude 3.7 Sonnet Extended Thinking
# def call_llm(prompt, use_cache: bool = True):
#     from anthropic import Anthropic
#     client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key"))
#     response = client.messages.create(
#         model="claude-3-7-sonnet-20250219",
#         max_tokens=21000,
#         thinking={
#             "type": "enabled",
#             "budget_tokens": 20000
#         },
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response.content[1].text

# # Use OpenAI o1
# def call_llm(prompt, use_cache: bool = True):
#     from openai import OpenAI
#     client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
#     r = client.chat.completions.create(
#         model="o1",
#         messages=[{"role": "user", "content": prompt}],
#         response_format={
#             "type": "text"
#         },
#         reasoning_effort="medium",
#         store=False
#     )
#     return r.choices[0].message.content

# Use OpenRouter API
# def call_llm(prompt: str, use_cache: bool = True) -> str:
#     import requests
#     # Log the prompt
#     logger.info(f"PROMPT: {prompt}")

#     # Check cache if enabled
#     if use_cache:
#         # Load cache from disk
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 logger.warning(f"Failed to load cache, starting with empty cache")

#         # Return from cache if exists
#         if prompt in cache:
#             logger.info(f"RESPONSE: {cache[prompt]}")
#             return cache[prompt]

#     # OpenRouter API configuration
#     api_key = os.getenv("OPENROUTER_API_KEY", "")
#     model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#     }

#     data = {
#         "model": model,
#         "messages": [{"role": "user", "content": prompt}]
#     }

#     response = requests.post(
#         "https://openrouter.ai/api/v1/chat/completions",
#         headers=headers,
#         json=data
#     )

#     if response.status_code != 200:
#         error_msg = f"OpenRouter API call failed with status {response.status_code}: {response.text}"
#         logger.error(error_msg)
#         raise Exception(error_msg)
#     try:
#         response_text = response.json()["choices"][0]["message"]["content"]
#     except Exception as e:
#         error_msg = f"Failed to parse OpenRouter response: {e}; Response: {response.text}"
#         logger.error(error_msg)        
#         raise Exception(error_msg)
    

#     # Log the response
#     logger.info(f"RESPONSE: {response_text}")

#     # Update cache if enabled
#     if use_cache:
#         # Load cache again to avoid overwrites
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 pass

#         # Add to cache and save
#         cache[prompt] = response_text
#         try:
#             with open(cache_file, "w", encoding="utf-8") as f:
#                 json.dump(cache, f)
#         except Exception as e:
#             logger.error(f"Failed to save cache: {e}")

#     return response_text

def safe_print(text):
    """Print text with proper Unicode handling for Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: encode to ASCII with error handling for Windows console
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text)

if __name__ == "__main__":
    test_prompt = "Hello, how are you? (Please respond in plain text without emojis.)"

    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    safe_print(f"Response: {response1}")
