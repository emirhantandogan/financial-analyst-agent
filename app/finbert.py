from transformers import pipeline


finbert = pipeline(
    "text-classification",
    model="ProsusAI/finbert"
)


def analyze(text):
    results = finbert(text, top_k=None)

    scores = {}

    for result in results:
        scores[result["label"]] = result["score"]

    return scores