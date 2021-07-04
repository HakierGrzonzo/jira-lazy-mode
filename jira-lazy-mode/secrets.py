from .constants import SECRET_FILE
import json

class Secrets:
    password = None
    login = None
    jira_url = None
    @classmethod
    def init(cls):
        secretFile = json.load(open(SECRET_FILE))
        cls.password = secretFile["password"]
        cls.login = secretFile["login"]
        cls.jira_url = secretFile["jira_url"]

Secrets.init()

