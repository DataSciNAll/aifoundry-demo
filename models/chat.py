from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_connection_string = "apihere"

project = AIProjectClient.from_connection_string(
    conn_str=project_connection_string,
    credential=DefaultAzureCredential()
)

# get a chat inferencing client using the project's default model inferencing endpoint
chat = project.inference.get_chat_completions_client()

# run a chat completion using the inferencing client
response = chat.complete(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an AI assistant that speaks like a techno punk rocker from 2350. Be cool but not too cool. Ya dig?"},
        {"role": "user", "content": "Hey, can you help me with my taxes? I'm a freelancer."},
    ],
    stream=True
)

# print chunks as they become available
print("🗨️  Response:")
for event in response:
    if event.choices:
        print(event.choices[0].delta.content, end="", flush=True)