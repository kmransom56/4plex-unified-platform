from autogen import AssistantAgent, UserProxyAgent
import json

# Configure LLM (replace with your actual configuration)
llm_config = {
    "config_list": [
        {
            "model": "gpt-4-turbo-preview",  # Example model - replace with your choice
            "api_key": "YOUR_OPENAI_API_KEY",  # Replace with your actual key if using OpenAI
            # Add other configuration parameters as needed (e.g., base_url for Azure OpenAI)
        }
    ],
    "seed": 42,
}

# Define the Assistant Agent (Magentic One) configuration as a dictionary
grant_researcher_config = {
    "name": "GrantResearcher",
    "llm_config": llm_config,
    "system_message": """You are a helpful AI research assistant specializing in finding grant opportunities.
Your goal is to research the provided websites and identify grants available in Brookhaven, Georgia (DeKalb County) for renovating small multifamily properties and for adopting clean energy during renovations.

You should carefully read the content of the web pages and extract relevant information such as:
- Grant names
- Brief descriptions of the grant programs
- Eligibility criteria (specifically for location and property type)
- Funding amounts or ranges
- Application deadlines (if available)
- Contact information or links for further details

You will be provided with a list of URLs to investigate. Please process each URL and summarize the findings related to the research goals. If a website does not contain relevant information, please state that.

Your final output should be a well-organized summary of potential grant opportunities, clearly indicating the source website for each grant.
""",
    "human_input_mode": "NEVER",
}

# Define the User Proxy Agent configuration as a dictionary
user_proxy_config = {
    "name": "User",
    "human_input_mode": "TERMINATE",
    "max_consecutive_auto_reply": 10,
    "code_execution_config": {"work_dir": "coding"},
}

# Create a dictionary containing the configurations of both agents
agent_configs = {
    "grant_researcher": grant_researcher_config,
    "user_proxy": user_proxy_config,
}

# Convert the dictionary to a JSON string
json_output = json.dumps(agent_configs, indent=4)

# Print the JSON output (you can then copy this to AutoGen Studio)
print(json_output)

# Optional: Save to a JSON file
# with open("autogen_agents.json", "w") as f:
#     f.write(json_output)