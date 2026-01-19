from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import (
    String, Float, Integer, create_engine, select
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DATABASE_URL = (
    #"postgresql+psycopg://user:pass@db.server:5432/postgres"
    #"postgresql+psycopg://postgres:1234abcd@cynwumoye-cyo-db.c96ckkegil1k.eu-west-1.rds.amazonaws.com:5432/cynwumoye_DB"
    "postgresql+psycopg://dbuser:dbpassword@192.168.10.23:32100/fruitveg_db"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# -----------------------------
# ORM BASE
# -----------------------------
class Base(DeclarativeBase):
    pass

# -----------------------------
# PRODUCT MODEL
# -----------------------------
class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # UI expects: fruit | veg | herbs
    cat: Mapped[str] = mapped_column(String(40), nullable=False)

    price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)

    rating: Mapped[float] = mapped_column(Float, nullable=False, default=4.5)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=20)

    # hot | fresh | deal | limited | ""
    tag: Mapped[str] = mapped_column(String(40), nullable=False, default="")

    image: Mapped[str] = mapped_column(String(600), nullable=False)

    deal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

# -----------------------------
# INITIAL DATA
# -----------------------------

def seed_data():
    with Session(engine) as session:
        if session.execute(select(Product.id).limit(1)).first():
            return

        products = [
            # ---------- FRUITS ----------
            Product(
                id="banana",
                name="Organic Bananas",
                cat="fruit",
                price=1.29,
                unit="bunch",
                rating=4.4,
                stock=40,
                tag="deal",
                deal=1.59,
                image="https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="mango",
                name="Golden Mango",
                cat="fruit",
                price=2.49,
                unit="each",
                rating=4.8,
                stock=36,
                tag="hot",
                image="https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="strawberries",
                name="Fresh Strawberries",
                cat="fruit",
                price=4.99,
                unit="pack",
                rating=4.7,
                stock=18,
                tag="fresh",
                image="https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="pineapple",
                name="Tropical Pineapple",
                cat="fruit",
                price=3.49,
                unit="each",
                rating=4.5,
                stock=12,
                tag="limited",
                image="https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="blueberries",
                name="Blueberries",
                cat="fruit",
                price=4.59,
                unit="pack",
                rating=4.7,
                stock=9,
                tag="limited",
                image="https://images.unsplash.com/photo-1498557850523-fd3d118b962e?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="apple",
                name="Red Apples",
                cat="fruit",
                price=2.99,
                unit="bag",
                rating=4.5,
                stock=25,
                tag="fresh",
                image="https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?auto=format&fit=crop&w=1200&q=80",
            ),

            # ---------- VEGETABLES ----------
            Product(
                id="tomato",
                name="Vine Tomatoes",
                cat="veg",
                price=3.29,
                unit="lb",
                rating=4.5,
                stock=28,
                tag="fresh",
                image="https://images.unsplash.com/photo-1561136594-7f68413baa99?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="kale",
                name="Curly Kale",
                cat="veg",
                price=2.19,
                unit="bunch",
                rating=4.4,
                stock=14,
                tag="hot",
                image="https://images.unsplash.com/photo-1511690656952-34342bb7c2f2?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="carrots",
                name="Rainbow Carrots",
                cat="veg",
                price=3.79,
                unit="bag",
                rating=4.6,
                stock=10,
                tag="limited",
                image="https://images.unsplash.com/photo-1582515073490-39981397c445?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="cucumber",
                name="Fresh Cucumbers",
                cat="veg",
                price=1.29,
                unit="each",
                rating=4.3,
                stock=45,
                tag="deal",
                deal=1.69,
                image="https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="bellpepper",
                name="Bell Pepper Mix",
                cat="veg",
                price=4.29,
                unit="pack",
                rating=4.5,
                stock=16,
                tag="hot",
                image="https://images.pexels.com/photos/594137/pexels-photo-594137.jpeg",
            ),
            Product(
                id="spinach",
                name="Baby Spinach",
                cat="veg",
                price=2.99,
                unit="bag",
                rating=4.4,
                stock=20,
                tag="fresh",
                image="https://images.unsplash.com/photo-1582515073490-39981397c445?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="onion",
                name="Yellow Onions",
                cat="veg",
                price=2.49,
                unit="bag",
                rating=4.3,
                stock=34,
                tag="",
                image="https://images.unsplash.com/photo-1508747703725-719777637510?auto=format&fit=crop&w=1200&q=80",
            ),

            # ---------- HERBS ----------
            Product(
                id="basil",
                name="Sweet Basil",
                cat="herbs",
                price=2.99,
                unit="bunch",
                rating=4.6,
                stock=16,
                tag="fresh",
                image="https://images.unsplash.com/photo-1526318472351-c75fcf070305?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="mint",
                name="Garden Mint",
                cat="herbs",
                price=2.49,
                unit="bunch",
                rating=4.5,
                stock=22,
                tag="deal",
                deal=2.99,
                image="https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="cilantro",
                name="Fresh Cilantro",
                cat="herbs",
                price=1.99,
                unit="bunch",
                rating=4.3,
                stock=30,
                tag="fresh",
                image="https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?auto=format&fit=crop&w=1200&q=80",
            ),
            Product(
                id="parsley",
                name="Flat Leaf Parsley",
                cat="herbs",
                price=1.89,
                unit="bunch",
                rating=4.2,
                stock=26,
                tag="",
                image="https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1200&q=80",
            ),
        ]

        session.add_all(products)
        session.commit()

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(title="Techleat Superstore API (MariaDB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    seed_data()

@app.get("/api/products")
def get_products():
    with Session(engine) as session:
        rows = session.execute(select(Product)).scalars().all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "cat": p.cat,
                "price": p.price,
                "unit": p.unit,
                "rating": p.rating,
                "stock": p.stock,
                "tag": p.tag,
                "deal": p.deal,
                "image": p.image,
            }
            for p in rows
        ]

#@app.get("/", response_class=HTMLResponse)
#def index():
#    return Path("index.html").read_text(encoding="utf-8")
