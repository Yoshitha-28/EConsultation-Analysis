import yake

kw_extractor = yake.KeywordExtractor(n=3, dedupLim=0.9, top=10, features=None)

def get_keywords(text: str) -> list:
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]