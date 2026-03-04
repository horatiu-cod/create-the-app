You are a helpful assistant.
Read the project.md file.
You have to create a multi-agent system, based on the project.md file, that processes PDF documents uploaded by the user, verifies the accuracy of the information, and generates a report. In the process of the Agent, it uses tools, mcp and skills. 


You have to generate proper scripts for each agent, tools, mcp ( if needed) and skills. 
Generate proper skills for each agent.
Generate required tools for each agent.
The tools, mcp and skills will be used by the agents.

For LLM API calls create proper prompts and instructions for each agent task. Be aware that the calls can fail due to external factors: the API might be down, you might hit rate limits, or your key might be invalid. Sending fewer tokens means faster responses and lower cost. 
You would want smarter chunking that splits the text on sentence or paragraph boundaries rather than a raw character count. Temperature 0.3 makes the output more focused and deterministic, which is ideal for summarization. The retry logic catches RateLimitError specifically and waits longer each time (5, 10, then 15 seconds) — this is called exponential backoff. Other API errors raise immediately because retrying them will not help. If the input is empty or the API fails completely, the agent writes a fallback message instead of crashing, so the downstream agents can still run.

Write tests for each agent tools. 

Create a web interface for the user to upload the PDF documents and to view the results.

Bring adjustments and improvements to the project based on your experience and best practices.

Create a README.md file for the project, that will explain how to run the project.