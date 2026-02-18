import requests
import streamlit as st

st.set_page_config(page_title="Legal Doc AI Demo", layout="wide")
st.title("⚖️ Legal Doc AI Pipeline Demo")

api_base = st.sidebar.text_input("API Base URL", value="http://localhost:8000")
api_key = st.sidebar.text_input("API Key (optional)", value="", type="password")


def headers() -> dict:
    return {"X-API-Key": api_key} if api_key else {}


if st.sidebar.button("Check Health"):
    r = requests.get(f"{api_base}/health", timeout=10, headers=headers())
    if r.ok:
        st.sidebar.success("API reachable")
        st.sidebar.json(r.json())
    else:
        st.sidebar.error(r.text)

ingest_tab, retrieve_tab, analyze_tab, qa_tab, audit_tab = st.tabs(
    ["Ingest", "Retrieve", "Analyze Text", "Grounded Q&A", "Audit"]
)

with ingest_tab:
    st.subheader("1) Upload document")
    uploaded = st.file_uploader("Upload txt/pdf/image", type=["txt", "pdf", "png", "jpg", "jpeg"])

    if uploaded is not None and st.button("Ingest"):
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
        r = requests.post(f"{api_base}/v1/ingest", files=files, timeout=60, headers=headers())
        if r.ok:
            st.success("Ingest complete")
            st.json(r.json())
        else:
            st.error(r.text)

with retrieve_tab:
    st.subheader("2) Retrieve")
    query = st.text_input("Query", value="contract parties and obligations")
    top_k = st.slider("Top K", min_value=1, max_value=10, value=5)

    if st.button("Search"):
        r = requests.post(
            f"{api_base}/v1/retrieve",
            json={"query": query, "top_k": top_k},
            timeout=30,
            headers=headers(),
        )
        if r.ok:
            data = r.json()
            if not data["results"]:
                st.info("No results yet. Try ingesting docs first.")
            for i, item in enumerate(data["results"], start=1):
                with st.expander(
                    f"#{i} | score={item['score']:.4f} | {item['metadata'].get('classification', '-')}"
                ):
                    st.write(item["text"])
                    st.caption(item["metadata"])
        else:
            st.error(r.text)

with analyze_tab:
    st.subheader("3) Analyze Raw Legal Text")
    entity_text = st.text_area(
        "Paste legal text",
        value=(
            "This agreement is made between Party A and Party B on 12/03/2026. "
            "Party A shall pay USD 5,000 within 15 days and keep confidentiality."
        ),
        height=180,
    )
    if st.button("Analyze"):
        r = requests.post(
            f"{api_base}/v1/analyze",
            json={"text": entity_text},
            timeout=45,
            headers=headers(),
        )
        if r.ok:
            st.json(r.json())
        else:
            st.error(r.text)

with qa_tab:
    st.subheader("4) Grounded Q&A over Indexed Documents")
    question = st.text_area(
        "Ask a question",
        value="What are the payment obligations and deadlines?",
        height=120,
    )
    qa_top_k = st.slider("Context Top K", min_value=1, max_value=10, value=5, key="qa_top_k")

    if st.button("Ask"):
        r = requests.post(
            f"{api_base}/v1/qa",
            json={"question": question, "top_k": qa_top_k},
            timeout=45,
            headers=headers(),
        )
        if r.ok:
            data = r.json()
            st.markdown("**Answer**")
            st.write(data["answer"])
            st.markdown("**Citations**")
            st.code("\n".join(data.get("citations", [])) or "No citations")
        else:
            st.error(r.text)

with audit_tab:
    st.subheader("5) Audit Trail")
    limit = st.slider("Event limit", min_value=5, max_value=100, value=20)
    if st.button("Load Audit Events"):
        r = requests.get(f"{api_base}/v1/audit", params={"limit": limit}, timeout=30, headers=headers())
        if r.ok:
            st.json(r.json())
        else:
            st.error(r.text)
