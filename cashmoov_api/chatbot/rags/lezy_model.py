import torch
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "intfloat/multilingual-e5-base"

MODEL = None
TOKENIZER = None


def get_model():
    """
    Charge le modèle et le tokenizer E5 une seule fois et les garde en mémoire.
    
    Retourne : (model, tokenizer)
    """
    global MODEL, TOKENIZER

    if MODEL is None or TOKENIZER is None:
        TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
        MODEL = AutoModel.from_pretrained(MODEL_NAME)
        MODEL.eval() 
    
    return MODEL, TOKENIZER
