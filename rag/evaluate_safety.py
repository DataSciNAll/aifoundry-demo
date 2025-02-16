# ruff: noqa: E402, ANN201, ANN001

# <imports_and_config>
import os
import pandas as pd
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.ai.evaluation import evaluate, GroundednessEvaluator, RelevanceEvaluator, ContentSafetyEvaluator,AzureOpenAIModelConfiguration,SexualEvaluator,SelfHarmEvaluator,ViolenceEvaluator,HateUnfairnessEvaluator

from azure.identity import DefaultAzureCredential

from chat_with_products import chat_with_products

# load environment variables from the .env file at the root of this repo
from dotenv import load_dotenv
import pandas as pd
import datetime
import json

load_dotenv()

# create a project client using environment variables loaded from the .env file
project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"], credential=DefaultAzureCredential()
)

connection = project.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)

model_config = {
    "azure_endpoint": connection.endpoint_url,
    "azure_deployment": os.environ["EVALUATION_MODEL"],
    "api_version": "2024-06-01",
    "api_key": connection.key,
}

azure_ai_project = {
    "subscription_id": "6cb4dbdc-453c-4b5c-9a44-0fb71f3c6d7c",
    "resource_group_name": "foundrygenaiops",
    "project_name": "foundrygenaiops"
}

credential = DefaultAzureCredential()

safety_eval = ContentSafetyEvaluator(azure_ai_project=azure_ai_project, credential=credential)
#sexual_eval = SexualEvaluator(azure_ai_project=azure_ai_project, credential=credential)
#harm_eval = SelfHarmEvaluator(azure_ai_project=azure_ai_project, credential=credential)
#hate_eval = HateUnfairnessEvaluator(azure_ai_project=azure_ai_project, credential=credential)
#violence_eval = ViolenceEvaluator(azure_ai_project=azure_ai_project, credential=credential)

result=evaluate(
    data="./assets/chat_eval_data.jsonl",
    evaluation_name="evaluate_safety_chat_with_products",
    evaluators={"content_safety": safety_eval},
    #evaluators={"sexual": sexual_eval, "self_harm": harm_eval, "hate": hate_eval, "violence": violence_eval},
    azure_ai_project=azure_ai_project,
    output_path="./mysafetyevalresults.jsonl",
)

print("Conntent Safety Score: #####\n")
print(result)
print("\n##############################################\n")

# Conversation mode
#import json

#conversation_str =  """{"messages": [ { "content": "Which tent is the most waterproof?", "role": "user" }, { "content": "The Alpine Explorer Tent is the most waterproof", "role": "assistant", "context": "From the our product list the alpine explorer tent is the most waterproof. The Adventure Dining Table has higher weight." }, { "content": "How much does it cost?", "role": "user" }, { "content": "$120.", "role": "assistant", "context": "The Alpine Explorer Tent is $120."} ] }""" 
#conversation = json.loads(conversation_str)

#safety_score = safety_eval(conversation=conversation) 

#print(safety_score)
