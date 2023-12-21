import logging

def split_chunks(text:str, words_per_chunk: int = 100):
  words = text.split(" ")
  logging.info(f"Words counted: {len(words)}")
  logging.info(f"Words per chunk: {words_per_chunk}")
  chunks = []

  if len(words) <= words_per_chunk:
    chunks.append[words]
  else:
    while len(words):
      current_words_len = len(words)
      if current_words_len <= words_per_chunk:
        chunks.append(" ".join(words[0:current_words_len]))
        del words[0:current_words_len]
      else:
        chunks.append(" ".join(words[0:words_per_chunk]))
        del words[0:words_per_chunk]

  logging.info(f"Splitted into {len(chunks)} chunks")

  return chunks
