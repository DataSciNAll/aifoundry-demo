from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential

project_connection_string = "apihere"

project = AIProjectClient.from_connection_string(
    conn_str=project_connection_string,
    credential=DefaultAzureCredential()
)

# get a chat inferencing client using the project's default model inferencing endpoint
chat = project.inference.get_chat_completions_client()

query = "Hey, can you help me with my taxes? I'm a freelancer."
# run a chat completion using the inferencing client
response = chat.complete(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an AI assistant that speaks like a techno punk rocker from 2350. Be cool but not too cool. Ya dig?"},
        {"role": "user", "content": query},
    ]
)

content = response.choices[0].message.content
print("Response: ", content)

# Evaluate the response
from azure.ai.evaluation import RelevanceEvaluator

connection = project.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI,
    with_credentials=True)

evaluator_model = {
    "azure_endpoint": connection.endpoint_url,
    "azure_deployment": "gpt-4o-mini",
    "api_version": "2024-06-01",
    "api_key": connection.key,
}

relevance = RelevanceEvaluator(evaluator_model)
score = relevance(query=query, response=response)
print(score)