import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware  # <-- ΑΥΤΗ Η ΓΡΑΜΜΗ ΕΛΕΙΠΕ!
import models
from database import engine, SessionLocal
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title = "Arm-έξ: Παρακολούθηση Εξόδων Θητείας")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Επιτρέπει σε όλα τα frontends να μιλήσουν στο API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExpenseCreate(BaseModel):
    amount: float
    subcategory_id: int
    description: str = ""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

#dhmioyrgia vasis dedomenwn
@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if not db.query(models.Category).first():
        default_data = [
            {"name": "ΚΨΜ", "is_inside": True, "subs": ["Καφές", "Νερό", "Aναψυκτικό", "Σνακ", "Είδη Υγιεινής", "Άλλο"]},
            {"name": "Έξοδος", "is_inside": False, "subs": ["Φαγητό", "Ποτό", "Διασκέδαση", "Πλυντήριο", "Άλλο"]},
            {"name": "Μεταφορικά", "is_inside": False, "subs": ["ΚΤΕΛ", "Τρένο", "Ταξί", "Αστικό", "Διόδια"]},
            {"name": "Προσωπικά", "is_inside": False, "subs": ["Τσιγάρα", "Κάρτα Κινητού"]}
        ]
        for cat_data in default_data:
            category = models.Category(name=cat_data['name'], is_inside_camp = cat_data['is_inside'])
            db.add(category)
            db.commit()
            db.refresh(category)
            for sub_name in cat_data['subs']:
                sub = models.Subcategory(name = sub_name, category_id = category.id)
                db.add(sub)
        db.commit()
    db.close()

#endpoints - pame na doume
@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    result = []
    for cat in categories:
        subs = [{"id": sub.id, "name": sub.name} for sub in cat.subcategories]
        result.append({"id":cat.id, "name":cat.name, "is_inside_camp": cat.is_inside_camp, 'subcategories': subs})
    return result

@app.post("/expenses/")
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = models.Expense(
        amount = expense.amount, 
        subcategory_id = expense.subcategory_id, 
        description = expense.description
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"message": "Το έξοδο καταγράφηκε"}

@app.get("/expenses/recent/")
def get_recent_expenses(db: Session = Depends(get_db)):
    recent = db.query(models.Expense).order_by(models.Expense.date.desc()).limit(15)

    result = []
    for exp in recent:
        result.append({
            "id": exp.id,
            "amount": exp.amount, 
            "category": exp.subcategory.category.name,
            "subcategory": exp.subcategory.name,
            "date": exp.date.strftime("%d/%m/%Y %H:%M")
        })
    return result

@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    total_amount = db.query(func.sum(models.Expense.amount)).scalar() or 0

    inside_total = db.query(func.sum(models.Expense.amount))\
        .join(models.Subcategory, models.Expense.subcategory_id == models.Subcategory.id)\
        .join(models.Category, models.Subcategory.category_id == models.Category.id)\
        .filter(models.Category.is_inside_camp == True).scalar() or 0.0
    outside_total = total_amount - inside_total

    cat_stats = db.query(
        models.Category.name,
        func.sum(models.Expense.amount)
    ).select_from(models.Expense)\
     .join(models.Subcategory, models.Expense.subcategory_id == models.Subcategory.id)\
     .join(models.Category, models.Subcategory.category_id == models.Category.id)\
     .group_by(models.Category.name).all()

    subcat_stats = db.query(
        models.Subcategory.name,
        func.sum(models.Expense.amount).label("total_sum"),
        func.count(models.Expense.id).label("total_count")
    ).join(models.Expense).group_by(models.Subcategory.name).all()

    return {
        "grand_total": round(total_amount, 2),
        "camp_ratio": {
            "inside_camp": round(inside_total, 2),
            "outside_camp": round(outside_total, 2)
        },
        "by_category": [{"name": name, "total": round(total, 2)} for name, total in cat_stats],
        "by_subcategory": [
            {"name": name, "total_cost": round(tot, 2), "times_bought": count} 
            for name, tot, count in subcat_stats
        ]
    }

@app.delete("/expenses/all/")
def delete_all_expenses(db: Session = Depends(get_db)):
    db.query(models.Expense).delete()   
    db.commit()
    return {"message": "Όλα τα έξοδα διαγράφηκαν"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

