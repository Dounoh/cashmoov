import numpy as np
from cashmoov_api.chatbot.models import Document
from .lezy_index import get_index
from .lezy_model import get_model
from .prompt_llm import llm_humanise


def search_documents(query_text, top_k=5):
    """
    Recherche les documents les plus proches d'une normalisation embedding avec FAISS.

    """
    model = get_model()

    query_vector = model.encode(query_text, convert_to_numpy=True)
    query_vector = query_vector / np.linalg.norm(query_vector)

    index = get_index()
    if index is None:
        return [], []

    q = np.array([query_vector], dtype=np.float32)
    distances, doc_ids = index.search(q, top_k) 
    docs = Document.objects.filter(pk__in=doc_ids[0])

    list_docs = [f"{do.title} : {do.content}" for do in docs]

    # response_llm = llm_humanise(query=query_text, context=list_docs)

    # return response_llm
    
    return reversed(list_docs)
