pgmName = "deidentification"
pgmUrl = "https://github.com/jftuga/deidentification"
pgmVersion = "1.0.0"

GENDER_PRONOUNS = {
    "he": "HE/SHE",
    "him": "HIM/HER",
    "his": "HIS/HER",
    "himself": "HIMSELF/HERSELF",
    "she": "HE/SHE",
    "her": "HIS/HER",
    "hers": "HIS/HERS",
    "herself": "HIMSELF/HERSELF",
    "mr.": "",
    "mrs.": "",
    "ms.": ""}

# ALL_CONTRACTIONS = (
#     "it",
#     "that",
#     "what",
#     "there",
#     "here",
#     "let",
#     "how",
#     "where",
#     "who",
#     "when",
#     "one",
#     "somebody",
#     "someone",
#     "something",
#     "nobody",
#     "everyone",
#     "anybody",
#     "nothing",
#     "why",
#     "this",
#     "which")


HTML_BEGIN = """<!DOCTYPE html>
<html>
<head>
<style>
#span1 {
  background: yellow;
  color: black;
  display: inline-block;
  font-weight: bold;
}
#span2 {
  background: turquoise;
  color: black;
  display: inline-block;
  font-weight: bold;
}
#span3 {
  background: pink;
  color: black;
  display: inline-block;
  font-weight: bold;
}
</style>
</head>
<body>
"""

HTML_END = """
</body>
</html>
"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
