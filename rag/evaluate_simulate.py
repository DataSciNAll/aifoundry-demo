# ruff: noqa
# File is WIP

from chat_with_products import chat_with_products
import os

from azure.ai.evaluation.simulator import Simulator
from azure.ai.evaluation import evaluate, GroundednessEvaluator
from typing import Any, Dict, List, Optional
import asyncio
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential

from dotenv import load_dotenv

from pathlib import Path
import json

load_dotenv()

project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"], credential=DefaultAzureCredential()
)

connection = project.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI, with_credentials=True)

evaluator_model = {
    "azure_endpoint": connection.endpoint_url,
    "azure_deployment": os.environ["EVALUATION_MODEL"],
    "api_version": "2024-06-01",
    "api_key": connection.key,
}


async def custom_simulator_callback(
    messages: List[Dict],
    stream: bool = False,
    session_state: Any = None,
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    # call your endpoint or ai application here
    actual_messages = messages["messages"]
    print(f"\n🗨️  {actual_messages[-1]['content']}")
    response = chat_with_products(actual_messages)
    message = {
        "role": "assistant",
        "content": response["message"]["content"],
        "context": response["context"]["grounding_data"],
    }
    actual_messages.append(message)
    return {"messages": actual_messages, "stream": stream, "session_state": session_state, "context": context}


async def custom_simulator_raw_conversation_starter():
    outputs = await custom_simulator(
        target=custom_simulator_callback,
        conversation_turns=[
            [
                "I need a new tent, what would you recommend?",
            ],
        ],
        max_conversation_turns=3,
    )
    
    output_file = Path("simdata.json")
    with output_file.open("a") as f:
        json.dump(outputs,f)
    
    groundedness = GroundednessEvaluator(model_config=evaluator_model)
    result = groundedness(conversation=outputs[0])
    with output_file.open("a") as f:
        json.dump(result,f )
    print(result)

if __name__ == "__main__":
    custom_simulator = Simulator(model_config=evaluator_model)

    async def main():
        await custom_simulator_raw_conversation_starter()

    asyncio.run(main())