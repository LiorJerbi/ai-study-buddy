import sys
import io
from rag_engine import RAGEngine

# תיקון ג'יבריש בטרמינל
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    engine = RAGEngine()
    
    print("Connecting to Knowledge Base...")
    if not engine.load_db():
        print("Database not found! Please run ingestion first.")
        return

    print("System Ready. (Type 'exit' to quit)")
    
    while True:
        question = input("\nשאלה שלך: ")
        if question.lower() in ['exit', 'quit', 'יציאה']:
            break
            
        print("Thinking...")
        answer = engine.query(question)
        print("\n" + "="*40)
        print(answer)
        print("="*40)

if __name__ == "__main__":
    main()