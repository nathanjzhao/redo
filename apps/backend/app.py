import stripe
from stripe.error import CardError, StripeError
from pydantic import BaseModel
import logging
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from backend.utils.auth import get_current_user
from backend.utils.db import ApiKey, User, get_db, Base, engine
from backend.utils.billing import stripe_charge
from backend.user_routes import router as user_router
import stripe

import secrets

# instantiate the API
app = FastAPI()
app.include_router(user_router)

stripe.api_key = 'your-stripe-secret-key'

origins = [
    "http://localhost:3000",  # Allow frontend origin during development
    # "https://your-production-frontend-url.com",  # Allow frontend origin in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    log.info('Initializing API ...')
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


class PaymentDetails(BaseModel):
    card_number: str
    exp_month: int
    exp_year: int
    cvc: str

class ForwardToGPTRequest(BaseModel):
    payload: dict
    api_key: str

@app.post("/forward_to_chatgpt")
async def forward_to_chatgpt(request: ForwardToGPTRequest):
    try:
        
        # stripe_charge()

        # Forward the request to ChatGPT
        response = requests.post(
            "https://api.openai.com/v1/engines/davinci-codex/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {request.api_key}",
            },
            json=request.payload,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to forward request to ChatGPT")

        return response.json()

    except (CardError, StripeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api_keys")
async def create_api_key(user_id: int, db: Session = Depends(get_db)):
    # Get the user from the database
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a new API key
    new_api_key = secrets.token_urlsafe(32)

    # Create a new ApiKey object and associate it with the user
    api_key = ApiKey(key=new_api_key, user=user)

    # Add the ApiKey object to the session and commit the session
    db.add(api_key)
    db.commit()

    return {"api_key": new_api_key}



class Customer(BaseModel):
    customerId: str

@app.post("/stripe/get-payment-methods")
async def get_payment_methods(current_user: User = Depends(get_current_user)):
    try:
        # Retrieve the payment methods for the customer
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.customerId,
            type="card",
        )
        return {"payment_methods": payment_methods["data"]}
    except Exception as e:
        return {"error": str(e)}
    

class PaymentMethod(BaseModel):
    paymentMethod: str

@app.post("/stripe/attach-payment-method")
async def attach_payment_methods(request: Request, current_user: User = Depends(get_current_user)):
    data = await request.json()
    print(data)
    pass
    try:
        # Create a customer in Stripe
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
        )

        # Attach the payment method to the customer
        stripe.PaymentMethod.attach(
            paymentMethod.paymentMethodId,
            customer=customer.id,
        )

        # Save the customer ID to the user in the database
        current_user.stripe_customer_id = customer.id
        current_user.save()

        return {"message": "Payment method attached to customer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))