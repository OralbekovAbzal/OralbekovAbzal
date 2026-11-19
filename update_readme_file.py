import base64
import httpx
import sys
import os

URL_README = "https://api.github.com/repos/OralbekovAbzal/OralbekovAbzal/contents/README.md"
URL_CONTENT = "https://api.github.com/repos/OralbekovAbzal/ai_prep/contents"

MODULES = {
    0: "sys and streams: stdin, stdout, stderr, pipes, exit codes",
    1: "Python basics: references, collections, slices, comprehensions",
    2: "OOP and errors: classes, dataclasses, exceptions, logging, venv",
    3: "Generators, decorators, async: yield, asyncio, httpx, Semaphore",
    4: "Git, tests and AI-assisted dev: branches, PRs, pytest, specs first",
    5: "HTTP and FastAPI: REST, status codes, Pydantic, Depends",
    6: "SQL and Postgres: JOIN, GROUP BY, indexes, transactions",
    7: "Docker and deploy: Dockerfile, compose, first service on Render",
    8: "ML basics: train/val/test, metrics, thresholds, baseline vs model",
    9: "LLM APIs: tokens, prompts, structured output, streaming",
    10: "Agents: tool calling, agent loop, guardrails, model routing",
    11: "RAG from scratch: embeddings, pgvector, hybrid search",
    12: "LangGraph, MCP and evals: agent graphs, MCP server, Skills",
    13: "Final project: brief → storyboard for AI video",
}

auth = {"Authorization": f"Bearer {os.getenv("GITHUB_TOKEN")}"}

with httpx.Client(timeout=10, headers=auth) as client:
    resp = client.get(URL_README).json()
    encoded_text = resp["content"]
    sha = resp["sha"]
    
    decoded_bytes = base64.b64decode(encoded_text.replace("\n", ""))
    decoded_text = decoded_bytes.decode("utf-8")
    
    start, end = decoded_text.split("<!-- NEXT:START -->")
    mid, end = end.split("<!-- NEXT:END -->")

    resp = client.get(URL_CONTENT)
    files = resp.json()
    module_nums = list()

    for f in files:
        try:
            if f["type"] == "dir" and f["name"][0] == "m":
                module_nums.append(int(f["name"][1:3]))
        except ValueError:
            continue

    max_num = max(module_nums)

    new_mid = f"\nNow on module {max_num} · {MODULES[max_num]}\n"

    if new_mid == mid:
        print("no changes")
        sys.exit(0)
    
    start = "<!-- NEXT:START -->".join([start, new_mid])
    new_text = "<!-- NEXT:END -->".join([start, end])

    encoded_text = base64.b64encode(new_text.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Update progress in README.md",
        "content": encoded_text,
        "branch": "main",
        "sha": sha
    }

    res = client.put(URL_README, json=payload)

    print(res)