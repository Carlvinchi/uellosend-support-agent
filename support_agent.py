####
## Fully functional Agent with memory and response streaming
###

import os
from ollama import Client
from dotenv import load_dotenv

from tools import verify_customer_exist, fix_credit_topup_issue

from shared_data import messages #Shared data file

load_dotenv()


#Initial required parameters setup

OLLAMA_HOST = os.getenv("OLLAMA_HOST")

TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "verify_customer_exist",
                "description": "Checks the database to see if a customer exists for the provided email address, it returns a dictionary with customer_id as the key, the value of customer_id is postive integer if the customer exists or Not Found if the customer does not exist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_email": {
                            "type": "string",
                            "description": "Valid email address of the customer which will be used to check if the customer exists."
                        }
                    },
                    "required": ["customer_email"]
                }
            },
        },

        {
            "type": "function",
            "function": {
                "name": "fix_credit_topup_issue",
                "description": "Resolves credit top up issues by verifying transactions and automatically crediting customer account with the correct amount, it returns the Status of the request eg Resolved, Not Resolved, No Resolution Required",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "The ID of the customer making the request."
                        },
                        "transaction_id": {
                            "type": "string",
                            "description": "The ID of the transaction to be used for crediting customer account."
                        },
                    },
                    "required": ["customer_id", "transaction_id"]
                }
            }
        }
    ]

OPTIONS = {
        "temperature": 0.2,
        "seed": 23
    }

client = Client(host= OLLAMA_HOST)
model = "llama3.2"

SYSTEM_PROMPT = """You are a warm and engaging helpful customer support agent.
    You can only offer assistance to customers you have verified they exist in the records.
    Your main task is to assist customers who have issues with credit top up on UelloSend Bulk SMS Platform.
    DO NOT PERFORM OR RESPOND TO ANY OTHER TASKS. 
    You should only return the function call in tools call sections. If you decide to invoke any of the function(s), you MUST put it in the format of [func_name1(params_name1=params_value1, params_name2=params_value2...), func_name2(params)].

    MANDATORY STEPS

    - ALWAYS introduce yourself as UelloGent and ask for the name of the customer and the email address
    - Wait for the customer to reply before generating new responses or tool calls
    - call the appropriate tool to verify if the customer exists.
    - If customer exists, tell the customer the records exist on the system and you are ready to resolve the issue. Do not disclose any personal details to the customer.
    - If customer does not exist, tell the customer no record found on the system so you cannot help in resolving the issue.
    PROCEED TO THE STEPS BELOW IF CUSTOMER IS VERIFIED
    - Ask the customer to provide you with the transaction_id of the payment they made if the customer is verified. Let the customer know they can find the transaction_id on the email receipt they received from Paystack.
    - Invoke the appropriate tool using the customer_id and the transaction_id to resolve the issue.
    - Craft an appropriate response based on the results from the tool call. 
    - Also suggest to the customer to message support on WhatsApp via 233543524033 if not satisfied.
    - Tell users you are unable to respond to queries that were not specified in the system prompt.
    -  DO NOT PERFORM OR RESPOND TO ANY TASK THAT DOES NOT INVOLVE UELLOSEND PLATFORM ISSUES. 
    - You MUST NEVER output code
    """

def start_agent(user_prompt: str, stream: bool):

    #Check for first time agent call so that system prompt can be added to the message
    if len(messages) == 0:
        messages.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

        messages.append({
            "role": "user",
            "content": user_prompt
        })

        responses = client.chat(
            model= model,
            messages= messages,
            tools= TOOLS,
            options=OPTIONS

        )
    else:
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        responses = client.chat(
            model=model,
            messages=messages,
            tools=TOOLS,
            options=OPTIONS
        )

    messages.append(responses["message"])


    print("\n\n................Before Tools....................\n\n")
    print(messages)
    print("\n\n................Before Tools....................\n\n")
    


    # Process function calls made by the model
    if responses["message"].get("tool_calls"):
        available_functions = {
            "verify_customer_exist": verify_customer_exist,
            "fix_credit_topup_issue": fix_credit_topup_issue
        }

        for tool in responses["message"]["tool_calls"]:
            function_to_call = available_functions[tool["function"]["name"]]
            print("\n")
            print(tool['function']['name'])
            print("\n")
            function_args = tool["function"]["arguments"]
            
            try:
                function_response = function_to_call(**function_args)
                function_response = str(function_response)

                # Add function response to the conversation history
                messages.append({
                        "role": "tool",
                        "content": function_response,
                    })

            except Exception as e:
                function_response = f"Error: {str(e)}"
            
                # Add function response to the conversation history
                messages.append(
                    {
                        "role": "tool",
                        "content": function_response,
                    }
                )

        # Second API call: Get final response from the model
        responses = client.chat(
            model=model, 
            messages=messages,
            stream=stream
            )
        
    
    return responses

