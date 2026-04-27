import sqlite3
import pandas as pd
from typing import List, Type
from vanna.core.tool import Tool, ToolContext, ToolResult
from pydantic import BaseModel, Field

class InferenceArgs(BaseModel):
    sql_query: str = Field(..., description="The raw, valid SQLite SELECT query you want to execute.")

class CoDesignInferenceTool(Tool[InferenceArgs]):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.last_json_result = None

    @property
    def name(self) -> str:
        return "codesign_inference_tool"
    
    @property
    def description(self) -> str:
        return (
            "Executes a SQL query against the database to retrieve records. "
            "You MUST provide the exact SQL query string using the 'sql_query' parameter. "
            "Do not pass database names or other parameters."
        )
    
    @property
    def access_groups(self) -> List[str]:
        return ['user', 'admin']  # Restricted access
    
    def get_args_schema(self) -> Type[InferenceArgs]:
        return InferenceArgs
    
    async def execute(self, context: ToolContext, args: InferenceArgs) -> ToolResult:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(args.sql_query, conn)
            conn.close()
            
            json_output = df.to_json(orient="records")
            
            # Save the perfect JSON string to the tool's memory
            self.last_json_result = json_output 
            
            return ToolResult(
                success=True, 
                result_for_llm=json_output
            )
            
        except Exception as e:
            # If it fails, make sure we clear the last result
            self.last_json_result = None 
            return ToolResult(
                success=False,
                result_for_llm=f"The SQL query failed with error: {str(e)}",
                error=str(e)
            )