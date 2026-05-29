# jira-cli

Operate Caidao's private Jira instance via the installed
[ankitpokhrel/jira-cli](https://github.com/ankitpokhrel/jira-cli) command.

## Configuration

| Variable           | Required | Description                                                         |
| ------------------ | -------- | ------------------------------------------------------------------- |
| `JIRA_API_TOKEN`   | Yes      | Jira password for basic auth, or Personal Access Token if available |
| `JIRA_AUTH_TYPE`   | No       | Set to `bearer` when using a Personal Access Token                  |
| `JIRA_CONFIG_FILE` | No       | Alternate config path for multiple Jira contexts                    |

Default server:

```text
http://jira.caidaocloud.com:8080/
```

First-time local setup with username/password:

```bash
export JIRA_API_TOKEN="<jira-password>"
```

```bash
jira init \
  --installation local \
  --server "http://jira.caidaocloud.com:8080/" \
  --login "<jira-username-or-email>" \
  --auth-type basic \
  --project "<default-project-key>"
```

If `jira init` fails during metadata generation after login succeeds, use a
manual config with `installation: Local` (capital `L`) and store the password in
macOS Keychain under service `jira-cli`.

## Common Commands

```bash
jira me
jira serverinfo
jira project list
jira issue list --plain --no-truncate
jira issue view ISSUE-123 --plain --comments 5
jira issue create -p PRJ -t Task -s "Summary" -b "Description" --no-input --raw
jira issue comment add ISSUE-123 "Comment" --no-input
jira issue move ISSUE-123 "In Progress"
```

## RapidBoard Planning Notes

For Jira 8.3 RapidBoard pages, use the page's GreenHopper planning endpoint when
the CLI sprint list does not match the web UI. Example for `2.0研发看板`
(`rapidView=45`):

```bash
curl -fsS -u "$(jira me):$(security find-generic-password -s jira-cli -a "$(jira me)" -w)" \
  "http://jira.caidaocloud.com:8080/rest/greenhopper/1.0/xboard/plan/backlog/data.json?rapidViewId=45&selectedProjectKey=DEV"
```

The sprint names may be `Dev Sprint ...` rather than uppercase `DEV Sprint ...`.
