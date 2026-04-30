from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "Helsinki-NLP/opus-mt-vi-fr"
print(f"Loading translation model: {model_name}...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
print("Model loaded successfully.")

def translate_text(text: str):
    print(f"Translating: {text[:50]}...")
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(**inputs)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Translation complete: {result[:50]}...")
    return result
