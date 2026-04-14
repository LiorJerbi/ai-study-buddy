import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

class RAGEngine:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2-preview")
        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
        self.vectorstore = None

    def load_db(self):
        """טוען את מסד הנתונים הוקטורי מהדיסק"""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory, 
                embedding_function=self.embeddings
            )
            return True
        return False

    def query(self, question):
        """מבצע חיפוש סמנטי ומחזיר תשובה מנומקת מה-AI"""
        if not self.vectorstore:
            return "Error: Database not loaded."
        
        # חיפוש הקשר
        results = self.vectorstore.similarity_search(question, k=5)
        context = "\n".join([res.page_content for res in results])
        
        # בניית הפרומפט
        prompt = f"""
        אתה עוזר לימודי למסדי נתונים. ענה על השאלה בצורה מקצועית על בסיס ההקשר המצורף.
        אם התשובה לא נמצאת במידע, ציין זאת.
        
        השאלה: {question}
        
        הקשר:
        {context}
        """
        
        response = self.llm.invoke(prompt)
        
        # ניקוי הפלט (Parsing)
        if isinstance(response.content, list):
            return response.content[0].get('text', '')
        return response.content