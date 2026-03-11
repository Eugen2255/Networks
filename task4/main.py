from fastapi import FastAPI, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import init_db, get_db, Product
from parser import parse 


app = FastAPI(title="Parser API")

@app.on_event("startup")
def startup():
    init_db()


@app.post("/parse")
def run_parser(
    url: str = Query(..., description="URL для парсинга"),
    db: Session = Depends(get_db)
):
    """
    Запускает парсер и сохраняет результат в БД.
    curl -X POST "http://127.0.0.1:8000/parse?url=https://divoroom.store/catalog"
    """
    try:
        products = parse(url=url, headless=True)
        
        if not products:
            return {"error": "Товары не найдены", "url": url}
        
        for p in products:
            existing = db.query(Product).filter(
                Product.product_id == p.get('product_id'),
                Product.source_url == url
            ).first()
            
            if existing:
                for k, v in p.items():
                    if hasattr(existing, k) and v is not None:
                        setattr(existing, k, v)
            else:
                product = Product(
                    product_id=p.get('product_id'),
                    title=p['title'],
                    description=p.get('description'),
                    price=p.get('price'), 
                    url=p.get('url'),
                    image=p.get('image'),
                    source_url=url
                )
                db.add(product)
        
        db.commit()
        return {"status": "ok", "parsed": len(products)}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products")
def get_products(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    source_url: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Возвращает товары из БД в JSON.
    curl "http://127.0.0.1:8000/products?limit=50"
    """
    query = db.query(Product)
    if source_url:
        query = query.filter(Product.source_url == source_url)
    
    products = query.order_by(Product.parsed_at.desc()).offset(offset).limit(limit).all()
    return [p.to_dict() for p in products]


@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Возвращает один товар по ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product.to_dict()


@app.get("/")
def root():
    return {"service": "Parser API", "docs": "/docs"}