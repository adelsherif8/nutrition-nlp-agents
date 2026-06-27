# Deploying Nutrition NLP Agents (free, live)

This is a **Gradio** app (`app.py`), so the simplest live home is **Hugging Face
Spaces** — free, no cold-start sleep, and a natural fit for an AI portfolio.

## Hugging Face Spaces (recommended)
1. <https://huggingface.co/new-space> → SDK: **Gradio**, hardware: **CPU basic (free)**.
2. Push this repo's files to the Space (or connect the GitHub repo). Required files:
   `app.py`, `requirements.txt`, and the `FoodData_Central_*` dataset.
3. In the Space → **Settings → Variables and secrets** → add a secret:
   - `GROQ_API_KEY` = your Groq key  (and `HF_TOKEN` if using the HF variant)
4. The Space builds and serves automatically. Note the URL, e.g.
   `https://huggingface.co/spaces/<you>/nutrition-nlp-agents`.

> Add this front-matter to the Space's own `README.md` so it knows how to run:
> ```yaml
> ---
> title: Nutrition NLP Agents
> sdk: gradio
> app_file: app.py
> ---
> ```

## Alternative — Render
Works too: New + → Web Service → root `.`, build `pip install -r requirements.txt`,
start `python app.py`. Ensure `app.launch()` binds `server_name="0.0.0.0"` and
`server_port=int(os.environ["PORT"])` so Render can route to it.

Then update the live-demo link at the top of [`README.md`](./README.md).
