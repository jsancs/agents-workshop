import sqlite3
from dotenv import load_dotenv

from src.db_agent import create_db_agent, AgentDeps


load_dotenv()

def main():
    db_conn = sqlite3.connect('data/movie.sqlite', check_same_thread=False)
    agent_deps = AgentDeps(conn=db_conn)
    db_agent = create_db_agent()
    
    message_history = []

    try:
        while True:
            user_input = input("> ").strip()
            if user_input.lower() in ['exit', 'quit', 'salir']:
                break
            
            if not user_input:
                continue
            
            response = db_agent.run_sync(user_input, deps=agent_deps, message_history=message_history)
            print(response.output)
            print()
            
            message_history = response.all_messages()
    
    finally:
        db_conn.close()


if __name__ == "__main__":
    main()
