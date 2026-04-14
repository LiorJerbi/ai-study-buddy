FROM python:3.12-slim
WORKDIR /app

# מעתיקים את הקבצים מהשורש של הפרויקט לתוך ה-Container
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# אנחנו מעתיקים את כל התוכן (כולל תיקיית src ו-data)
COPY . .

# מעדכנים את נתיב ההרצה לתוך תיקיית src
CMD ["python", "src/main.py"]