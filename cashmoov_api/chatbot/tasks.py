from celery import shared_task
import numpy as np
from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.rags.lezy_model import get_model
from config.settings import FAISS_PATH
import faiss
from cashmoov_api.chatbot.rags.lezy_index import FAISS_INDEX
import os

@shared_task
def save_embedding(slug):
    """  
        La fonction asynchrone pour calculer le embedding des mots et 
        ajouter sa normalisation en db + indexation FAISS immédiate
    """
    model = get_model()

    try:
        document = Document.objects.get(slug=slug) 
    except Document.DoesNotExist:
        return

    text = document.content
    title = document.title
    vector_text = f"{text} {title}"

    vec = model.encode([vector_text], convert_to_numpy=True)[0]  # (dim,)
    vec = vec / np.linalg.norm(vec) 
    document.embedding = vec.tolist()
    document.save()

    try:
        index = faiss.read_index(FAISS_PATH)
    except:
        dimension = vec.shape[0]
        base = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIDMap(base)

    index.add_with_ids(
        np.array([vec], dtype=np.float32),         
        np.array([document.id], dtype=np.int64)   
    )

    faiss.write_index(index, FAISS_PATH)

    global FAISS_INDEX
    FAISS_INDEX = index

    return True



@shared_task
def build_vec():
    documents = Document.objects.exclude(embedding=None).order_by('id')
    normalized = np.array(
        [document.embedding for document in documents], 
        dtype=np.float32
    )
    ids = np.array([d.pk for d in documents], dtype=np.int64)

    dimansion = normalized.shape[1]
    index = faiss.IndexFlatL2(dimansion)
    index = faiss.IndexIDMap(index)

    # index.add(normalized)
    index.add_with_ids(normalized, ids)
    faiss.write_index(index, FAISS_PATH)
    
    return True




# @shared_task
# def delete_from_faiss(document_id):
#     from .faiss_utils import FAISS_INDEX

#     if os.path.exists(FAISS_PATH):
#         index = faiss.read_index(FAISS_PATH)
#     else:
#         return False

#     try:
#         index.remove_ids(np.array([document_id], dtype=np.int64))
#     except Exception as e:
#         print(f"Erreur suppression FAISS: {e}")
#         return False

#     faiss.write_index(index, FAISS_PATH)

#     # Mettre à jour le cache mémoire
#     global FAISS_INDEX
#     FAISS_INDEX = index

#     return True



# @shared_task
# def save_embedding(slug):
#     """  
#         La fonction asynchrone pour calculer le embedding des mots et 
#         ajouter sa normalisation en db
#     """
#     model = get_model()

#     try:
#         document = Document.objects.get(slug=slug) 
#     except Document.DoesNotExist:
#         pass

#     if document:
#         text = document.content
#         titile = document.title
#         vector_text = f"{text} {titile}"

#         vec = model.encode([vector_text], convert_to_numpy=True)[0]
#         vec = vec / np.linalg.norm(vec)  

#         document.embedding = vec.tolist()
#         document.save()

#         return 





