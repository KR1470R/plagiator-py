import sys
import json
import dotenv
import logging
from time import sleep
import concurrent.futures
from random import randint
from utils.exists import exists
from os import getenv, path, curdir, mkdir
from utils.plagiator import Plagiator
from utils.split_chunks import split_chunks
from utils.document_parser import DocumentParser

dotenv.load_dotenv(path.abspath(path.join(
  curdir, "configs", ".env"
)))

logging.basicConfig(level=logging.INFO)

try:
  docpath_arg = sys.argv[1]
except Exception:
  docpath_arg = None

document_path = docpath_arg or getenv("DOC_PATH") or input(
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
result_folder = path.join(curdir, "results")
if not path.exists(result_folder):
  mkdir(result_folder)
results_designation = path.abspath(path.join(
  result_folder,
  result_target_filename
))
concurrent_tasks_limit = int(getenv("CONCURRENT_TASKS_LIMIT") or 5)
bar_length = 30

parser = DocumentParser()
plagiator = Plagiator()

data = parser.extract_data(document_path)

if data is None:
  raise Exception("Unable to extact text from the document.")

chunks = split_chunks(data, words_per_chunk)
total = int(len(chunks))

results = []

def render_progress_bar(bar_percentage, completed, nl=False):
  sys.stdout.write('\r')
  sys.stdout.write(
    "Chunks completed: [{:{}}] {}/{}{}".format(
      '='*int(bar_percentage/(100.0/bar_length)),
      bar_length, 
      completed,
      total,
      "\n" if nl else ""
    )
  )
  sys.stdout.flush()

def test_plagiarism_task(data: str):
  processed = plagiator.process(data)
  if processed: results.append(processed)

logging.info(f"Checking for plagiarism in {document_path}...")
executor = concurrent.futures.ThreadPoolExecutor(
  max_workers=concurrent_tasks_limit
)
current_progress = 0
while len(chunks):
  bar_percentage = 100.0 * current_progress / total
  render_progress_bar(bar_percentage, current_progress)
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
render_progress_bar(100, total, True)

if len(results) == 0:
  logging.error("There are no results.")

sum_percentage = 0

for result in results:
  if exists(result, "percent"):
    sum_percentage += float(result["percent"])

average_percent = sum_percentage / len(results)

logging.info(
  f"The average uniqueness of the text is {round(average_percent, 2)}%"
)

logging.info(f"Saving detailed results to {results_designation}...")
with open(results_designation, "w") as results_file:
  results_file.write(json.dumps(results, indent=2, ensure_ascii=False))
  results_file.close()

