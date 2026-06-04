import os
import sys
import json

try:
    import httpx
except Exception:
    httpx = None


def load_env(path: str) -> dict:
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
    except FileNotFoundError:
        return {}
    return data


def main():
    repo_root = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(repo_root, ".env")
    env = load_env(env_path)
    key = env.get("MISTRAL_KEY")
    if not key:
        print("MISTRAL_KEY not found in backend/.env")
        sys.exit(2)

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Provide a one-line acknowledgement: hello from mistral"},
        ],
        "temperature": 0.0,
        "max_tokens": 100,
    }

    if httpx is None:
        print("httpx not available in this environment. Please install httpx or run this test elsewhere.")
        sys.exit(3)

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            print("status:", resp.status_code)
            try:
                print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
            except Exception:
                print(resp.text)
    except Exception as exc:
        print("Request failed:", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
