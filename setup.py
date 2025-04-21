import subprocess
import sys


def install_spacy_model():
    print("Installing spaCy model...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    print("spaCy model installed successfully!")


if __name__ == "__main__":
    install_spacy_model()
