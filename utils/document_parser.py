import re
import textract
import docx2txt
from pathlib import Path
from PyPDF2 import PdfReader
from unicodedata import normalize

class DocumentParser:
  def __init__(self):
    pass

  def extract_data(self, filepath):
    try:
      extension = Path(filepath).suffix
      extract_method = self.__ext_binds__(extension)
      result = self.__normilize__(extract_method(filepath))
      if result is None:
        raise Exception(
          f"cannot extract text from '{file.actual_path}' - returned 'None'"
        )
      return result
    except Exception as err:
      raise Exception(
        f"extraction error: {err}"
      )

  def __ext_binds__(self, ext):
    binds = {
      ".pdf": self.__extract_text_from_pdf__,
      ".docx": self.__extract_text_from_docx__,
      ".doc": self.__extract_text_from_doc__,
      ".txt": self.__extract_text_from_txt__
    }
    if ext not in binds:
      raise Exception(f"Unsupportable document type: '{ext}'")
    return binds[ext]

  def __normilize__(self, text):
    try:
      return normalize(
        "NFKC", 
        re.sub(
          "\u0000", 
          "", 
          re.sub(
            "\s+|\n+",
            " ",
            text
          )
        )
      )
    except Exception as err:
      raise Exception(f"normalization error: {repr(err)}")

  def __extract_text_from_doc__(self, doc_path):
    try:
      return textract.process(doc_path).decode('utf-8')
    except KeyError:
      return None

  def __extract_text_from_docx__(self, docx_path):
    try:
      temp = docx2txt.process(docx_path)
      text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
      return ' '.join(text)
    except KeyError:
      return None

  def __extract_text_from_pdf__(self, pdf_path: str):
    try:
      reader = PdfReader(pdf_path)
      number_of_pages = len(reader.pages)
      text = ""
      page = reader.pages[0]
      for page in reader.pages:
        text += page.extract_text()
      return text
    except Exception:
      return None

  def __extract_text_from_txt__(self, txt_path):
    try:
      with open(txt_path, "r") as f:
        return "\n".join(str(i) for i in f.readlines())
    except Exception:
      return None
