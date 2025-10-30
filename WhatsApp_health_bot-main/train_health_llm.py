"""
train_health_llm.py
Sample script to fine-tune a DistilBERT model for health queries using Hugging Face Transformers.
Replace the sample data with your own health Q&A dataset for real results.
"""

from transformers import Trainer, TrainingArguments, DistilBertTokenizerFast, DistilBertForSequenceClassification
from datasets import Dataset
import torch

# Sample health Q&A data (replace with your own dataset)
data = {
    "text": [
        "What are the symptoms of diabetes?",
        "How to treat a headache?",
        "What is a healthy diet?",
        "How to prevent flu?",
        "What are the signs of dehydration?"
    ],
    "label": [0, 1, 2, 3, 4]  # Each label corresponds to a unique answer
}
answers = [
    "Common symptoms of diabetes include increased thirst, frequent urination, and fatigue.",
    "Treat a headache with rest, hydration, and over-the-counter pain relief.",
    "A healthy diet includes fruits, vegetables, lean proteins, and whole grains.",
    "Prevent flu by washing hands, getting vaccinated, and avoiding close contact with sick people.",
    "Signs of dehydration include dry mouth, dizziness, and dark urine."
]

dataset = Dataset.from_dict(data)
tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

def preprocess(examples):
    return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=32)

tokenized_dataset = dataset.map(preprocess, batched=True)

model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=len(answers))

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=2,
    logging_dir='./logs',
    logging_steps=10,
    save_steps=20,
    report_to=[]
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()

# Save model and answers
model.save_pretrained('./health_llm_model')
tokenizer.save_pretrained('./health_llm_model')
import json
with open('./health_llm_model/answers.json', 'w') as f:
    json.dump(answers, f)

print("Model trained and saved to ./health_llm_model")
