import os
import glob
import gensim
from gensim import corpora
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from config import PROCESSED_DATA_DIR, RAW_DATA_DIR

# Download NLTK data files
nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def preprocess(text):
    tokens = word_tokenize(text.lower())
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    return tokens

def chunk_data_with_lda(texts, num_topics=5, chunks_per_topic=3):
    tokenized_texts = [preprocess(text) for text in texts]
    dictionary = corpora.Dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]

    lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

    topic_chunks = [[] for _ in range(num_topics)]
    for i, text in enumerate(texts):
        bow = dictionary.doc2bow(preprocess(text))
        topics = lda_model.get_document_topics(bow)
        dominant_topic = max(topics, key=lambda x: x[1])[0]
        topic_chunks[dominant_topic].append(text)

    final_chunks = []
    for topic_chunk in topic_chunks:
        if len(topic_chunk) > 0:
            chunk_size = max(1, len(topic_chunk) // chunks_per_topic)
            for i in range(0, len(topic_chunk), chunk_size):
                final_chunks.append(' '.join(topic_chunk[i:i + chunk_size]))

    return final_chunks

def process_files():
    texts = []
    file_paths = []

    for filepath in glob.glob(os.path.join(RAW_DATA_DIR, '**/*.txt'), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as file:
            texts.append(file.read())
            file_paths.append(filepath)

    chunks = chunk_data_with_lda(texts)
    save_chunks(file_paths, chunks)

def save_chunks(file_paths, chunks):
    for filepath, chunk in zip(file_paths, chunks):
        relative_path = os.path.relpath(filepath, RAW_DATA_DIR)
        new_dir = os.path.join(PROCESSED_DATA_DIR, os.path.dirname(relative_path))
        os.makedirs(new_dir, exist_ok=True)
        chunk_filename = os.path.join(new_dir, f"{os.path.basename(filepath)}_chunk.txt")
        with open(chunk_filename, 'w', encoding='utf-8') as file:
            file.write(chunk)

def main():
    process_files()

if __name__ == "__main__":
    main()
