import os
from typing_extensions import Any
from sqlite3 import Connection

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

from .prompts import DB_AGENT_PROMPT


class AgentDeps(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    conn: Connection


def create_db_agent() -> Agent[AgentDeps]:

    azure_model = OpenAIChatModel(
        model_name='gpt-4.1-nano',
        provider=AzureProvider(
            api_version='2024-12-01-preview',
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
    )

    db_agent = Agent(
        model=azure_model,
        instructions=DB_AGENT_PROMPT,
        deps_type=AgentDeps,
        output_type=str,
    )

    @db_agent.tool()
    def list_tables(ctx: RunContext[AgentDeps]) -> list[str]:
        """
        List all tables in the sqlite database.
        Returns a list with the names of all tables.
        """
        print("🔧 [TOOL] list_tables")

        cursor = ctx.deps.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_raw = cursor.fetchall()

        tables = [t[0] for t in tables_raw]
        return tables

    @db_agent.tool()
    def describe_table(ctx: RunContext[AgentDeps], table_name: str) -> list[Any]:
        """
        Describe the schema of a specific table in the database.
        Returns information about the columns including name, type, and constraints.
        """
        print("🔧 [TOOL] describe_table")

        cursor = ctx.deps.conn.cursor()
        cursor.execute(f'PRAGMA table_info({table_name});')

        table_info = cursor.fetchall()
        return table_info

    @db_agent.tool()
    def execute_query(ctx: RunContext[AgentDeps], sql_query: str):
        """
        Execute a SQL query against the database.
        Returns the results of the query execution.
        """
        print(f"🔧 [TOOL] execute_query -> {sql_query}")
        
        cursor = ctx.deps.conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results


    return db_agent
