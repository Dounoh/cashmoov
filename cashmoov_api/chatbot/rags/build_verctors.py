import faiss
from config.settings import FAISS_PATH
import os
from cashmoov_api.chatbot.tasks import build_vec

FAISS_INDEX = None


def get_index():
    global FAISS_INDEX

    if FAISS_INDEX is None:
        if os.path.exists(FAISS_PATH):
            FAISS_INDEX = faiss.read_index(FAISS_PATH)  
        else:
            build_vec.delay()
            return None
        
    return FAISS_INDEX

