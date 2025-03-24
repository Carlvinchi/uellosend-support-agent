
####
# Tools for the LLM to use in completing tasks
####
import os
from pydantic import EmailStr, validate_call
import requests
from dotenv import load_dotenv

load_dotenv()

CUSTOMER_URL = os.getenv("CUSTOMER_URL")
TRANSACTION_URL = os.getenv("TRANSACTION_URL")


@validate_call
def verify_customer_exist(customer_email: EmailStr)-> dict:
    """
    This function checks the database to see if a customer exists for the provided email address.
    :param customer_email: Valid email address of the customer
    :return: A dictionary with customer_id as the key, the value of customer_id is postive integer if the customer exists or Not Found if the customer does not exist.
    """
    # Prepare request parameters
    url = CUSTOMER_URL
    data = {'email': customer_email}
    header = {'Content-Type': 'application/json'}

    response = requests.post(url=url, headers=header, json=data)
    res = response.json()

    
    if  int(res["code"]) == 404:
        return {"customer_id": "Not Found"}
    
    elif int(res["code"]) == 200:
        return {"customer_id": res["result"]}
    

@validate_call
def fix_credit_topup_issue(customer_id: int, transaction_id: str) -> str:
    """
    This function resolves credit top up issues by verifying transactions and automatically crediting customer account with the correct amount.
    :param customer_id: The ID of the customer making the request
    :param transaction_id: The ID of the transaction to be used for crediting customer account.
    :return: Status of the request eg Resolved, Not Resolved, No Resolution Required.
    """
    url = TRANSACTION_URL
    data = {'user_id': customer_id, 'transaction_id': transaction_id}
    header = {'Content-Type': 'application/json'}

    response = requests.post(url=url, headers=header, json=data)

    res = response.json()

    if int(res["code"]) == 502:
        return "Not Resolved: Payment Gateway Error"
    elif int(res["code"]) == 402:
        return f"No Resolution Required: The transaction with ID - {transaction_id} was not completed by the customer"
    elif int(res["code"]) == 406:
        return f"No Resolution Required: The transaction with ID - {transaction_id} cannot be found or has already been credited to the customer"
    elif int(res["code"]) == 200:
        return f"Resolved: The transaction with ID - {transaction_id} has been credited to the customer successfully, customer should check UelloSend Dashboard"


#print(verify_transaction(675, "LVC3V1VTR08H"))
