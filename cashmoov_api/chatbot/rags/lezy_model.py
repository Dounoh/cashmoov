
MODEL = None


def get_model():
    """ 
    Cette fonction nous permet de charger le model utiliser pour faire le embedding
    une seul fois et le garder dasn une variable gloabal pour eviter de le charger à chaque requette
    pour optimiser le temps de chargement et la consomation de resourse.
    """
    
    from sentence_transformers import SentenceTransformer
    
    global MODEL

    if MODEL is None:
        MODEL = SentenceTransformer('all-MiniLM-L6-v2')

    return MODEL


