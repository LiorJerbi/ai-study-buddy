import os
import sys
import io
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# תיקון ג'יבריש: מכריח את הטרמינל להשתמש ב-UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# הגדרות
PERSIST_DIRECTORY = "./chroma_db"
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2-preview")
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

print("Connecting to Vector Store...")

# טעינת מסד הנתונים הקיים (בלי לבנות מחדש!)
if os.path.exists(PERSIST_DIRECTORY):
    vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
else:
    print("Error: Vector store not found. Please run the build process again.")
    sys.exit(1)

# שאילתה לבדיקה
question = "מה זה מפתח זר ואיך הוא עוזר לשמור על תקינות נתונים?"

# שולפים את 5 החתיכות הכי רלוונטיות (הגדלנו מ-3 ל-5)
results = vectorstore.similarity_search(question, k=5)
context = "\n".join([res.page_content for res in results])

# פרומפט משופר לקבלת תשובה כללית ומקצועית
prompt = f"""
אתה עוזר לימודי מקצועי למסדי נתונים.
על בסיס המידע מהסיכום המצורף בלבד, ענה על השאלה בצורה מפורטת.
הפרד בין ההסבר התאורטי לבין דוגמאות אם קיימות.

השאלה: {question}

הקשר מהסיכום:
{context}
"""

try:
    response = llm.invoke(prompt)
    
    # חילוץ הטקסט הנקי בלבד
    if isinstance(response.content, list):
        final_text = response.content[0].get('text', '')
    else:
        final_text = response.content

    print("\n" + "="*30)
    print("תשובה סופית מהסיכום:")
    print("="*30)
    print(final_text)
    print("="*30)
    
except Exception as e:
    print(f"Error: {e}")