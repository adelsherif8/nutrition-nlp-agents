# Project Briefing — Multi-Agent Nutrition Planner

---

## What the project does

A multi-agent AI pipeline that takes a user's physical profile (age, sex, weight, height, activity level, goal) and produces a personalised daily meal plan with verified macro-nutrient totals. It also supports reading body composition data directly from an InBody scan image. There is a full web UI built with Gradio (app.py) and a Jupyter notebook version of the pipeline (pipeline.ipynb).

---

---

## Tech stack

| Component | Technology |
|-----------|-----------|
| LLM (text generation) | Groq API — `llama-3.1-8b-instant` |
| LLM (vision / InBody) | Groq API — `meta-llama/llama-4-scout-17b-16e-instruct` |
| Food database (primary) | Local USDA SR Legacy CSV (7,756 foods) |
| Food database (fallback 1) | USDA FoodData Central API |
| Food database (fallback 2) | Open Food Facts API |
| Web UI | Gradio |
| Language | Python 3 |
| Notebooks | Jupyter |

---

## Agents

### Agent 1 — User Profile Collector (SHAKER)
- Accepts free-text input (e.g. "I'm 25, male, 180 lbs, 5'11, gym 5x a week, want to bulk")
- Built-in **unit converter**: lbs → kg, ft/in → cm using regex
- Extracts age, sex, weight, height, activity level, goal from natural language
- Falls back to interactive prompts for any missing fields
- Outputs a structured profile dict passed to Agent 2

### Agent 2 — Macro Calculator & Validator (ISLAM)
- **Validation layer**: checks all fields are present, numeric, in-range; normalises free-form values (e.g. "gym 3x" → "moderate") via lookup maps
- **LLM semantic fallback**: if a value can't be normalised by lookup, calls Groq to map it to a valid enum
- **Safety check**: blocks underage users (< 18), BMI < 18.5 (underweight), BMI > 35 (severely obese), medical conditions
- **Groq function calling** (CALCULATOR_TOOLS): Groq is given 4 tools and must call them in sequence:
  1. `calculate_bmr` — Mifflin-St Jeor formula
  2. `calculate_tdee` — BMR × activity multiplier
  3. `apply_goal` — weight_loss: −400 kcal, muscle_gain: +300 kcal, maintenance: 0
  4. `calculate_macros` — protein (2.0g/kg muscle, 1.8g/kg cut, 1.4g/kg maintain), fat (25% of calories), carbs (remainder)
- **Direct calculate fallback**: if Groq function calling returns implausible values (cal < 1200 or > 5000), falls back to a hardcoded Python implementation of the same formulas
- Generates a 1-2 sentence plain-English explanation of the targets via Groq

### Agent 3 — Meal Planner (LLM) (ADEL)
- Receives calorie/macro targets and per-meal budgets (breakfast 25%, lunch 35%, dinner 30%, snack 10%)
- Calls Groq (`llama-3.1-8b-instant`) with a structured prompt instructing it to output **only valid JSON**
- Prompt includes: user profile, daily targets, per-meal breakdowns, food rules (lean whole foods only, avoid processed/junk)
- JSON is parsed and each food item is **verified against the local food database** (Agent 4)
- Verified meals are scaled to exactly hit the target calorie total
- Temperature is the key variable studied in variants.ipynb (see Variants section)

### Agent 4 — Food Database (GHONEM)
- **Primary**: searches local USDA SR Legacy CSV (7,756 foods) by string match, then word-by-word fallback
- Filters out junk matches (baby food, candies, dry mix, infant formula)
- Picks shortest matching food name to prefer the simplest/most generic entry
- **Fallback 1**: USDA FoodData Central REST API
- **Fallback 2**: Open Food Facts API
- Calculates macros for any gram amount given a food name
- Calculates full meal totals (sum of all items)

### Agent 5 — InBody Extractor (Vision) (ISLAM)
- Takes a photo/scan of an InBody body composition report
- Encodes image to base64, sends to Groq vision model (`llama-4-scout-17b-16e-instruct`)
- Extracts: weight_kg, height_cm, skeletal_muscle_mass_kg, body_fat_mass_kg, body_fat_percent, BMI, BMR, visceral fat level, total body water
- Null-safe — returns None for any field not visible in the image
- Feeds extracted weight/height directly into Agent 2 to skip manual input

### Agent 6 Substitution Agent (ADEL)
- Runs after a meal plan is generated, on user feedback ("I hate salmon", "no eggs")
- Calls Groq to extract disliked foods from natural text → JSON array
- For each disliked food found in the plan, calls Groq again to suggest 5 substitutes
- Looks up each substitute in the food DB and swaps in the first one that matches
- Returns updated meal plan + list of changes made

---

