from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi import UploadFile, File, Form
import os
import re
import zipfile

load_dotenv()

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class UserRequest(BaseModel):
    description: str
    dataset_size: int = 0


# ----------------------------
# Clean SQL output
# ----------------------------
def clean_sql(sql_text):
    sql_text = sql_text.replace("```sql", "")
    sql_text = sql_text.replace("```", "")
    return sql_text.strip()


# ----------------------------
# SQL → SQLAlchemy Models
# ----------------------------
def sql_to_sqlalchemy_models(sql_schema):

    models = []
    tables = re.findall(r'CREATE TABLE (\w+) \((.*?)\);', sql_schema, re.S)

    for table_name, columns_block in tables:

        class_name = table_name.capitalize()

        model = f"class {class_name}(Base):\n"
        model += f"    __tablename__ = \"{table_name}\"\n\n"

        columns = columns_block.split(",")

        for col in columns:

            col = col.strip()

            if col.upper().startswith("FOREIGN KEY"):
                continue

            parts = col.split()

            if len(parts) < 2:
                continue

            column_name = parts[0]

            if column_name.upper() == "PRIMARY":
                continue

            sql_type = parts[1].upper()

            if "INT" in sql_type:
                py_type = "Integer"
            elif "VARCHAR" in sql_type:
                py_type = "String"
            elif "DATE" in sql_type:
                py_type = "Date"
            elif "DECIMAL" in sql_type:
                py_type = "Float"
            else:
                py_type = "String"

            if "PRIMARY KEY" in col.upper():
                model += f"    {column_name} = Column({py_type}, primary_key=True)\n"
            else:
                model += f"    {column_name} = Column({py_type})\n"

        models.append(model)

    return "\n\n".join(models)

#-------
#extract table names from SQL schema 
#-------

def extract_table_names(sql_schema):

    tables = re.findall(r'CREATE TABLE (\w+)', sql_schema)

    return tables

#----------------------------
# table parser
#----------------------------
def generate_crud_routes(sql_schema):

    tables = extract_table_names(sql_schema)

    routes = ""

    for table in tables:

        routes += f"""

@router.get("/{table}")
def get_{table}():
    return {{"message": "List all {table}"}}


@router.post("/{table}")
def create_{table}():
    return {{"message": "Create {table}"}}


@router.put("/{table}/{{id}}")
def update_{table}(id: int):
    return {{"message": "Update {table} with id {{id}}"}}


@router.delete("/{table}/{{id}}")
def delete_{table}(id: int):
    return {{"message": "Delete {table} with id {{id}}"}}
"""

    return routes

#----------
#Add dataset generation function - generates simple datasets
#----------
from faker import Faker
import csv
import random

fake = Faker()

def generate_dataset(sql_schema, project_path, size):

    dataset_path = os.path.join(project_path, "dataset")
    os.makedirs(dataset_path, exist_ok=True)

    tables = extract_table_names(sql_schema)

    for table in tables:

        file_path = os.path.join(dataset_path, f"{table}.csv")

        with open(file_path, "w", newline="") as f:

            writer = csv.writer(f)

            # simple header
            writer.writerow(["id", "name", "value"])

            for i in range(size):

                writer.writerow([
                    i + 1,
                    fake.name(),
                    random.randint(1, 1000)
                ])


def get_next_project_folder():

    base_path = "generated_projects"

    os.makedirs(base_path, exist_ok=True)

    existing = [
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d)) and d.startswith("generated_backend_")
    ]

    numbers = []

    for name in existing:
        try:
            num = int(name.split("_")[-1])
            numbers.append(num)
        except:
            pass

    next_number = max(numbers) + 1 if numbers else 1

    return os.path.join(base_path, f"generated_backend_{next_number}")

# ----------------------------
# Create FastAPI backend project
# ----------------------------
def create_fastapi_project(sql_schema):

    models_code = sql_to_sqlalchemy_models(sql_schema)
    
    routes_code = generate_crud_routes(sql_schema)

    project_path = get_next_project_folder()

    os.makedirs(project_path + "/app", exist_ok=True)

    main_file = """
from fastapi import FastAPI
from .database import engine
from .models import Base
from .routes import router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)
"""

    database_file = """
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
"""

    routes_file = f"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {{"message": "Generated FastAPI backend running"}}
{routes_code}
"""

    models_file = f"""
from sqlalchemy import Column, Integer, String, Date, Float
from .database import Base

{models_code}
"""

    requirements_file = """
fastapi
uvicorn
sqlalchemy
"""

    with open(project_path + "/app/main.py", "w") as f:
        f.write(main_file)

    with open(project_path + "/app/database.py", "w") as f:
        f.write(database_file)

    with open(project_path + "/app/routes.py", "w") as f:
        f.write(routes_file)

    with open(project_path + "/app/models.py", "w") as f:
        f.write(models_file)

    with open(project_path + "/requirements.txt", "w") as f:
        f.write(requirements_file)

    return project_path


# ----------------------------
# ZIP generator
# ----------------------------
def zip_project(project_path):

    zip_path = project_path + ".zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_path)
                zipf.write(file_path, arcname)

    return zip_path


# ----------------------------
# API Endpoints
# ----------------------------
@app.get("/")
def home():
    return {"message": "Backend running successfully!"}


@app.post("/generate")
async def generate(
    description: str = Form(...),
    dataset_size: int = Form(0),
    file: UploadFile = File(None)
):

    try:
        prompt = f"""
        Generate a SQL database schema for the following application:

        {description}

        Return only SQL code.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        result = completion.choices[0].message.content

        cleaned_sql = clean_sql(result)

        project_path = create_fastapi_project(cleaned_sql)

        dataset_folder = os. path.join(project_path, "dataset")
        os.makedirs(dataset_folder, exist_ok=True)

        # If user uploads dataset
        if file:
            file_location = os.path.join(dataset_folder, file.filename)

            with open(file_location, "wb") as f:
                f.write(await file.read())

        # Else generate dataset
        elif dataset_size > 0:
            generate_dataset(cleaned_sql, project_path, dataset_size)

        if dataset_size > 0:
            generate_dataset(cleaned_sql, project_path, dataset_size)  

        zip_project(project_path)

        return {
            "generated_schema": cleaned_sql
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/download")
def download_file():

    base_path = "generated_projects"

    zips = [
        os.path.join(base_path, f)
        for f in os.listdir(base_path)
        if f.endswith(".zip")
    ]

    if not zips:
        return {"error": "No generated projects found"}

    latest_zip = max(zips, key=os.path.getctime)

    return FileResponse(latest_zip, filename=os.path.basename(latest_zip))