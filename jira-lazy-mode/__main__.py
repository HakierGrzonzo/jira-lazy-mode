from jira import JIRA
from requests import Session
from requests.auth import HTTPBasicAuth
import datetime
from .secrets import Secrets

jira = JIRA(Secrets.jira_url, basic_auth=(Secrets.login, Secrets.password))
session = Session()

search_from = datetime.date.today() - datetime.timedelta(days=7)

issues = jira.search_issues(
        r'worklogDate > {} and worklogDate < endOfDay() and worklogAuthor={}'.format(
            search_from.isoformat(),
            Secrets.login
        ),
        fields="worklog,summary",
        maxResults=-1
    )

logs = list()

for issue in issues:
    try:
        print(issue.fields.summary)
        allWorklogs = session.get(
                Secrets.jira_url + "/rest/api/2/issue/{}/worklog".format(
                    issue.key
                ),
                auth=HTTPBasicAuth(Secrets.login, Secrets.password)
            ) 
        for worklog in allWorklogs.json()["worklogs"]:
            started_at = datetime.datetime.strptime(
                    worklog["started"], 
                    '%Y-%m-%dT%H:%M:%S.%f%z'
            )
            if (
                    started_at.date() > search_from and
                    worklog["author"]["name"] == Secrets.login
                ):
                    logs.append((worklog, started_at, issue))
    except Exception as e:
        print("Skiping {} because {}".format(issue.key, e))

logs.sort(key=lambda x: x[1])

for log, started_at, issue in logs:
    end_time = started_at + datetime.timedelta(
            seconds=log["timeSpentSeconds"]
        )
    print(
            issue.key,
            issue.fields.summary.strip(),
            "{}:".format(log["author"]["displayName"]), 
            "{:2d}:{:02d} - {:2d}:{:02d}".format(
                started_at.hour, started_at.minute,
                end_time.hour, end_time.minute
            ), 
            log["comment"].strip(), 
            sep="\t"
    )
    

