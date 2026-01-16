
MODEL = None


def get_model():
    from sentence_transformers import SentenceTransformer
    global MODEL

    if MODEL is None:
        MODEL = SentenceTransformer('all-MiniLM-L6-v2')

    return MODEL



# # lezy_model.py
# import os
# from sentence_transformers import SentenceTransformer

# MODEL = None

# def get_model():
#     global MODEL
    
#     if MODEL is None:
#         # Essaie d'abord le modèle local (plus rapide)
#         local_path = "/app/local_model"
#         if os.path.exists(local_path):
#             MODEL = SentenceTransformer(local_path)
#         else:
#             # Fallback au cache système
#             MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    
#     return MODEL