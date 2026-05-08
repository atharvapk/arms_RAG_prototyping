import asyncio
from vanna.capabilities.agent_memory import ToolMemory
from vanna.core.tool import ToolContext
from vanna.core.user.models import User

from vanna import Agent, AgentConfig
from vanna.integrations.ollama import OllamaLlmService
from vanna.integrations.chromadb import ChromaAgentMemory
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext

from custom_tools import CoDesignInferenceTool

#DONT USE THIS, THIS IS FOR TESTING ONLY 

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
    config=AgentConfig(stream_responses=False)
)

async def train_golden_queries():
    print("Training Agent Memory with Golden Queries...")
    
    training_examples = [
        ToolMemory(
            question="I have a cylinder of diameter 1 and I want it to fit loosely running",
            tool_name="run_sql",
            args={
                "sql": """
                SELECT * FROM engineering_fits 
                WHERE basic_size = 1.0 
                AND fit_category = 'Loose Running'
                """
            }
        ),
        ToolMemory(
            question="What is the max hole size for a 1mm Free Running fit?",
            tool_name="run_sql",
            args={
                "sql": """
                SELECT hole_max 
                FROM engineering_fits 
                WHERE basic_size = 1.0 
                AND fit_category = 'Free Running'
                """
            }
        )
    ]
    
    your_user = User(id="admin", email="admin@example.com", group_memberships=["admin"])
    
    for example in training_examples:
        await agent.agent_memory.save_tool_usage(
            question=example.question,
            tool_name=example.tool_name,
            args=example.args,
            context=ToolContext(user=your_user),
            success=True
        )
    print("Training complete! ChromaDB now remembers these examples.")

asyncio.run(train_golden_queries())