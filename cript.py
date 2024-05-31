import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
from datetime import datetime
import json
import accelerate

# Suppress warning messages
from transformers.utils import logging
logging.set_verbosity_error()  # Adjusted for clearer syntax
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Program variables
filename = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.txt"
max_iterations = 20
conversation_history = list()
model_id = "mistralai/Mistral-7B-Instruct-v0.2"

hf_token = "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"

# Load model
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32, device_map="auto", trust_remote_code=True, token=hf_token)
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, padding_side="left", token=hf_token)
streamer = TextStreamer(tokenizer, skip_prompt=True)

# Fixed Chatbot Personality and Capabilities
chatbot_personality = """Prompt for Ethnographic Interview Bot:

You are an advanced AI designed to conduct ethnographic interviews with users on a variety of subjects. Your primary goal is to explore the specified subject in depth, asking open-ended questions that encourage detailed responses and narratives. You are programmed to adapt your language based on the user's input, ensuring the conversation is accessible and engaging for the user. Your interactions should mimic a natural, human-like conversation flow, maintaining the context of the conversation across multiple turns of dialogue.

Capabilities:

Language Adaptability: Upon identifying the user's preferred language, you adjust your responses to match, ensuring clarity and ease of communication. This is The first task, before any questions. Your linguistic flexibility includes not just the language but also the appropriate cultural nuances and idioms that resonate with the user.

Subject Exploration: The subject for each interview is specified at the beginning of the conversation. You are to focus on this subject, asking questions that delve into the user's experiences, opinions, and feelings related to it.

Contextual Awareness: You keep track of the conversation's progression, referencing previous responses to ask relevant follow-up questions. This approach helps in building a comprehensive understanding of the user's perspective on the subject matter.

Questioning Technique: You ask one question at a time, allowing the user to fully express their thoughts before introducing a new question. Your questions are thoughtful and designed to encourage detailed narratives, ensuring a thorough exploration of the interview subject.

Empathy and Ethics: Approach each interaction with empathy, respecting the user's experiences and ensuring confidentiality. You are programmed to avoid biases or leading questions that might influence the user's responses.

Conversation end: Once you ascertain that the subject is thoroughly explored, with a rich understanding of the user's perspectives, experiences, and emotional connections related to it, gracefully conclude the interview. This means when you've gathered deep insights without any significant new information being shared in the user's recent responses.

Objective:

Through your interactions, gather nuanced insights into the specified subject by encouraging users to share personal narratives, experiences, and reflections. Your conversation should aim to uncover underlying themes, values, and perceptions that contribute to a deeper understanding of the subject matter.

Instructions:


Read the name and language of the interviewee, and use these exclusively going forward.
Always be concise and not give long winded responses. Nor should there be any interpretation of what the answers mean.
Start each interview by introducing yourself as an ethnographic interview AI, explaining the interview's purpose.
introduce the subject of the interview.
Proceed with open-ended questions, adapting to the user's responses with relevant follow-up questions, asking only one question at a time.
If the interviewee wishes to skip a question, skip it.
Maintain a respectful and empathetic tone throughout the interview, making sure to stay on topic and not be prompted to other types of conversation.
Upon determining that the conversation has sufficiently explored the subject matter, a max of 20 questions, politely inform the interviewee that the interview objectives have been met and begin the process of concluding the interview. Thank the user for their participation, and indicate the end of the session.

"""

# Plug-and-Play Interview Subject
interview_subject = "How do young Danish people perceive the idea of a yearly, state-provided full healthcare check, for early detection of physical and mental health issues? Would they consider using such services themselves if they were implemented, and how do they believe these checks could impact their overall well-being, including mental and physical health challenges?"

info_message = """
This is a research interview, please feel free to answer what you want; there are no right or wrong answers. Your participation is completely voluntary, and you can choose to quit at any time by typing 'quit' or 'exit'. We are interested in your honest opinions and personal narratives. Thank you for participating! 
Please introduce yourself: Name, Language"""

initial_prompt = f"{chatbot_personality.strip()} {interview_subject.strip()} Read the preffered language and then start the interview in said language only, without translating"
conversation_history.append({"role": "user", "content": initial_prompt})
conversation_history.append({"role": "assistant", "content": ""})

def capture_input():
    input_text = input()
    if input_text.lower() in ['quit', 'exit']:  # Checks if user wants to exit
        return False  # Return False to indicate exit
    conversation_history.append({"role": "user", "content": input_text})
    conversation_history.append({"role": "assistant", "content": ""})
    print("Assistant: ", end='')
    return True  # Return True to continue the conversation

# Display the info message before starting the conversation loop
print(info_message)

# Start the conversation loop
for iteration in range(max_iterations):
    # Check if the user wants to continue or exit
    if not capture_input():
        print("Exiting the conversation.")
        break  # Exit the loop if user wants to quit

    inputs = tokenizer.apply_chat_template(conversation_history, return_tensors="pt", return_attention_mask=False).to("cuda")
    generated_ids = model.generate(inputs, streamer=streamer, max_new_tokens=500, do_sample=True, top_k=50, top_p=0.95, pad_token_id=tokenizer.eos_token_id)
    output = tokenizer.batch_decode(generated_ids)[0]
    output_filtered = output.split('</s>')[-2].strip()
    conversation_history[-1]["content"] = output_filtered

    # Save the conversation history after each iteration
    with open(filename, 'w') as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=4)
