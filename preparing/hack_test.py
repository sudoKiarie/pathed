import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Function to initialize the OpenAI API client
def initialize_openai():
    try:
        return OpenAI(
            api_key=os.getenv("API_KEY"),  # Load API key from environment
            base_url="https://api.aimlapi.com"
        )
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return None

# Function to interact dynamically with the model and patient
def dynamic_patient_questionnaire():
    client = initialize_openai()
    if client is None:
        return

    # Initialize conversation history
    conversation_history = []

    # Start with the first question
    current_question = "Which symptoms are you experiencing?"

    for question_num in range(1, 6):  # Limit to 6 questions for now
        # Ask the current question and collect the patient's response
        print(f"Question {question_num}: {current_question}")
        patient_response = input("> ")

        # Append the current question and response to the conversation history
        conversation_history.append(f"Medical Assistant: {current_question}")
        conversation_history.append(f"Patient: {patient_response}")

        # Create a prompt from the entire conversation history
        prompt = "\n".join(conversation_history) + "\nBased on this information, please generate the next relevant question."

        print("Prompt:", prompt)

        # Send request to OpenAI to generate the next question
        try:
            response = client.chat.completions.create(
                model="o1-preview",  # Use the appropriate model version
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                max_tokens=1000,  # Increased tokens for detailed medical questions
            )
            next_question = response.choices[0].message.content.strip()
            print("Next question is:", next_question)

            # Prepare for the next iteration
            current_question = next_question
            
        except Exception as e:
            print(f"Error during OpenAI API call for next question: {e}")
            break

    # After collecting responses, ask the model for a differential diagnosis
    # Function to generate a diagnosis after the conversation
def generate_diagnosis(conversation_history):
    client = initialize_openai()
    if client is None:
        return
    if conversation_history:
        # Initialize the prompt with the header
        prompt_for_diagnosis = "Prompt for differential diagnosis:\nHere are the patient's responses:\n"
        
        # Format each response appropriately
        for response in conversation_history:
            # Assuming each response is a tuple (question, answer)
            question, answer = response  # Unpack the tuple if it's structured this way
            prompt_for_diagnosis += f"- {question}: {answer}\n"

        # Add the request for differential diagnoses
        prompt_for_diagnosis += "\nPlease provide 3-5 differential diagnoses along with any recommended tests to narrow down the diagnosis."

        print("Prompt for differential diagnosis:", prompt_for_diagnosis)
        try:
            response = client.chat.completions.create(
                model="o1-preview",  # Adjust model version as needed
                messages=[
                    {
                        "role": "user",
                        "content": prompt_for_diagnosis
                    },
                ],
                max_tokens=1000,  # Adjust token limit for diagnosis generation
            )
            diagnosis = response.choices[0].message.content.strip()
            print(f"Assistant: {diagnosis}")
        except Exception as e:
            print(f"Error during OpenAI API call for differential diagnosis: {e}")
    else:
        print("No patient responses recorded. Cannot proceed with diagnosis.")


if __name__ == "__main__":
    dynamic_patient_questionnaire()