## Gradio Web App (app.py)

Three input tabs:
1. **Describe Yourself** — free text, same as Agent 1
2. **InBody Scan** — upload image, Agent 5 extracts metrics
3. **Manual Entry** — form fields for all profile values

Model selector (top): M1 Consistent (temp 0.0), M2 Balanced (temp 0.4), M3 Creative (temp 0.9), M4 Llama 3.2 (temp 0.4, smaller model)

Compare All Models button: runs all 4 models on the same profile and shows a side-by-side table

Swap Foods section: apply_substitutions on any generated plan

---

## Variants Comparison (variants.ipynb)

Three runs of Agent 3 on the **same profile and targets**, varying only temperature:

| Variant | Temperature | Behaviour |
|---------|-------------|-----------|
| V1 — Deterministic | 0.0 | Same output every run |
| V2 — Balanced | 0.4 | Slight variation run to run |
| V3 — Creative | 0.9 | Different output each run |

**Test profile:** 25yo male, 174cm, 71kg, active, muscle gain  
**Targets:** 3,194 kcal | 142g protein | 89g fat | 457g carbs

---

## Variant Analysis Results

```
=================================================================
  VARIANT ANALYSIS
=================================================================

V1 — Deterministic  (temp=0.0)
  Behaviour  : deterministic (same result every run)
  Macro focus: high-protein (+39g over target), low-fat (20g under target — lean foods), carb-heavy (+63g over target)
  Macro split: 22.7% protein  |  19.3% fat  |  65.0% carbs
  Protein density : 5.7g protein per 100 kcal
  Food variety    : 10 unique foods across the day
  Heaviest meal   : lunch (1164 kcal)
  Calorie accuracy: 0.2% error (over by 5 kcal)

V2 — Balanced  (temp=0.4)
  Behaviour  : slightly varied per run
  Macro focus: high-protein (+41g over target)
  Macro split: 22.9% protein  |  23.8% fat  |  59.5% carbs
  Protein density : 5.7g protein per 100 kcal
  Food variety    : 10 unique foods across the day
  Heaviest meal   : lunch (1109 kcal)
  Calorie accuracy: 0.0% error (over by 1 kcal)

V3 — Creative  (temp=0.9)
  Behaviour  : creative — different result each run
  Macro focus: low-protein (-29g under target), high-fat (+25g over target)
  Macro split: 14.2% protein  |  32.3% fat  |  53.8% carbs
  Protein density : 3.6g protein per 100 kcal
  Food variety    : 10 unique foods across the day
  Heaviest meal   : dinner (988 kcal)
  Calorie accuracy: 0.1% error (under by 3 kcal)

=================================================================
  WINNER PER METRIC
=================================================================
  Best calorie accuracy : V2 — Balanced
  Most protein          : V2 — Balanced
  Most food variety     : V1 — Deterministic
  Leanest (lowest fat)  : V1 — Deterministic
```

**Key observations:**
- All 3 variants hit calorie targets within 0.2% — the scaling step in Agent 3 forces this
- V1 and V2 are protein-heavy because the model picks lean foods (chicken, turkey, egg whites) and the DB matches to lean variants
- V3 at temp=0.9 broke the protein target significantly (−29g) and overshot fat (+25g) — higher creativity trades accuracy for variety
- Food variety is identical (10 unique foods) across all 3 — the food DB constraint dominates over LLM creativity
- Lunch is consistently the heaviest meal (35% budget) in V1/V2; V3 shifted the weight to dinner

---

## Charts generated (variants.ipynb)

| File | What it shows |
|------|--------------|
| `variant_macros.png` | 4-panel bar chart — achieved vs target for calories, protein, fat, carbs across all 3 variants |
| `variant_meal_dist.png` | 3 pie charts — calorie split across breakfast/lunch/dinner/snack per variant |
| `variant_errors.png` | Grouped bar chart — % error from target per macro per variant |
| `variant_radar.png` | Radar/spider chart — macro % split vs target reference shape |
| `variant_meal_accuracy.png` | Per-meal calorie bars — how close each meal is to its budget |
| `variant_food_overlap.png` | Heatmap — which foods appear in which variants |
| `variant_response_time.png` | Bar chart — Groq API response time per variant |

---

## Metrics used for evaluation

| Metric | Definition |
|--------|-----------|
| Calorie accuracy (%) | `abs(achieved - target) / target × 100` |
| Protein/fat/carbs error (%) | Same formula per macro |
| Macro split (%) | protein×4, fat×9, carbs×4 as % of total calories |
| Protein density | grams protein per 100 kcal |
| Food variety | count of unique food names across the day |
| Heaviest meal | meal with highest calorie total |
| API response time | wall-clock seconds for Agent 3 LLM call |
