from rhubarb import Entities

model_params = {
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0", #anthropic.claude-3-opus-20240229-v1:0', 'anthropic.claude-3-sonnet-20240229-v1:0', 'anthropic.claude-3-haiku-20240307-v1:0' or 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    "region": "us-east-1",
    "max_tokens": 512,
    "temperature": 0.5,
    "top_p": 0.9,
    # "ner_entities": [
    #     Entities.PERSON,       
    #     Entities.DATE_TIME,    
    #     Entities.ADDRESS,      
    #     Entities.CREDIT_DEBIT_NUMBER,       
    #     Entities.TITLE,         
    #     Entities.QUANTITY
    # ]
}
