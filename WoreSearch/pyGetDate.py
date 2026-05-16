import http.client
import json
import sys

headers = {
    "X-API-KEY": "25eebc1810a1c4c92ad09dd1d5ef7499ca216576",
    "Content-Type": "application/json"
}


def search_google(query):
    connection = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query,
        "gl" : "eg"
    })

    connection.request("POST", "/search", payload, headers)
    response = connection.getresponse()
    data = response.read().decode("utf-8")
    connection.close()

    return response.status, data


def shorten(text, width):
    text = " ".join(str(text or "").split())
    if len(text) <= width:
        return text.ljust(width)

    return text[:width - 3] + "..."


def print_table(results):
    columns = [
        ("#", 3),
        ("Title", 35),
        ("Link", 45),
        ("Snippet", 55),
    ]
    separator = "+".join("-" * (width + 2) for _, width in columns)
    header = "|".join(f" {name.ljust(width)} " for name, width in columns)

    print(separator)
    print(header)
    print(separator)

    for index, result in enumerate(results, start=1):
        row = [
            str(index),
            result.get("title", ""),
            result.get("link", ""),
            result.get("snippet", ""),
        ]
        print("|".join(f" {shorten(value, width)} " for value, (_, width) in zip(row, columns)))

    print(separator)


def format_results(data):
    results = json.loads(data)
    return results.get("organic", [])


def run_search(query, as_json=False):
    status, data = search_google(query)

    if status != 200:
        if as_json:
            print(json.dumps({
                "ok": False,
                "status": status,
                "error": data,
                "results": [],
            }))
        else:
            print(f"Error: HTTP {status}")
            print(data)
        return 1

    organic_results = format_results(data)

    if as_json:
        print(json.dumps({
            "ok": True,
            "status": status,
            "query": query,
            "results": organic_results,
        }))
        return 0

    if not organic_results:
        print("No results found.")
        return 0

    print_table(organic_results)
    return 0


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip().lstrip("\ufeff")
        return run_search(query, as_json=True)

    while True:
        user = input("Enter your search (blank or q to quit): ").strip().lstrip("\ufeff")

        if not user or user.lower() == "q":
            break

        run_search(user)


if __name__ == "__main__":
    raise SystemExit(main())
