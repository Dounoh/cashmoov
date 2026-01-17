import faiss
from config.settings import FAISS_PATH
import os

FAISS_INDEX = None


def get_index():
    global FAISS_INDEX

    if FAISS_INDEX is None:
        if os.path.exists(FAISS_PATH):
            FAISS_INDEX = faiss.read_index(FAISS_PATH)  
        else:
            from cashmoov_api.chatbot.tasks import build_vec
            build_vec.delay()
            return None
        
    return FAISS_INDEX

