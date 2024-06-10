import streamlit as st
import json
import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
@st.cache_data
def fetch_questions(text_content, quiz_level):
 RESONSE_JSON = {
  "mcqs" : [
   {
    "mcq" : "multiple choice question1",
    "options":{
     "a":"choice here1",
     "b":"choice here2",
     "c":"choice here3",
     "d":"choice here4",
    },
    "correct" : "correct choice option",
   },
   {
    "mcq" : "multiple choice question1",
    "options":{
     "a":"choice here",
     "b":"choice here",
     "c":"choice here",
     "d":"choice here",
    },
    "correct" : "correct choice option",
   },
   {
    "mcq" : "multiple choice question1",
    "options":{
     "a":"choice here",
     "b":"choice here",
     "c":"choice here",
     "d":"choice here",
    },
    "correct" : "correct choice option",
   }
  ]
 }
 PROMPT_TEMPLATE="""
 Text:{text_content}
 You are an expert in generating MCQ type quiz on the basis of provided content.
 Given the above text, create a quiz of 3 multiple choice questions keeping difficulty level as {quiz_level}.
 Make sure the questions are not repeated and check all the questions to be conforming the text as well.
 Make sure to format your response like RESONSE_JSON below and use it as a guide.
 HERE is the RESONSE_JSON:

 {RESONSE_JSON}
 
 """

 formatted_template = PROMPT_TEMPLATE.format(text_content=text_content,quiz_level=quiz_level,RESONSE_JSON=RESONSE_JSON)

 #Make API request
 response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {
         "role": "user",
         "content": formatted_template
        },
   ],
   temperature=0.3,
   max_tokens=1000,
   top_p=1,
   frequency_penalty=0,
   presence_penalty=0
 )

 extracted_response = response.choices[0].message.content

 # Try replacing single quotes with double quotes (if applicable)
 try:
     fixed_response = extracted_response.replace("'", '"')
     return json.loads(fixed_response).get("mcqs", [])
 except (json.JSONDecodeError, AttributeError):
     pass  # Handle cases where replace or decode fails

 # If replace fails, try removing extra characters at the beginning (optional)
 try:
     # Assuming the issue is at the beginning, remove first 10 characters
     fixed_response = extracted_response[10:]
     return json.loads(fixed_response).get("mcqs", [])
 except (json.JSONDecodeError, AttributeError):
     # Raise an error or handle it gracefully if both attempts fail
     raise ValueError("Failed to decode API response")

    # You can add more advanced checks and handling based on the response format

def main():
 st.title("Quiz Generator App")

 text_content = st.text_area("Pasts the text content here:")

 quiz_level = st.selectbox("Select quiz level:",["Easy","Medium","Hard"])

 quiz_level_lower = quiz_level.lower()

 session_state = st.session_state

 if 'quiz_generated' not in session_state:
    session_state.quiz_generated = False

 if not session_state.quiz_generated:
  session_state.quiz_generated = st.button("Generate Quiz")

 if session_state.quiz_generated:
  questions = fetch_questions(text_content=text_content,quiz_level=quiz_level_lower)

 

 
  selected_options = []
  correct_answers = []
  for question in questions:
   options = list(question["options"].values())
   selected_option = st.radio(question["mcq"],options,index=None)
   selected_options.append(selected_option)
   correct_answers.append(question["options"][question["correct"]])
 
  if st.button("Submit"):
   marks = 0
   st.header("Quiz Result:")
   for i, question in enumerate(questions):
          selected_option = selected_options[i]
          correct_option = correct_answers[i]
          st.subheader(f"{question['mcq']}")
          st.write(f"You selected: {selected_option}")
          st.write(f"Correct answer: {correct_option}")
          if selected_option == correct_option:
            marks += 1
   st.subheader(f"You scored {marks} out of {len(questions)}")

if __name__ == "__main__":
  main()
