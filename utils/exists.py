# Returns value by speicified key path, else None
def exists(obj, *keys):
  format_keys = "".join(
    list(map(
      lambda key: f"['{key}']",
      keys
    ))
  )
  try:
    return eval(f"obj{format_keys}")
  except Exception:
    return None
