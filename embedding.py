from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer("jhgan/ko-sroberta-multitask")

    def embed(self, texts: list[str]):
        return self.model.encode(texts, show_progress_bar=True)