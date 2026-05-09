# 🎓 AI Study Buddy

**AI Study Buddy** is a sophisticated RAG (Retrieval-Augmented Generation) application designed to help students interact with their study materials. By leveraging Large Language Models (LLMs) and Vector Databases, the system allows users to upload academic PDFs and receive context-aware, accurate answers in real-time.

---

## 🚀 Overview

This project was built to solve the "context window" limitation of traditional LLMs. Instead of feeding an entire textbook into a prompt, **AI Study Buddy** indexes the content into a vector space, retrieving only the most relevant sections to answer a specific query. This ensures high accuracy, lower latency, and cost-effectiveness.

---

## 🛠️ Tech Stack

* **Language:** Python 3.12
* **AI Framework:** [LangChain](https://www.langchain.com/)
* **LLM:** Google Gemini 1.5 Flash
* **Embeddings:** Google Text-Embedding-004
* **Vector Database:** [ChromaDB](https://www.trychroma.com/)
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Containerization:** Docker & Docker Compose

---

## 🌟 Key Features

* **Dynamic PDF Ingestion:** Upload and process academic papers or lecture notes on the fly.
* **Semantic Search:** Uses vector embeddings to understand the *meaning* of your questions, not just keywords.
* **RTL Support:** Full Hebrew and English support with a specialized Right-to-Left (RTL) user interface.
* **Session Management:** Persistent chat history and database state management.
* **Database Control:** Built-in tools to reset the knowledge base and clear conversation history.

---

## 🧠 System Architecture

The application follows a standard RAG pipeline with enhanced resilience:

1.  **Document Loading:** Utilizing `PyPDFLoader` to extract raw text.
2.  **Text Pre-processing:** Specialized Regex cleaning to remove PDF artifacts, broken encodings, and non-printable characters.
3.  **Chunking:** `RecursiveCharacterTextSplitter` divides text into 3,000-character segments with a 300-character overlap to maintain semantic context.
4.  **Vectorization:** Converting text chunks into high-dimensional vectors via Google Generative AI.
5.  **Storage:** Persistence is handled by ChromaDB, mapped to a Docker volume for data durability.

---

## 📈 Engineering Challenges & Solutions

As a Computer Science graduate, I focused on building a "production-ready" system rather than a simple script. Key challenges included:

* **Rate Limit Management (API 429):** Implemented an **Exponential Backoff** strategy and a "Batch-to-Individual" fallback mechanism. If the API hits a limit during batch processing, the system automatically switches to individual chunk processing with a controlled delay to ensure 100% data ingestion.
* **Data Integrity (IndexErrors):** Solved a common issue where PDF encoding artifacts caused the Embedding API to return empty results. I implemented a strict character-level cleaning layer to ensure all data sent to the model is valid.
* **Docker Persistence:** Configured specialized volume mapping and file-locking checks to prevent the "Database file is locked" errors common when running SQLite-based databases across Windows/WSL and Docker.

---

## 🛠️ Installation & Setup

### Prerequisites
* Docker & Docker Compose
* Google Gemini API Key (Obtainable via [Google AI Studio](https://aistudio.google.com/))

### Steps
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/ai-study-buddy.git](https://github.com/your-username/ai-study-buddy.git)
    cd ai-study-buddy
    ```
2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```
3.  **Launch the Application:**
    ```bash
    docker-compose up --build
    ```
4.  **Access the UI:**
    Navigate to `http://localhost:8501` in your browser.

---

## 🔮 Future Roadmap
* **Source Citations:** Add page numbers and source snippets to every AI response.
* **Multimodal Support:** Enable image parsing within PDFs (OCR) for charts and diagrams.
* **Conversation Memory:** Implement `ConversationSummaryBufferMemory` for long-term dialogue context.

---

**Developed by Lior Jerbi**