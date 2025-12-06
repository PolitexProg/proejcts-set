import json
import sys
from urllib import error, request


def fetch_github_events(username: str):
    """Запрашивает события пользователя с GitHub API."""
    url = f"https://api.github.com/users/{username}/events"
    try:
        with request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data, response.getcode()
    except error.HTTPError as e:
        if e.code == 404:
            print("Ошибка: Пользователь не найден.")
        elif e.code == 403:
            print("Ошибка: Превышен лимит запросов к API (rate limit).")
        else:
            print(f"Ошибка HTTP {e.code}: {e.reason}")
        return None, e.code
    except error.URLError as e:
        print(f"Ошибка сети: {e.reason}")
        return None, None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None, None


def format_event(event: dict) -> str:
    """Преобразует событие в человекочитаемую строку."""
    event_type = event.get("type")
    repo_name = event["repo"]["name"]

    if event_type == "PushEvent":
        # В API нет количества коммитов в PushEvent.payload, но можно взять len(commits) — но его нет.
        # Поэтому просто пишем "Pushed to..."
        return f"Pushed to {repo_name}"

    elif event_type == "IssuesEvent":
        action = event["payload"]["action"]
        issue_number = event["payload"]["issue"]["number"]
        if action == "opened":
            return f"Opened issue #{issue_number} in {repo_name}"
        elif action == "closed":
            return f"Closed issue #{issue_number} in {repo_name}"
        else:
            return f"{action.capitalize()} issue #{issue_number} in {repo_name}"

    elif event_type == "IssueCommentEvent":
        issue_number = event["payload"]["issue"]["number"]
        return f"Commented on issue #{issue_number} in {repo_name}"

    elif event_type == "ForkEvent":
        return f"Forked {repo_name}"

    elif event_type == "WatchEvent":
        return f"Starred {repo_name}"

    elif event_type == "PullRequestEvent":
        action = event["payload"]["action"]
        pr_number = event["payload"]["number"]
        return f"{action.capitalize()} pull request #{pr_number} in {repo_name}"

    else:
        return f"Did something in {repo_name}"  # fallback


def main():
    if len(sys.argv) != 2:
        print("Использование: python github_activity.py <username>")
        sys.exit(1)

    username = sys.argv[1].strip()
    if not username:
        print("Имя пользователя не может быть пустым.")
        sys.exit(1)

    print(f"Получение активности для пользователя: {username}\n")

    data, status = fetch_github_events(username)

    if data is None:
        sys.exit(1)

    if not data:
        print("Нет недавней активности.")
        return

    # Выводим максимум первые 10 событий
    for event in data[:10]:
        line = format_event(event)
        print(f"- {line}")


if __name__ == "__main__":
    main()
