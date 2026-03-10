# Evalbot MCP Server

MCP Server for the Evalbot

## Tools

hint: you can find all key definitions [here](https://bytedance.larkoffice.com/sheets/Ex0IsHwlLhqxgStXRbLcgTC6nDc)

1. `data_generation`
   - Generate Model Evaluation Data
   - Required inputs:
     - `generate_type` (str): The type for generating data, only support `hot_topic` currently.
     - `params` (dict[str, str]): The params used to generate data. Support keys:

           "top_n": target the top n hot topic.
   - Returns: Optional[str | List[str]]: The error info or the generated data list

2. `model_evaluation`
   - Evaluate Model
   - Required inputs:
     - `evaluate_type` (str): The type for evaluating model. Supported values:
                             
           "knowledge-instruction_following": Requires keys location, scene, question, reply.
           "knowledge-scalable-comprehensive_key_points": Requires keys scene, question, reply.
           "knowledge-authentic_and_accurate-general": Requires keys base_time, question, reply.
           "knowledge-richness": Requires keys query, reply.
           "knowledge-gsb-compare": Requires keys query, domain, reply_a, reply_b, evaluation_criteria.
       - `params` (dict[str, str]): Dictionary of  parameters for the evaluation. The allowed keys depend on `evaluate_type`:
                                 
             location: The geographical location entered by the user, such as "Shenzhen xx".
             scene: The scenario to which the user's input query belongs, such as "Knowledge Question - Local Life".
             question: The user input.
             query: The user input.
             reply: The reply of the user input, such as "It's 28 degrees today...".
             base_time: Define the test verification time for the evaluation task, such as "2025-10-11".
             domain: The domain to which the user's input query belongs, such as "education".
             reply_a: Multiple replies input by the user.
             reply_b: Multiple replies input by the user.
             evaluation_criteria: 
   - Returns: Optional[str | AbilityTriggerRespData]: The error info or the result for the model evaluation.

## Setup

1. Get User-Access-Token
   
    Check out [website](https://evalbot.bytedance.com/) to fetch the token

2. Run the server

    There are two ways to run the MCP Evalbot server:

    ### Option 1: Direct Command
    Run the server directly using:
    ```bash
    uvx --from git+https://github.com/mstf-zyx/mcp@main#subdirectory=evalbot \
        mcp-server-evalbot \
        --transport streamable-http \
        --token User-Access-Token
    ```

    ### Option 2: Claude Desktop Integration
    1. Visit the [Claude Desktop Quick Start Guide](https://modelcontextprotocol.io/quickstart/user)
    2. Create or update your `mcp.json` configuration file:
    ```json
    {
      "mcpServers": {
        "evalbot": {
          "command": "uvx",
          "args": [
            "--from",
            "git+https://github.com/mstf-zyx/mcp@main#subdirectory=evalbot",
            "mcp-server-evalbot",
            "--transport",
            "streamable-http",
            "--token",
            "User-Access-Token"
          ]
        }
      }
    }
    ```

    > **Note**: Replace `User-Access-Token` with the actual token gotten from step 1.
