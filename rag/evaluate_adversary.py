# File is WIP
# Need to fix Evaluate function

from chat_with_products import chat_with_products
import os

from azure.ai.evaluation.simulator import Simulator, AdversarialSimulator, AdversarialScenario
from azure.ai.evaluation import evaluate, GroundednessEvaluator, SexualEvaluator, SelfHarmEvaluator, HateUnfairnessEvaluator, ViolenceEvaluator
from typing import Any, Dict, List, Optional
import asyncio
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from datetime import datetime

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
    "subscription_id": "6cb4dbdc-453c-4b5c-9a44-0fb71f3c6d7c",
    "resource_group_name": "foundrygenaiops",
    "project_name": "foundrygenaiops"
}

credential = DefaultAzureCredential()

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
        "context": {},
    }
    actual_messages.append(message)
    return {"messages": actual_messages, "stream": stream, "session_state": session_state, "context": context}


async def custom_simulator_raw_conversation_starter():
    outputs = await custom_simulator(
        scenario=scenario,
        target=custom_simulator_callback,
        conversation_turns=[
            [
                "I need a new tent, what would you recommend"
            ],
        ],
        max_conversation_turns=1,
        Max_simulation_results=3,
        jailbreak=False
    )

    output_file = Path("./advdata.jsonl")
    with output_file.open("a") as f:
        json.dump(outputs,f)

    sexual_evaluator = SexualEvaluator(azure_ai_project=evaluator_model,credential=credential)
    self_harm_evaluator = SelfHarmEvaluator(azure_ai_project=evaluator_model,credential=credential)
    hate_unfairness_evaluator = HateUnfairnessEvaluator(azure_ai_project=evaluator_model,credential=credential)
    violence_evaluator = ViolenceEvaluator(azure_ai_project=evaluator_model,credential=credential)
    
    adv_eval_result = evaluate(
        evaluation_name=f"Adversarial Tests",
        data=output_file,
        evaluators={
            "sexual": sexual_evaluator,
            "self_harm": self_harm_evaluator,
            "hate_unfairness": hate_unfairness_evaluator,
            "violence": violence_evaluator
            },
        azure_ai_project=evaluator_model,
        output_path="./adversarial_test.json"
    )

if __name__ == "__main__":
    custom_simulator = Simulator(model_config=evaluator_model)
    scenario = AdversarialScenario.ADVERSARIAL_QA

    async def main():
        await custom_simulator_raw_conversation_starter()

    asyncio.run(main())