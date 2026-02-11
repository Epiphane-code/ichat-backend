from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import status, users, messages, otp, token, contacts

app = FastAPI(title="iChat Backend")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(status.router, prefix="/status", tags=["Status"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(otp.router, prefix="/otp", tags=["OTP"])
app.include_router(token.router, prefix="/token", tags=["Token"])
app.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])

@app.get("/home")
async def root():
    return {"message": "Backend iChat opérationnel !"}
