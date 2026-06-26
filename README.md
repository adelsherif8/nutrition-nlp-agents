# Nutrition NLP Agents

A multi-agent NLP pipeline for nutrition planning. Several cooperating agents
interpret a user's request, look up nutrition data, and generate meal plans and
variants — backed by the **USDA FoodData Central** dataset and an LLM.

## Architecture

```
agent1.py / agent3.py / Agent_2.ipynb / agent4.ipynb   pipeline agents
tools.ipynb        shared tools / function calling
pipeline*.ipynb    end-to-end pipelines (incl. Hugging Face variant)
variants.ipynb     meal-variant generation
app.py             entry point
FoodData_Central_sr_legacy_food_csv_2018-04/   USDA nutrient dataset
```

## Tech Stack

- **Python**
- LLM APIs — **Groq** and **Hugging Face**
- USDA FoodData Central (CSV) for nutrient lookups
- Jupyter notebooks documenting each agent

## Getting Started

```bash
pip install -r requirements.txt   # or install deps used in the notebooks
python app.py
```

## Configuration

API keys are read from environment variables — set your own before running:

```bash
export GROQ_API_KEY=your_key
export HF_TOKEN=your_token
```

> The code uses placeholders (`<YOUR_GROQ_API_KEY>`, `<YOUR_HF_TOKEN>`).
> Never hardcode real keys — load them from the environment.
