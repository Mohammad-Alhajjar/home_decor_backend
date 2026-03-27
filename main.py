import uuid
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI(
    title="Home Decor API 🛋️",
    description="Professional Backend for Furniture App Training",
    version="1.0.0"
)

security = HTTPBearer()

# --- Configurations ---
USER_DATA = {
    "id": "user-homedecor-88",
    "name": "Daniel Martinez",
    "phone": "+1 555-987-654",
    "email": "user@email.com",
    "password": "user123456"
}
active_tokens = set()

# --- Models ---
class Review(BaseModel):
    id: int
    username: str
    review_body: str
    rating: int
    views: int

class Furniture(BaseModel):
    id: int
    name: str
    description: str
    price: int
    rating: int
    category: str
    type: str
    color: str
    reviews: List[Review]

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Data Generation Helpers ---

def get_furniture_description(name, category):
    # نصوص احترافية بين 30 و 35 كلمة
    descriptions = [
        f"This premium {name} is meticulously crafted to elevate your {category} with a blend of modern aesthetics and unparalleled comfort, ensuring a sophisticated atmosphere that lasts for many years of daily use.",
        f"Enhance your home interior with this stunning {name}. Designed specifically for the {category}, it features high-quality materials and a timeless design that perfectly balances functionality with contemporary elegance and style.",
        f"Experience the ultimate luxury with our exclusive {name}. This piece is the perfect addition to any {category}, offering a unique combination of durable construction and artistic design that stands out beautifully."
    ]
    return random.choice(descriptions)

def get_review_body():
    # نصوص ريفيو بين 15 و 25 كلمة
    reviews = [
        "I absolutely love this piece! It fits perfectly in my room and the quality is much better than I expected for this price.",
        "Exceptional build quality and very fast delivery. The color is exactly as shown in the pictures and it feels very sturdy and durable.",
        "Great addition to my home decor. It was very easy to assemble and the design is truly modern and elegant. Highly recommended for everyone."
    ]
    return random.choice(reviews)

def generate_furniture_list(count: int) -> List[Furniture]:
    items = []
    categories = ["Kitchen", "Livingroom", "Bedroom", "Dining Room", "Office"]
    types = ["Sofa", "Tables", "Cupboards", "Office Chairs", "Desktop Lamp", "Puff Chair", "Decor", "Nightstand"]
    colors = ["Purple", "Blue", "Light Blue", "Orange", "Black", "White"]
    usernames = ["James K.", "Sarah M.", "Oliver H.", "Emma W.", "Lucas B.", "Sophia R."]

    for i in range(1, count + 1):
        cat = random.choice(categories)
        f_type = random.choice(types)
        name = f"Premium {f_type} {i}"
        
        items.append(Furniture(
            id=2000 + i,
            name=name,
            description=get_furniture_description(name, cat),
            price=random.randint(50, 1500),
            rating=random.randint(3, 5),
            category=cat,
            type=f_type,
            color=random.choice(colors),
            reviews=[
                Review(
                    id=i * 10 + j,
                    username=random.choice(usernames),
                    review_body=get_review_body(),
                    rating=random.randint(4, 5),
                    views=random.randint(200, 500)
                ) for j in range(5) # 5 reviews per item
            ]
        ))
    return items

# Pre-generate data
ALL_FURNITURE = generate_furniture_list(30)
BEST_SELLING = random.sample(ALL_FURNITURE, 10)

# --- Dependency ---
def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    token = auth.credentials
    if token not in active_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Access denied.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# --- Endpoints ---

@app.post("/login", tags=["Auth"])
def login(request: LoginRequest):
    if request.email == USER_DATA["email"] and request.password == USER_DATA["password"]:
        token = uuid.uuid4().hex
        active_tokens.add(token)
        return {"status": "success", "token": token}
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/furniture", response_model=List[Furniture], tags=["Data"])
def get_all_furniture(token: str = Depends(verify_token)):
    return ALL_FURNITURE

@app.get("/furniture/best-selling", response_model=List[Furniture], tags=["Data"])
def get_best_selling(token: str = Depends(verify_token)):
    return BEST_SELLING

@app.get("/profile", tags=["User"])
def get_profile(token: str = Depends(verify_token)):
    return {
        "id": USER_DATA["id"],
        "email": USER_DATA["email"],
        "phone": USER_DATA["phone"],
        "name": USER_DATA["name"]
    }

@app.post("/logout", tags=["Auth"])
def logout(token: str = Depends(verify_token)):
    if token in active_tokens:
        active_tokens.remove(token)
    return {"message": "Successfully logged out from Home Decor"}