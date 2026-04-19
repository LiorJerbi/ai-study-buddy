import os
import time
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

class Ingestor:
    def __init__(self, persist_directory="chroma_db"):
        # הפיכת הנתיב למוחלט כדי למנוע שגיאות הרשאות בדוקר
        self.persist_directory = os.path.abspath(persist_directory)
        # יצירה מראש של התיקייה אם היא לא קיימת
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2-preview")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)

    def clean_text(self, text):
        """מנקה תווים לא תקינים שמשגעים את הקידוד של גוגל ושל מסד הנתונים"""
        if not text: return ""
        # השארת עברית, אנגלית, מספרים ופיסוק בסיסי בלבד
        cleaned = re.sub(r'[^\w\s\u0590-\u05FF.,?!:;()-]', '', text)
        # סינון תווים בלתי נראים (Control Characters)
        cleaned = "".join(c for c in cleaned if c.isprintable())
        return re.sub(r'\s+', ' ', cleaned).strip()

    def process_pdf(self, file_path):
        print(f"⚡ Starting Process: {file_path}")
        
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
        except Exception as e:
            print(f"❌ Failed to read PDF file: {e}")
            return 0
        
        # --- שלב ה-DEBUG: מה המערכת באמת מצליחה לקרוא? ---
        raw_text = "\n".join([p.page_content for p in pages])
        print(f"🔍 DEBUG: Raw text length extracted: {len(raw_text)} characters")
        
        if len(raw_text.strip()) < 100:
            print("❌ ERROR: PDF seems empty or an image (No text found).")
            return 0

        # ניקוי ופיצול
        cleaned_content = self.clean_text(raw_text)
        splits = self.text_splitter.create_documents([cleaned_content])
        print(f"📦 Total chunks created: {len(splits)}")

        # אתחול מסד הנתונים
        vectorstore = Chroma(
            persist_directory=self.persist_directory, 
            embedding_function=self.embeddings
        )

        batch_size = 5 # מנה מאוזנת ליציבות
        for i in range(0, len(splits), batch_size):
            batch = splits[i:i + batch_size]
            success = False
            while not success:
                try:
                    vectorstore.add_documents(batch)
                    print(f"🚀 Progress: {min(i + batch_size, len(splits))}/{len(splits)} chunks done.")
                    success = True
                except Exception as e:
                    error_detail = repr(e) # מוציא את השגיאה המלאה ולא רק את "e"
                    if "429" in error_detail or "RESOURCE_EXHAUSTED" in error_detail:
                        print("⏳ API Limit hit. Sleeping 60s...")
                        time.sleep(60)
                    else:
                        print(f"⚠️ Batch failed: {error_detail[:100]}. Switching to individual mode...")
                        # ניסיון פרטני לכל חתיכה במנה שנכשלה
                        for j, doc in enumerate(batch):
                            item_success = False
                            while not item_success:
                                try:
                                    vectorstore.add_documents([doc])
                                    print(f"   - Sub-chunk {j+1} added.")
                                    item_success = True
                                    time.sleep(2) # מניעת הצפה בבודדים
                                except Exception as inner_e:
                                    if "429" in str(inner_e):
                                        print("     ⏳ Busy... waiting 30s")
                                        time.sleep(30)
                                    else:
                                        print(f"     ❌ Skipping broken chunk: {repr(inner_e)[:50]}")
                                        item_success = True # דלג על חתיכה שבאמת אי אפשר לקרוא
                        success = True # ממשיך למנה הבאה
            
            time.sleep(3) # הפסקה קצרה בין מנות למניעת חסימה

        print("🎯 Ingestion completed successfully!")
        return len(splits)