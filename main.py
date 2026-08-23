import uvicorn
import os
from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import timedelta, datetime
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
import models
from jwt.exceptions import InvalidTokenError
from database import engine, SessionLocal
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title = "Arm-έξ: Παρακολούθηση Εξόδων Θητείας")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "ena-prosorino-kleidi")
ALGORITHM = 'HS256'

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_hashed_password(password: str):
    return pwd_context.hash(password)


origins = [
    "http://localhost",
    "http://localhost:5500",     
    "http://127.0.0.1:5500",     
    "https://armex-q7rd.onrender.com",
    "https://manolis-s.github.io" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExpenseCreate(BaseModel):
    amount: float
    subcategory_id: int
    description: str = ""

class DateUpdate(BaseModel):
    discharge_date: str

class UserCreate(BaseModel):
    username: str
    password: str
    discharge_date: str  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token:str=Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Δεν ήταν δυνατή η επαλήθευση",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        user_id: str=payload.get("sub")
        if user_id is None: 
            raise credentials_exception
       
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


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
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_expense = models.Expense(
        amount = expense.amount, 
        subcategory_id = expense.subcategory_id, 
        description = expense.description, 
        user_id = current_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"message": "Το έξοδο καταγράφηκε"}

@app.get("/expenses/recent")
def get_recent_expenses(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
   
    expenses = db.query(models.Expense)\
                 .filter(models.Expense.user_id == current_user.id)\
                 .order_by(models.Expense.date.desc())\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    
    result = []
    for exp in expenses:
        # Βρίσκουμε την υποκατηγορία και την κατηγορία της (προσαρμόσε τα ονόματα αν στη βάση σου λένε διαφορετικά)
        sub_name = exp.subcategory.name if exp.subcategory else "Άγνωστο"
        cat_name = exp.subcategory.category.name if (exp.subcategory and exp.subcategory.category) else "Άγνωστο"
        
        result.append({
            "id": exp.id,
            "amount": exp.amount,
            "date": exp.date,
            "description": exp.description,
            "subcategory": sub_name,
            "category": cat_name
        })
        
    return result

@app.get("/stats/")
def get_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Προσθέσαμε ΠΑΝΤΟΥ το .filter(models.Expense.user_id == current_user.id)
    
    total_amount = db.query(func.sum(models.Expense.amount))\
        .filter(models.Expense.user_id == current_user.id).scalar() or 0.0

    inside_total = db.query(func.sum(models.Expense.amount))\
        .join(models.Subcategory, models.Expense.subcategory_id == models.Subcategory.id)\
        .join(models.Category, models.Subcategory.category_id == models.Category.id)\
        .filter(models.Expense.user_id == current_user.id)\
        .filter(models.Category.is_inside_camp == True).scalar() or 0.0
        
    outside_total = total_amount - inside_total

    cat_stats = db.query(
        models.Category.name,
        func.sum(models.Expense.amount)
    ).select_from(models.Expense)\
     .join(models.Subcategory, models.Expense.subcategory_id == models.Subcategory.id)\
     .join(models.Category, models.Subcategory.category_id == models.Category.id)\
     .filter(models.Expense.user_id == current_user.id)\
     .group_by(models.Category.name).all()

    subcats_stats = db.query(
        models.Subcategory.name,
        models.Category.name,
        func.sum(models.Expense.amount).label("total_sum"),
        func.count(models.Expense.id).label("count")
    ).select_from(models.Expense)\
     .join(models.Subcategory, models.Expense.subcategory_id == models.Subcategory.id)\
     .join(models.Category, models.Subcategory.category_id == models.Category.id)\
     .filter(models.Expense.user_id == current_user.id)\
     .group_by(models.Subcategory.id, models.Subcategory.name, models.Category.name).all()

    return {
        "discharge_date": current_user.discharge_date,
        "grand_total": round(total_amount, 2),
        "camp_ratio": {
            "inside_camp": round(inside_total, 2),
            "outside_camp": round(outside_total, 2)
        },
        "by_category": [{"name": name, "total": round(total, 2)} for name, total in cat_stats],
        "by_subcategory": [{"name": sub_name, "category": cat_name, "total_cost": round(tot, 2), "times_bought": count} for sub_name, cat_name, tot, count in subcats_stats]
    }

@app.delete("/expenses/all/")
def delete_all_expenses(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db.query(models.Expense).filter(models.Expense.user_id == current_user.id).delete()   
    db.commit()
    return {"message": "Όλα τα έξοδά σου διαγράφηκαν"}


@app.put("/users/update-date")
def update_date(date_data: DateUpdate, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    current_user.discharge_date = date_data.discharge_date
    db.commit()
    return{"message": "Η ημερομηνία ανανεώθηκε"}
#-----------------USERS----------------------

@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code = 400, detail = "Το όνομα χρήστη χρησιμοποιείται ήδη")
    
    hashed_pw = get_hashed_password(user.password)
    new_user = models.User(username=user.username, hashed_password = hashed_pw, discharge_date = user.discharge_date)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Ο λογαριασμός δημιουργήθηκε με επιτυχία!"}




@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Λάθος όνομα χρήστη ή κωδικός!",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return({"access_token": access_token, 'token_type': "bearer"})

@app.delete("/delete_expense/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Το έξοδο δεν βρέθηκε")

    db.delete(expense)
    db.commit()
    return{"message": "Το έξοδο διεγράφη!"}

    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

