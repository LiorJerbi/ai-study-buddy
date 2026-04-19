import streamlit as st
import os
import shutil # ספריה לניהול קבצים ותיקיות
from rag_engine import RAGEngine
from ingestion import Ingestor

# --- הגדרות דף ---
st.set_page_config(page_title="AI Study Buddy", layout="centered")

# --- CSS ליישור לימין (RTL) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stChatMessage"] {
        direction: rtl; text-align: right;
    }
    [data-testid="stMarkdownContainer"] p { text-align: right; }
    [data-testid="stChatInput"] textarea { direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות עזר ---
def clear_all_data():
    """מוחק את מסד הנתונים בצורה בטוחה"""
    # סגירת המנוע לפני מחיקה כדי לשחרר נעילת קבצים
    if "engine" in st.session_state:
        st.session_state.engine = None
    
    # המתנה קצרה לשחרור קבצים
    time.sleep(1)
    
    if os.path.exists("chroma_db"):
        try:
            shutil.rmtree("chroma_db")
        except Exception as e:
            st.error(f"שגיאה במחיקה: {e}")
            
    os.makedirs("data", exist_ok=True)
    st.session_state.engine = RAGEngine()
    st.session_state.messages = []
    st.toast("המערכת אותחלה!", icon="🗑️")

# --- אתחול המערכת (Session State) ---
if "engine" not in st.session_state:
    st.session_state.engine = RAGEngine()
    st.session_state.engine.load_db()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- כותרת ---
st.title("🎓 AI Study Buddy")

# --- Sidebar (תפריט צד) ---
with st.sidebar:
    st.header("ניהול חומר לימוד")
    
    # חיווי סטטוס מסד הנתונים
    db_exists = os.path.exists("chroma_db") and os.listdir("chroma_db")
    if db_exists:
        st.success("המערכת מחוברת למסד הנתונים")
    else:
        st.warning("מסד הנתונים ריק. העלה קובץ.")
    
    st.divider()
    
    # העלאת קבצים
    uploaded_file = st.file_uploader("העלה סיכום חדש (PDF)", type="pdf")
    
    if uploaded_file is not None:
        os.makedirs("data", exist_ok=True)
        temp_path = os.path.join("data", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("עבד והוסף לזיכרון", use_container_width=True):
            with st.spinner("מעבד את נתוני הסיכום ..."):
                ingestor = Ingestor()
                ingestor.process_pdf(temp_path)
                
                # טעינה מחדש של המנוע מתוך ה-session_state
                st.session_state.engine.load_db()
                st.session_state.upload_success = True
                st.rerun()

    # חיווי הצלחה
    if st.session_state.get("upload_success"):
        st.toast("המידע התווסף בהצלחה!", icon="🎓")
        st.balloons()
        del st.session_state.upload_success

    st.divider()
    
    # כפתורי ניהול
    if st.button("🗑️ נקה מסד נתונים (Reset)", use_container_width=True):
        clear_all_data()
        st.rerun()
        
    if st.button("💬 נקה היסטוריית שיחה", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- צ'אט (גוף האפליקציה) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("שאל אותי על חומר הלימוד..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("סורק סיכומים..."):
            # שימוש במנוע מתוך ה-session_state
            full_response = st.session_state.engine.query(prompt)
            st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})