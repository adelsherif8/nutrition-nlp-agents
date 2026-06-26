import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

FINETUNED_MODEL_PATH = "llama-nutrition-finetuned/variant_1/final"
BASE_MODEL = "meta-llama/Llama-3.2-1B"
MAX_NEW_TOKENS = 300

class MealPlanningAgent:
    def __init__(self):
        print("Loading meal planning agent...")
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model = PeftModel.from_pretrained(base_model, FINETUNED_MODEL_PATH)
        self.model.eval()
        print("Agent 3 ready.")

    def generate_meal_plan(self, user_needs: dict) -> str:
        """
        user_needs = {
            "calories": 2500,
            "protein": 150,
            "fat": 70,
            "carbs": 300
        }
        """
        prompt = (
            f"### Instruction:\n"
            f"Create a meal plan for someone who needs "
            f"{user_needs['calories']} calories, "
            f"{user_needs['protein']}g protein, "
            f"{user_needs['fat']}g fat, "
            f"{user_needs['carbs']}g carbs.\n\n"
            f"### Response:\n"
        )

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        meal_plan = response.split("### Response:")[-1].strip()
        return meal_plan


if __name__ == "__main__":
    # Test with hardcoded input (replace with Agent 2 output later)
    user_needs = {
        "calories": 2500,
        "protein": 150,
        "fat": 70,
        "carbs": 300
    }

    agent = MealPlanningAgent()
    meal_plan = agent.generate_meal_plan(user_needs)

    print("\nGenerated Meal Plan:")
    print("=" * 50)
    print(meal_plan)
