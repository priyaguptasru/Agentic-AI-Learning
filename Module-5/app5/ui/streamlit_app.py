import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()

MODULE5_ROOT = CURRENT_FILE.parents[2]
PROJECT_ROOT = MODULE5_ROOT.parent

if str(MODULE5_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE5_ROOT))

import chromadb
import streamlit as st

from app5.services.rag_service import RAGService

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="Multi-Document RAG Assistant",
    page_icon="🤖",
    layout="wide",
)

# ----------------------------------------------------
# Load RAG Service
# ----------------------------------------------------


@st.cache_resource
def load_rag():

    return RAGService()


rag = load_rag()

# ----------------------------------------------------
# Session State
# ----------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []

if "recent_chats" not in st.session_state:

    st.session_state.recent_chats = []

# ----------------------------------------------------
# Load Documents
# ----------------------------------------------------


@st.cache_resource
def get_documents():

    VECTOR_DB = PROJECT_ROOT / "Module-4" / "vector_db"

    client = chromadb.PersistentClient(path=str(VECTOR_DB))

    collection = client.get_collection("documents")

    data = collection.get(include=["metadatas"])

    documents = sorted({metadata["document"] for metadata in data["metadatas"]})

    return documents


# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

with st.sidebar:

    st.title("🤖 RAG Assistant")

    st.divider()

    st.subheader("📄 Loaded Documents")

    try:

        docs = get_documents()

        if docs:

            for doc in docs:

                st.success(doc)

        else:

            st.info("No documents found.")

    except Exception:

        st.warning("Vector database not found.")

    st.divider()

    # ---------------------------------------------

    st.subheader("🕒 Recent Chats")

    if st.session_state.recent_chats:

        for index, chat in enumerate(st.session_state.recent_chats):

            col1, col2 = st.columns([8, 1])

            # -----------------------------
            # Open Chat
            # -----------------------------
            with col1:

                if st.button(
                    f"💬 {chat['title']}",
                    key=f"chat_{index}",
                    use_container_width=True,
                ):

                    # Save current chat before switching
                    if st.session_state.messages:

                        title = "New Chat"

                        for msg in st.session_state.messages:

                            if msg["role"] == "user":

                                title = msg["content"][:30]

                                if len(msg["content"]) > 30:
                                    title += "..."

                                break

                        if not any(
                            c["messages"] == st.session_state.messages
                            for c in st.session_state.recent_chats
                        ):

                            st.session_state.recent_chats.insert(
                                0,
                                {
                                    "title": title,
                                    "messages": st.session_state.messages.copy(),
                                },
                            )

                            st.session_state.recent_chats = (
                                st.session_state.recent_chats[:10]
                            )

                    try:
                        rag.memory.clear()
                    except Exception:
                        pass

                    st.session_state.messages = chat["messages"].copy()

                    st.rerun()

            # -----------------------------
            # Delete Chat
            # -----------------------------
            with col2:

                if st.button(
                    "🗑",
                    key=f"delete_{index}",
                    help="Delete Chat",
                ):

                    deleted_chat = st.session_state.recent_chats.pop(index)

                    if deleted_chat["messages"] == st.session_state.messages:
                        st.session_state.messages = []

                    st.rerun()

    else:

        st.info("No recent chats")

    st.divider()

    # ---------------------------------------------

    if st.button(
        "💬 New Chat",
        use_container_width=True,
    ):

        if st.session_state.messages:

            title = "New Chat"

            for msg in st.session_state.messages:

                if msg["role"] == "user":

                    title = msg["content"][:30]

                    if len(msg["content"]) > 30:
                        title += "..."

                    break

            st.session_state.recent_chats = [
                chat
                for chat in st.session_state.recent_chats
                if chat["messages"] != st.session_state.messages
            ]

            st.session_state.recent_chats.insert(
                0,
                {
                    "title": title,
                    "messages": st.session_state.messages.copy(),
                },
            )

            st.session_state.recent_chats = st.session_state.recent_chats[:10]

        st.session_state.messages = []

        try:
            rag.memory.clear()
        except Exception:
            pass

        st.rerun()

    # ---------------------------------------------

    if st.button(
        "🧹 Clear Cache",
        use_container_width=True,
    ):

        st.cache_resource.clear()

        st.success("Cache Cleared")

# ----------------------------------------------------
# Main Window
# ----------------------------------------------------

st.title("🤖 Multi-Document RAG Assistant")

st.caption("Ask questions about the uploaded documents.")

# ----------------------------------------------------
# Chat History
# ----------------------------------------------------

# if "messages" not in st.session_state:

#     st.session_state.messages = []

# if "recent_chats" not in st.session_state:

#     st.session_state.recent_chats = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ----------------------------------------------------
# Chat Input
# ----------------------------------------------------

question = st.chat_input("Ask anything...")

if question:

    # ---------------------------------------------
    # User Message
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # ---------------------------------------------
    # Assistant Message
    # ---------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = rag.process_question(question)

                # -----------------------------
                # Answer
                # -----------------------------

                st.markdown(response.answer)

                # -----------------------------
                # Confidence
                # -----------------------------

                st.caption(f"🎯 Confidence : {response.confidence:.2f}")

                # -----------------------------
                # Sources
                # -----------------------------

                if response.sources:

                    with st.expander(
                        f"📚 Sources ({len(response.sources)})",
                        expanded=False,
                    ):

                        for index, source in enumerate(
                            response.sources,
                            start=1,
                        ):

                            st.markdown(
                                f"<small><b>📄 Source {index}</b></small>",
                                unsafe_allow_html=True,
                            )

                            st.info(source)

                            st.divider()

                assistant_message = response.answer

            except Exception as e:

                assistant_message = f"❌ Error\n\n{e}"

                st.error(assistant_message)

    # ---------------------------------------------
    # Save Chat History
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message,
        }
    )
