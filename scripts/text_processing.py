from nltk.tokenize import TreebankWordTokenizer


def preprocess_text(text):
    tokenizer = TreebankWordTokenizer()
    tokens = tokenizer.tokenize(text.lower())  # Tokenize text
    return " ".join(tokens)  # Convert list back to string
