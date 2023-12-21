import sys
import json
import dotenv
import logging
from time import sleep
import concurrent.futures
from utils.exists import exists
from os import getenv, path, curdir
from random import randint, shuffle
from utils.plagiator import request
from utils.split_chunks import split_chunks
from utils.document_parser import DocumentParser

dotenv.load_dotenv(path.abspath(path.join(
  curdir, "configs", ".env"
)))

logging.basicConfig(level=logging.INFO)

document_path = getenv("DOC_PATH") or input(
"""
Enter absolute path to your document
Supported formats:
- .doc
- .docx 
- .pdf 
- .txt
-> """
)
words_per_chunk = int(getenv("WORDS_PER_CHUNK") or 100)
result_target_filename = path.basename(document_path).split(".")[0] + ".json"
results_designation = path.abspath(path.join(
  curdir, 
  "results",
  result_target_filename
))
concurrent_tasks_limit = int(getenv("CONCURRENT_TASKS_LINIT") or 12)
bar_length = 30

parser = DocumentParser()

data = parser.extract_data(document_path)
chunks = split_chunks(data, words_per_chunk)
shuffle(chunks)

results = []

def render_progress_bar(bar_percentage):
  sys.stdout.write('\r')
  sys.stdout.write(
    "Completed: [{:{}}] {:>3}%".format(
      '='*int(bar_percentage/(100.0/bar_length)),
      bar_length, 
      int(bar_percentage)
    )
  )
  sys.stdout.flush()

def test_plagiarism_task(data: str):
  results.append(request(data))

logging.info(f"Checking for plagiarism in {document_path}...")
executor = concurrent.futures.ThreadPoolExecutor(
  max_workers=concurrent_tasks_limit
)
current_progress = 0
total = int(len(chunks))
while len(chunks):
  bar_percentage = 100.0 * current_progress / total
  render_progress_bar(bar_percentage)
  if len(chunks) < concurrent_tasks_limit:
    executor.map(test_plagiarism_task, chunks)
    tasks_created = len(chunks)
  else:
    executor.map(
      test_plagiarism_task, 
      chunks[:concurrent_tasks_limit]
    )
    tasks_created = concurrent_tasks_limit
  executor.shutdown()
  executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=concurrent_tasks_limit
  )
  del chunks[:concurrent_tasks_limit]
  current_progress += tasks_created
render_progress_bar(100)
print()

sum_percentage = 0

for result in results:
  if exists(result, "percent"):
    sum_percentage += float(result["percent"])

average_percent = sum_percentage / len(results)

logging.info(
  f"The average uniqueness of the text is {round(average_percent, 2)}%"
)

logging.info(f"Saving detailed results in {results_designation}.")
with open(results_designation, "w") as results_file:
  results_file.write(json.dumps(results, indent=2, ensure_ascii=False))
  results_file.close()
