import os
import requests
import streamlit as st
from typing import Dict, Any, List

#API = st.secrets.get("API_URL") or os.getenv("API_URL") or "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF Insight Assistant Pro", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1200px; }
    .stChatMessage { max-width: 820px; }
    .stChatMessage p { line-height: 1.55; font-size: 1.02rem; }
    .muted { color: rgba(255,255,255,0.65); font-size: 0.92rem; }
    .card {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 14px 14px;
        background: rgba(255,255,255,0.03);
    }
    .chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.16);
        font-size: 0.85rem;
        color: rgba(255,255,255,0.75);
        margin-right: 6px;
        margin-top: 6px;
        background: rgba(255,255,255,0.02);
    }
    .source-title { font-weight: 650; margin-bottom: 6px; }
    </style>
    """,
    unsafe_allow_html=True
)

def api_get(path: str, timeout: int = 60):
    return requests.get(f"{API}{path}", timeout=timeout)

def api_post_json(path: str, payload: dict, timeout: int = 300):
    return requests.post(f"{API}{path}", json=payload, timeout=timeout)

def api_post_file(path: str, filename: str, file_bytes: bytes, timeout: int = 900):
    files = {"file": (filename, file_bytes, "application/pdf")}
    return requests.post(f"{API}{path}", files=files, timeout=timeout)

def load_documents() -> List[Dict[str, Any]]:
    r = api_get("/documents", timeout=60)
    r.raise_for_status()
    return r.json().get("docs", [])

def ensure_state():
    st.session_state.setdefault("docs", [])
    st.session_state.setdefault("doc_id", "")
    st.session_state.setdefault("session_id", "default")
    st.session_state.setdefault("top_k", 5)
    st.session_state.setdefault("language", "bn")
    st.session_state.setdefault("messages", [])

ensure_state()

st.markdown("## PDF Insight Assistant Pro")
st.markdown('<div class="muted">Upload a PDF, then chat with it. Answers include page sources.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.caption(f"Backend API: {API}")

    st.markdown("### Upload")
    st.markdown('<div class="muted">Backend limit is 25 MB. Keep PDFs smaller for faster indexing.</div>', unsafe_allow_html=True)
    pdf = st.file_uploader("Select a PDF", type=["pdf"])

    if st.button("Upload and index", use_container_width=True):
        if pdf is None:
            st.error("Please select a PDF first.")
        else:
            with st.spinner("Uploading and indexing"):
                res = api_post_file("/upload", pdf.name, pdf.getvalue(), timeout=1200)

            if res.status_code != 200:
                st.error(f"Upload failed, status {res.status_code}")
                st.text(res.text[:800])
                st.stop()
            else:
                data = res.json()
                st.success("Upload done")

                st.session_state["doc_id"] = data.get("doc_id", "")
                st.session_state["docs"] = load_documents()

                if st.session_state["docs"]:
                    st.session_state["doc_id"] = st.session_state["docs"][0].get(
                        "doc_id", st.session_state["doc_id"]
                    )
                st.rerun()

    st.write("")
    st.markdown("### Documents")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Refresh", use_container_width=True):
            try:
                st.session_state["docs"] = load_documents()
            except Exception as e:
                st.error(str(e))
    with c2:
        if st.button("Clear chat", use_container_width=True):
            st.session_state["messages"] = []

    if not st.session_state["docs"]:
        try:
            st.session_state["docs"] = load_documents()
        except Exception:
            st.session_state["docs"] = []

    docs = st.session_state["docs"]

    def label(d: Dict[str, Any]) -> str:
        return f'{d.get("filename","unknown")} , chunks {d.get("chunks",0)} , {d.get("created_at","")}'

    label_to_id = {label(d): d.get("doc_id","") for d in docs}
    options = list(label_to_id.keys())

    if options:
        current_label = None
        for k, v in label_to_id.items():
            if v == st.session_state["doc_id"]:
                current_label = k
                break
        if current_label is None:
            current_label = options[0]
            st.session_state["doc_id"] = label_to_id[current_label]

        selected = st.selectbox(
            "Select a document",
            options=options,
            index=options.index(current_label) if current_label in options else 0
        )
        st.session_state["doc_id"] = label_to_id[selected]

    st.write("")
    st.markdown("### Settings")
    st.session_state["session_id"] = st.text_input("Session id", value=st.session_state["session_id"])
    st.session_state["top_k"] = st.slider("Top K chunks", 1, 12, int(st.session_state["top_k"]))

    lang_label = "Bangla" if st.session_state["language"] == "bn" else "English"
    lang_choice = st.selectbox(
        "Answer language",
        options=["Bangla", "English"],
        index=0 if lang_label == "Bangla" else 1
    )
    st.session_state["language"] = "bn" if lang_choice == "Bangla" else "en"

doc_id = st.session_state["doc_id"]

if not doc_id:
    st.info("Upload a PDF or select one from the sidebar.")
else:
    active_doc = next((d for d in st.session_state["docs"] if d.get("doc_id") == doc_id), None)

    st.markdown(
        f"""
        <div class="card">
            <div class="muted">Active document</div>
            <div style="font-size:1.02rem; font-weight:600;">{active_doc.get("filename","") if active_doc else ""}</div>
            <div class="chip">doc_id {doc_id}</div>
            <div class="chip">chunks {active_doc.get("chunks",0) if active_doc else 0}</div>
            <div class="chip">top_k {int(st.session_state["top_k"])}</div>
            <div class="chip">session {st.session_state["session_id"]}</div>
            <div class="chip">language {st.session_state["language"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.write(m["content"])
            if m.get("sources"):
                with st.expander("Sources"):
                    for s in m["sources"]:
                        page = s.get("page", None)
                        src = s.get("source", "")
                        snippet = (s.get("snippet", "") or "").strip()
                        if len(snippet) > 320:
                            snippet = snippet[:320] + "..."
                        st.markdown(
                            f"""
                            <div class="card">
                                <div class="source-title">Page {page}</div>
                                <div class="muted">{src}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.code(snippet)

    user_text = st.chat_input("Ask a question about the selected PDF")
    if user_text:
        st.session_state["messages"].append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.write(user_text)

        payload = {
            "doc_id": doc_id,
            "session_id": st.session_state["session_id"],
            "question": user_text,
            "top_k": int(st.session_state["top_k"]),
            "language": st.session_state["language"],
        }

        with st.chat_message("assistant"):
            with st.spinner("Thinking"):
                r = api_post_json("/ask", payload, timeout=600)

            if r.status_code != 200:
                st.error(f"Ask failed, status {r.status_code}")
                st.text(r.text[:800])
            else:
                data = r.json()
                answer = data.get("answer", "")
                sources = data.get("sources", [])
                st.write(answer)

                if sources:
                    with st.expander("Sources"):
                        for s in sources:
                            page = s.get("page", None)
                            src = s.get("source", "")
                            snippet = (s.get("snippet", "") or "").strip()
                            if len(snippet) > 320:
                                snippet = snippet[:320] + "..."
                            st.markdown(
                                f"""
                                <div class="card">
                                    <div class="source-title">Page {page}</div>
                                    <div class="muted">{src}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.code(snippet)

                st.session_state["messages"].append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
