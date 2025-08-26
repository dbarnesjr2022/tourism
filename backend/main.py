from fastapi import FastAPI
from backend.app.api import forecast, pricing, personas, campaigns, chatbot, auth, billing, crm, offers

app = FastAPI(title="Tourism Intelligence Platform")

app.include_router(forecast.router, prefix="/forecast")
app.include_router(pricing.router, prefix="/pricing")
app.include_router(personas.router, prefix="/personas")
app.include_router(campaigns.router, prefix="/campaigns")
app.include_router(chatbot.router, prefix="/chatbot")
app.include_router(auth.router, prefix="/auth")
app.include_router(billing.router, prefix="/billing")
app.include_router(crm.router, prefix="/crm")
app.include_router(offers.router, prefix="/offers")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Tourism Intelligence Platform API"}
