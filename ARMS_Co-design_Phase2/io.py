import json
import pandas as pd

from vanna import Agent, AgentConfig
from vanna.integrations.ollama import OllamaLlmService
from vanna.integrations.chromadb import ChromaAgentMemory
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.capabilities.agent_memory import ToolMemory
from vanna.core.tool import ToolContext
from vanna.core.system_prompt import SystemPromptBuilder

from custom_tools import CoDesignInferenceTool

llm = OllamaLlmService(
    model = "llama3.1",
    host = "http://localhost:11434"
)

db_tool = CoDesignInferenceTool(
    db_path = 'resources/engineering_standards.db'
)

agent_memory = ChromaAgentMemory(
    collection_name = "vannaTransform",
    persist_directory = "chromafolder"
)

class CustomSystemPromptBuilder(SystemPromptBuilder):
    async def build_system_prompt(self, context, tools):
        prompt = """You are an expert mechanical engineering SQL assistant.
        You are querying an SQLite database with the following schema:

        CREATE TABLE engineering_fits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            standard TEXT,
            fit_type TEXT,
            basic_size REAL,
            fit_category TEXT,
            hole_class TEXT,
            shaft_class TEXT,
            hole_max REAL,
            shaft_max REAL,
            fit_max REAL,
            hole_min REAL,
            shaft_min REAL,
            fit_min REAL
        );

        Based on this schema, write a valid SQLite query to answer the user's question.
        """
        
        if tools:
            prompt += "\n\nYou have access to the following tools:\n"
            for tool in tools:
                prompt += f"\n### {tool.name}\n{tool.description}\nParameters: {tool.parameters}\n"
                
        return prompt

class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_cookie('vanna_email') or 'guest@example.com'
        group = 'admin' if user_email == 'admin@example.com' else 'user'
        return User(id=user_email, email=user_email, group_memberships=[group])
user_resolver = SimpleUserResolver()

tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=['admin', 'user'])

agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    agent_memory=agent_memory,
    user_resolver=user_resolver,
    system_prompt_builder=CustomSystemPromptBuilder(),
    config=AgentConfig(stream_responses=False)
)

async def train_database():
    print("Training Agent on database schema...")

    training_examples = [
        ToolMemory(
            question="I have a cylinder of diameter 1 and I want it to fit loosely running",
            tool_name="codesign_inference_tool", 
            args={
                "sql_query": "SELECT * FROM engineering_fits WHERE basic_size = 1.0 AND fit_category LIKE '%Loose%'"
            }
        ),
        ToolMemory(
            question="What is the tolerance for an h11 shaft?",
            tool_name="codesign_inference_tool",
            args={
                "sql_query": "SELECT * FROM engineering_fits WHERE shaft_class = 'h11'"
            }
        )
    ]
    
    admin_user = User(id="local_tester", username="tester", group_memberships=['admin'])
    
    for example in training_examples:
        await agent.agent_memory.save_tool_usage(
            question=example.question,
            tool_name=example.tool_name,
            args=example.args,
            context=ToolContext(
                user=admin_user,
                conversation_id="manual_training_run",
                request_id="manual_training_run",
                agent_memory=agent_memory
            ),
            success=True
        )
    print("Training complete! Schema saved to ChromaDB.")

async def run_JSONpipeline():
    try:
        with open('color_output.json', 'r') as file:
            input_data = json.load(file)
            raw_prompt = input_data.get("prompt")
            user_prompt = f"You are an expert mechanical engineering database and co-design assistant. A user is asking: '{raw_prompt}'. For now, query the database to find the exact tolerance records they need."
    except FileNotFoundError:
        print("Could not find color_output.json")
        return

    print(f"Asking Agent: {user_prompt}")

    local_user = User(id="local_tester", username="tester", group_memberships=['admin'])
    conversation_id = "local-json-test"

    final_result_text = ""

    try:
        async for component in agent.send_message(
            message=user_prompt,
            conversation_id=conversation_id,
            request_context=RequestContext()
        ):

            if hasattr(component, "simple_component") and component.simple_component:
                if hasattr(component.simple_component, "text") and component.simple_component.text:

                    final_result_text += component.simple_component.text + "\n"

        if db_tool.last_json_result:
            final_data_payload = json.loads(db_tool.last_json_result)
        else:
            final_data_payload = final_result_text.strip()

        output_data = {
            "original_prompt": user_prompt,
            "final_result": final_data_payload
        }

        with open('output.json', 'w') as file:
            json.dump(output_data, file, indent=4)
            
        print("Successfully generated output.json with RAW data!")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        error_data = {"prompt": user_prompt, "error": str(e)}
        with open('output.json', 'w') as file:
            json.dump(error_data, file, indent=4)

if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--train":
        asyncio.run(train_database())
    else:
        asyncio.run(run_JSONpipeline())