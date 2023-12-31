import json
import logging
import requests
from .exists import exists
from configs.edupirdie import API_URI, HEADERS
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

class Plagiator:
  def __init__(self):
    self.session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=10000, pool_maxsize=10000)
    self.session.mount("https://", adapter)
    software_names = [software_name.value for software_name in SoftwareName]
    operating_systems = [operating_system.value for operating_system in OperatingSystem]
    self.user_agent_rotator = UserAgent(
      software_names=software_names, 
      operating_systems=operating_systems, 
      limit=1000
    )

  def concretize_response(self, response: dict):
    if exists(response, "error") and response["error"]:
      return response
    del response["error"]
    del response["error_code"]
    if len(response["title"]) == 0:
      del response["title"]
    words = response["text"].split(" ")
    if exists(response, "highlight") and len(response["highlight"]):
      highlight_text = []
      for span in response["highlight"]:
        span = list(map(int, span))
        selected_words = words[span[0]] if (
            span[0] == span[1]
          ) else words[span[0]:span[1]]
        if isinstance(selected_words, list):
          selected_words = " ".join(selected_words)
        highlight_text.append(selected_words)
      response["highlight"] = highlight_text
    if exists(response, "matches") and len(response["matches"]):
      matches_highlight = []
      for match in response["matches"]:
        matched_highlight_text = []
        for match_span in match["highlight"]:
          match_span = list(map(int, match_span))
          selected_words = words[match_span[0]] if (
              match_span[0] == match_span[1]
            ) else words[match_span[0]:match_span[1]]
          if isinstance(selected_words, list):
            selected_words = " ".join(selected_words)
          matched_highlight_text.append(selected_words)
        matches_highlight.append({**match, "highlight": matched_highlight_text})
      response["matches"] = matches_highlight
    return response

  def __request__(self, text: str, title: str = None):
    return self.session.post(
      API_URI, 
      headers={
        **HEADERS,
        "User-Agent": self.user_agent_rotator.get_random_user_agent()
      },
      params={
        "is_free": "true",
        "plagchecker_locale": "ua",
        "title": title or "",
        "text": text
      }
    )

  def process(self, text: str, title: str = None):
    try:
      api_response = self.__request__(text, title)
      api_response.raise_for_status()
      jsonify = json.loads(api_response.content.decode("unicode-escape"))
      error_code = jsonify["error_code"]
      if error_code and int(error_code) > 0:
        if exists(jsonify, "error"):
          message = jsonify["error"]
        elif exists(jsonify, "message"):
          message = jsonify["message"]
        else: message = ""
        logging.warning(
          f"REQUEST RETURNED ERROR WITH STATUS {error_code}: " +\
            f"{message}\n" +\
              f"{text}"
        )
    except Exception as err:
      skip_err_msg = "The action you just performed triggered the security solution."
      if skip_err_msg in api_response.decode():
        return
      logging.error(f"REQUEST ERROR: {repr(err)}:{api_response.content}")
      try:
        return {"error": api_response.content.decode()}
      except Exception:
        return {"error": "something went wrong"}
    return self.concretize_response(jsonify)

