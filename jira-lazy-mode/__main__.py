from jira import JIRA
from git import Repo
from requests import Session
from requests.auth import HTTPBasicAuth
import datetime
from .secrets import Secrets
from jinja2 import Template

jira = JIRA(Secrets.jira_url, basic_auth=(Secrets.login, Secrets.password))
session = Session()

#search_from = datetime.date.today() - datetime.timedelta(days=40)
search_from = datetime.datetime.strptime(input("Odkąd: "), "%Y-%m-%d").date() - datetime.timedelta(days=1)
print("Searching from", search_from.isoformat())

issues = jira.search_issues(
        r'worklogDate > {} and worklogDate < endOfDay() and worklogAuthor={}'.format(
            search_from.isoformat(),
            Secrets.login
        ),
        fields="worklog,summary",
        maxResults=-1
    )

logs = list()
x = 1
for issue in issues:
    try:
        print("\33[2K({}/{}) {}".format(
                x,
                len(issues),
                issue.fields.summary
            ), end="\r")
        x += 1
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
print()
logs.sort(key=lambda x: x[1])

gaps = list()

timeInDay = datetime.timedelta()
timeCarry = datetime.timedelta()
timeSum = datetime.timedelta()
days = []
hourSum = 0

prevData = None
for log, started_at, issue in logs:
    if prevData:
        if prevData["started_at"].date() != started_at.date():
            hours = timeInDay.seconds // 3600
            days.append({
                "date": prevData["started_at"].date(),
                "amount": hours
            })
            hourSum += hours
            timeInDay -= datetime.timedelta(hours=hours)
            timeSum += timeCarry
            timeCarry = datetime.timedelta()
            print("----", started_at.date().isoformat(), "----", sep="\t")
        elif prevData["end_time"] != started_at:
            print(
                "Gap #{}".format(len(gaps))
            )
            gaps.append((prevData["end_time"], started_at))
    else:
        print("----", started_at.date().isoformat(), "----", sep="\t")
    end_time = started_at + datetime.timedelta(
            seconds=log["timeSpentSeconds"]
        )
    timeInDay += datetime.timedelta(
            seconds=log["timeSpentSeconds"]
        )
    timeCarry += datetime.timedelta(
            seconds=log["timeSpentSeconds"]
        )

    prevData = {
        "started_at" : started_at,
        "end_time" : end_time,
        "log" : log,
        "issue" : issue
    }
    """
    print(
            "{:<10.10}".format(issue.key),
            "{:<35.35}".format(issue.fields.summary.strip()),
            "{}:".format(log["author"]["displayName"]), 
            "{:2d}:{:02d} - {:2d}:{:02d}".format(
                started_at.hour, started_at.minute,
                end_time.hour, end_time.minute
            ), 
            log["comment"].strip(), 
            sep="\t"
    )
"""
hours = timeInDay.seconds // 3600
days.append({
    "date": prevData["started_at"].date(),
    "amount": hours
})
print("Spent time", hours)
hourSum += hours
timeSum += timeCarry
if timeCarry.seconds > 0:
    print(timeCarry.seconds)
    days[-1]["amount"] += 1
    hourSum += 1
print("Total", timeSum, ";", hourSum, hourSum * 27)

template = Template(open("template.tex").read())
result = template.render(lines=days, total = hourSum)
resultFile = open("res.tex", "w+")
resultFile.write(result)
resultFile.close()

"""
repo = Repo("/home/hakiergrzonzo/Desktop/apa/weboweSO/WEBSO")
assert not repo.bare
if len(gaps) > 0:
    print("--- Commity dla dziur: ---")
    stop_at = gaps[0][0]
    commit = repo.head.commit
    while True:
        commitDate = datetime.datetime.fromtimestamp(commit.committed_date)
        if commitDate.timestamp() < stop_at.timestamp():
            break
        print(
                commit.message.strip(),
                commit.author,
            "{:2d}:{:02d}".format(
                commitDate.hour, commitDate.minute,
            )
        )
        if len(commit.parents) > 0:
            commit = commit.parents[0]
        else:
            break
"""
