from celery import shared_task
import numpy as np
from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.rags.lezy_model import get_model
from config.settings import FAISS_PATH
import faiss




@shared_task
def save_embedding(slug):
    model = get_model()

    try:
        document = Document.objects.get(slug=slug) 
    except Document.DoesNotExist:
        pass

    text = document.content
    titile = document.title
    vector_text = f"{text} {titile}"
    if document:
        vec = model.encode([vector_text], convert_to_numpy=True)[0]
        vec = vec / np.linalg.norm(vec)  

        document.embedding = vec.tolist()
        document.save()



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




# def add_embeddings(new_docs):
#     """
#     Ajoute des nouveaux documents à l'index existant.
#     new_docs: liste de documents Django avec .embedding
#     """
#     index = get_index()
#     if index is None:
#         build_vec()  # si index n'existe pas, rebuild complet
#         index = get_index()
#         if index is None:
#             return False

#     vectors = np.array([d.embedding for d in new_docs], dtype=np.float32)
#     ids = np.array([d.pk for d in new_docs], dtype=np.int64)

#     index.add_with_ids(vectors, ids)
#     faiss.write_index(index, FAISS_PATH)

#     return True

# def remove_document(doc_id):
#     """
#     Supprime un document de l'index (si nécessaire, après suppression dans la DB)
#     """
#     index = get_index()
#     if index is None:
#         return False

#     if hasattr(index, "remove_ids"):
#         ids = np.array([doc_id], dtype=np.int64)
#         index.remove_ids(ids)
#         faiss.write_index(index, FAISS_PATH)
#         return True
#     return False