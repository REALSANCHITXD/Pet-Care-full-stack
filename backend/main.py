from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users,products,orders,vets,booking,pets,carts,chatbot
import auth


app = FastAPI(title = "Pet Care App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router,tags=["Users"])
app.include_router(products.router,tags=["Products"])
app.include_router(carts.router,tags=["Carts"])
app.include_router(orders.router,tags=["Orders"])
app.include_router(vets.router,tags=["Vets"])
app.include_router(booking.router,tags=["Booking"])
app.include_router(pets.router,tags=["Pets"])
app.include_router(auth.router)
app.include_router(chatbot.router,tags=["Chatbot"])

@app.get("/")
def root():
    return {"message": "Welcome to the Pet Care App"}