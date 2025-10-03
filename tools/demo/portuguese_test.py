import improved_bilingual_agent as agent

agent.test_goal(
    agent.load_tools_from_directory("../../schema/examples"), "fazer um furo"
)
agent.test_goal(
    agent.load_tools_from_directory("../../schema/examples"), "preciso traduzir texto"
)
