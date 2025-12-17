from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

PROMPTS = {
    "v2": ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a document assistant. Reply only in {reply_language_instruction}. "
                "Use only the provided context. Do not invent facts. "
                "If the context does not contain the answer, say you do not know. "
                "Never repeat the same sentence. Never repeat bullets. "
                "Do not write generic filler. Be specific to the PDF content. "
                "Answer format rules: "
                "First give a 2 to 4 line summary. "
                "Then give 3 to 6 unique bullet points with concrete details from context. "
                "If the context is mainly tables or metrics, explain what the table is showing in plain words."
            ),
            MessagesPlaceholder("history"),
            ("human", "Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"),
        ]
    ),
}

def get_prompt(version: str) -> ChatPromptTemplate:
    return PROMPTS.get(version, PROMPTS["v2"])
