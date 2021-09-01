# jira-lazy-mode
## how to use

- install packages with `pip install jira jinja2 PythonGit
- create file `secret.json` that looks like this:

```json
{
    "jira_url": "http://…",
    "login": "…",
    "password": "…"
}
```

- modify `template.tex` as you see fit
- run `python -m jira-lazy-mode`
- then run `xelatex res.tex`
