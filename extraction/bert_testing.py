import tensorflow as tf
from transformers import BertTokenizer, TFBertForQuestionAnswering

# Load the tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = TFBertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

# Define the context and question
context = "The capital of France is Paris . Berlin is the capital of Germany . England's capital is London ."
question = " What is the capital of Germany ?"

# Tokenize the context and question
inputs = tokenizer(question, context, return_tensors='tf', max_length=512, truncation = True)

# Get the model's output
output = model(inputs)

# Get the start and end token indices
start_index = tf.argmax(output.start_logits, axis=1).numpy()[0]
end_index = tf.argmax(output.end_logits, axis=1).numpy()[0]

# Convert the token indices to the answer text
answer_tokens = inputs['input_ids'][0][start_index:end_index+1]
answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(answer_tokens))
print(answer)