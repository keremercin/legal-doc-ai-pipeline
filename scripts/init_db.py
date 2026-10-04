from legal_doc_ai.db import init_db

if __name__ == "__main__":
    init_db()
    print("DB initialized (tables + vector extension ensured).")
