from datetime import datetime
import stripe
from stripe.error import CardError, StripeError
from pydantic import BaseModel
import logging
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.utils.auth import get_current_user
from backend.utils.db import ApiKey, User, get_db, Base, engine
from backend.user_routes import router as user_router
import stripe
import os
import secrets

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# instantiate the API
app = FastAPI()
app.include_router(user_router)

stripe.api_key = os.getenv("STRIPE_PRIVATE_KEY")

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

@app.post("/forward_to_chatgpt")
async def forward_to_chatgpt(request: Request, api_key: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    data = await request.json()
    payload = data.get('payload')

    try:
        # Retrieve the user attached to the api_key
        user = db.query(User).filter(User.api_key == api_key).first()

        if not user:
            raise HTTPException(status_code=404, detail="Invalid API Key")

        stripe_customer_id = user.stripe_customer_id

        # Forward the request to ChatGPT
        response = requests.post(
            "https://api.openai.com/v1/engines/davinci-codex/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=data.get('payload'),
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to forward request to ChatGPT")
        

        # Create a payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=1000,  # amount in cents. NOTE: calculate from payload size in future
            currency="usd",
            customer=stripe_customer_id,  # replace with your customer's Stripe ID
        )

        # Confirm the payment intent
        confirmed_payment_intent = stripe.PaymentIntent.confirm(payment_intent.id)

        return response.json()

    except (CardError, StripeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/create-api-key")
async def create_api_key(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print("in")
    # Get the user from the database
    user = db.query(User).get(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a new API key
    new_api_key = secrets.token_urlsafe(32)

    # Get the current time
    current_time = datetime.now()

    # Create a new ApiKey object and associate it with the user
    api_key = ApiKey(key=new_api_key, user=user, date_created=current_time)

    # Add the ApiKey object to the session and commit the session
    db.add(api_key)
    db.commit()

    return {"api_key": new_api_key}

@app.get("/fetch-api-keys")
async def fetch_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get the user from the database
    user = db.query(User).get(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all API keys associated with the user
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == user.id).all()

    # Convert the API keys to a list of dictionaries, each containing the key and its usage
    api_keys_info = [{"key": api_key.key, "usage": api_key.usage, "date_created": api_key.date_created, "last_used": api_key.last_used } for api_key in api_keys]

    return {"api_keys": api_keys_info}

@app.post("/stripe/get-payment-methods")
async def get_payment_methods(current_user: User = Depends(get_current_user)):
    return {"message": "Payment methods retrieved"}
    # try:
    #     # Retrieve the payment methods for the customer
    #     payment_methods = stripe.PaymentMethod.list(
    #         customer=customer.customerId,
    #         type="card",
    #     )
    #     return {"payment_methods": payment_methods["data"]}
    # except Exception as e:
    #     return {"error": str(e)}
    


@app.post("/stripe/attach-payment-method")
async def attach_payment_methods(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    paymentMethod = data.get('paymentMethod')

    try:
        # Create a customer in Stripe
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
        )

        # Attach the payment method to the customer
        stripe.PaymentMethod.attach(
            paymentMethod['id'],
            customer=customer.id,
        )

        # Save the customer ID to the user in the database
        user = db.query(User).filter(User.id == current_user.id).first()
        user.stripe_customer_id = customer.id
        user.card_country = paymentMethod['card']['country']
        user.card_last4 = paymentMethod['card']['last4']
        user.card_brand = paymentMethod['card']['brand']
        db.commit()

        return {"message": "Payment method attached to customer"}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=400, detail=str(e))