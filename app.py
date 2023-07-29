import uvicorn

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from database import database
from models import TokenModel, ResponseModel, token_helper, Network
from process import processing_coin_info


app = FastAPI()

@app.post("/add_token", response_description="Add new token")
async def add_token(token_url:str, network:Network = Network.ETH):
    base_token_name, base_token_address, quote_token_name, quote_token_address, market_cap = processing_coin_info(token_url, network.value)
    if base_token_address is None:
        return ResponseModel(data=None,message="Insert failed. Please try again")
    else:
        token_dict = {
            "base_token_name": base_token_name,
            "base_token_address": base_token_address,
            "quote_token_name":quote_token_name,
            "quote_token_address":quote_token_address,
            "network": network.value,
            "market_cap":market_cap
        }
        token = TokenModel(**token_dict)
        token = jsonable_encoder(token)
        token = await database["tokens"].insert_one(token)
        new_token = await database["tokens"].find_one({"_id": token.inserted_id})
        return ResponseModel(data=token_helper(new_token),message="Insert successfully")
        

@app.get("/get_tokens", response_description="Get list tokens")
async def get_tokens():
    list_tokens_db = await database['tokens'].find().to_list(50)
    tokens = [token_helper(token) for token in list_tokens_db]
    return ResponseModel(data=tokens,message="Get list tokens successfully")
    

if __name__ == "__main__":
    uvicorn.run(app=app, host='0.0.0.0', port=8888)