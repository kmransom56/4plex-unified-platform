from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import json

# 1. Configure LLM (Replace with your actual configuration details)
# Ensure you have your API key and model details configured correctly.
# You can either define it directly here or use config_list_from_json if you have a config file.
# Example using direct configuration:
llm_config = {
    "config_list": [
        {
            "model": "gpt-4-turbo-preview",  # Replace with your desired model
            "api_key": "your-openai-api-key-here",  # Replace with your actual API key or use environment variable
            # Add other parameters like base_url for Azure OpenAI if needed
        }
    ],
    "seed": 42,
}

# If you have an OAI_CONFIG_LIST.json file:
# config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
# llm_config = {"config_list": config_list, "seed": 42}

# 2. Define the Assistant Agent (GrantResearcher - our "Magentic One")
grant_researcher = AssistantAgent(
    name="GrantResearcher",
    llm_config=llm_config,
    system_message="""You are a helpful AI research assistant specializing in finding grant opportunities in Brookhaven, Georgia (DeKalb County) for renovating small multifamily properties and adopting clean energy. You will research provided websites, extract relevant information (grant names, descriptions, eligibility, funding, deadlines, contacts), and provide a well-organized summary with source URLs.""",
    human_input_mode="NEVER",  # Set to "ALWAYS" if you want to manually approve each step
)

# 3. Define the User Proxy Agent
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",  # The user initiates and the agent runs automatically
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},  # Optional: for code execution if needed
)

# 4. Define the list of URLs to research
urls_to_research = [
    "https://www.brookhavenga.gov/1304/Economic-Development",
    "https://www.dekalbcountyga.gov/",
    "https://www.dekalbcountyga.gov/community-development/community-development-block-grant-cdbg",
    "https://www.dekalbcountyga.gov/sites/default/files/users/user2778/FINAL%202024-2028%20Consolidated%20Plan%20Including%20the%202024%20Annual%20Action%20Plan.pdf",
    "https://www.dekalbcountyga.gov/human-development/grants-and-administration",
    "https://www.decidedekalb.com/grow-your-business/",
    "https://www.energy.gov/",
    "https://www.epa.gov/energy/",
    "https://www.georgiapower.com/residential/green-energy/incentives.html",
    "https://www.gefa.org/",
    "https://www.dsireusa.org/",
    "https://gefa.georgia.gov/energy-programs/home-energy-rebate-programs",
    "https://www.rd.usda.gov/programs-services/energy-programs/rural-energy-america-program-renewable-energy-systems-energy-efficiency-improvement-guaranteed-loans-13"
]

# 5. Initial message to trigger the research
initial_message = f"Research the following websites for grant opportunities in Brookhaven, Georgia (DeKalb County) for renovating small multifamily properties and adopting clean energy: {urls_to_research}"

# 6. Initiate the chat (to test the agents)
user_proxy.initiate_chat(
    grant_researcher,
    message=initial_message
)

# 7. Export Agent Configurations to JSON (for AutoGen Studio)
grant_researcher_config_for_export = grant_researcher.config
user_proxy_config_for_export = user_proxy.config

agent_configs_for_studio = {
    "grant_researcher": grant_researcher_config_for_export,
    "user_proxy": user_proxy_config_for_export,
}

json_output = json.dumps(agent_configs_for_studio, indent=4)

print("\n--- JSON Configuration for AutoGen Studio ---")
print(json_output)

# You can copy the JSON output above and paste it into the JSON editor
# when creating or editing an agent in AutoGen Studio.