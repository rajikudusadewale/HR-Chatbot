import os
import openai
import re
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from typing_extensions import override
from openai import AssistantEventHandler

# Load the API key from .env and authenticate with OpenAI
load_dotenv(find_dotenv(), override=True)
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Create OpenAI client
client = OpenAI()

# Create and Upload Vector Stores for Knowledge Bases
def create_and_upload_vector_store(store_name, file_paths):
    vector_store = client.beta.vector_stores.create(name=store_name)
    file_streams = [open(path, "rb") for path in file_paths]
    
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    
    for stream in file_streams:
        stream.close()
    
    return vector_store.id

# IDs for the knowledge base files
company_policies_vector_store_id = create_and_upload_vector_store("Company Policies", ["base/company_policies.txt"])
employee_benefits_vector_store_id = create_and_upload_vector_store("Employee Benefits", ["base/employee_benefits.txt"])
leave_request_vector_store_id = create_and_upload_vector_store("Leave Requests", ["base/leave_request.txt"])
payroll_vector_store_id = create_and_upload_vector_store("Payroll", ["base/payroll.txt"])

# Create and Update Assistants with Vector Stores and Detailed Instructions
assistants = {
    "Company Policies": client.beta.assistants.create(
        name="Company Policies Assistant",
        instructions="""
        You are an HR assistant for FutureTech Solutions specializing in company policies. 
        Your role is to provide comprehensive information about company policies, including but not limited to:
        - Code of Conduct
        - Attendance and Punctuality
        - Dress Code
        - Workplace Safety
        - Anti-Harassment Policy
        - Data Security
        - Use of Company Property
        - Confidentiality
        - Conflict of Interest
        - Disciplinary Actions

        When an employee asks a question, provide detailed information based on the query and suggest additional relevant topics they might be interested in. But If a query is outside this scope, you must politely decline to answer.
        """,
        tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
        tool_resources={"file_search": {"vector_store_ids": [company_policies_vector_store_id]}},
        model='gpt-4o',
    ),
    "Employee Benefits": client.beta.assistants.create(
        name="Employee Benefits Assistant",
        instructions="""
        You are an HR assistant for FutureTech Solutions specializing in employee benefits. 
        Your role is to provide comprehensive information about employee benefits, including but not limited to:
        - Health Insurance
        - Retirement Plans
        - Paid Time Off
        - Wellness Programs
        - Employee Discounts
        - Education and Training Reimbursement
        - Flexible Work Arrangements
        - Parental Leave

        When an employee asks a question, provide detailed information based on the query and suggest additional relevant topics they might be interested in. But If a query is outside this scope, you must politely decline to answer.
        """,
        tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
        tool_resources={"file_search": {"vector_store_ids": [employee_benefits_vector_store_id]}},
        model='gpt-4o',
    ),
    "Leave Requests": client.beta.assistants.create(
        name="Leave Request Assistant",
        instructions="""
        You are an HR assistant for FutureTech Solutions specializing in leave requests and policies. 
        Your role is to assist employees with submitting leave requests and provide information about leave policies, including but not limited to:
        - Types of Leave (e.g., Sick Leave, Vacation Leave, Parental Leave, etc.)
        - Leave Accrual and Usage
        - Leave Approval Process
        - How to Submit a Leave Request
        - Paid and Unpaid Leave

        When an employee asks a question, provide detailed information based on the query, guide them through the leave request process, and suggest additional relevant topics they might be interested in If a query is outside this scope, you must politely decline to answer.
        """,
        tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
        tool_resources={"file_search": {"vector_store_ids": [leave_request_vector_store_id]}},
        model='gpt-4o',
    ),
    "Payroll": client.beta.assistants.create(
        name="Payroll Assistant",
        instructions="""
        You are an HR assistant for FutureTech Solutions specializing in payroll inquiries. 
        Your role is to provide comprehensive information about payroll, including but not limited to:
        - Pay Schedules
        - Deductions and Taxes
        - Overtime Pay
        - Bonuses and Commissions
        - Direct Deposit
        - Payroll Corrections
        - Year-End Tax Documents

        When an employee asks a question, provide detailed information based on the query and suggest additional relevant topics they might be interested in. If a query is outside this scope, you must politely decline to answer.
        """,
        tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
        tool_resources={"file_search": {"vector_store_ids": [payroll_vector_store_id]}},
        model='gpt-4o',
    )
}


# Dictionary to store conversation history
conversation_histories = {}

def create_thread():
    thread = client.beta.threads.create()
    conversation_histories[thread.id] = []
    return thread.id

def add_message_to_thread(thread_id, role, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role=role,
        content=content
    )
    conversation_histories[thread_id].append({"role": role, "content": content})
    return message.id

def get_first_user_message(thread_id):
    for message in conversation_histories[thread_id]:
        if message["role"] == "user":
            return message["content"]
    return "No user messages found."

def run_and_poll_thread(thread_id, assistant_id):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run

def replace_annotations_in_response(response, assistant_choice):
    # Define the regex pattern to match annotations like  
    pattern = re.compile(r'【\d+:\d+†source】')
    annotations = pattern.findall(response)
    
    # Remove annotations
    for annotation in annotations:
        response = response.replace(annotation, '')
    
    return response

class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []
        
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_current_temperature":
                tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
            elif tool.function.name == "get_rain_probability":
                tool_outputs.append({"tool_call_id": tool.id, "output": "0.06"})
        
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            assistant_response = ""
            for text in stream.text_deltas:
                assistant_response += text
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

def test_assistant(assistant_id, user_query, assistant_choice):
    thread_id = create_thread()
    add_message_to_thread(thread_id, "user", user_query)
    
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        event_handler=EventHandler()
    ) as stream:
        assistant_response = ""
        for text in stream.text_deltas:
            assistant_response += text
        
        # Replace annotations in the assistant's response
        assistant_response = replace_annotations_in_response(assistant_response, assistant_choice)

        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

# Streamlit Web App

st.set_page_config(page_title="FutureTech Solutions HR Chatbot Assistant", layout="wide")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'employee_name' not in st.session_state or not st.session_state.employee_name:
    st.session_state.employee_name = ""
if 'employee_id' not in st.session_state or not st.session_state.employee_id:
    st.session_state.employee_id = ""

if not st.session_state.employee_name or not st.session_state.employee_id:
    st.title("FutureTech Solutions HR Chatbot Assistant")
    st.write("""
    Welcome to FutureTech Solutions! We are here to assist you with all your HR-related inquiries. 
    Our HR chatbot can help you with company policies, employee benefits, leave requests, and payroll information. 
    Please enter your details to get started.
    """)
    st.session_state.employee_name = st.text_input("Enter your name:")
    st.session_state.employee_id = st.text_input("Enter your Employee ID:")
    st.write("Developed By DeDataDude")
else:
    st.sidebar.title("FutureTech Solutions HR Chatbot Assistant")
    st.sidebar.write("""
    Welcome to FutureTech Solutions! We are here to assist you with all your HR-related inquiries. 

    Our HR chatbot can help you with:
    - Company Policies

    - Employee Benefits

    - Leave Requests

    - Payroll Information.
    """)
    st.sidebar.write(f"**Employee:** {st.session_state.employee_name}")
    st.sidebar.write(f"**ID:** {st.session_state.employee_id}")

    st.title("HR Chatbot")

    # Short welcome message for the employee
    st.write(f"""
    Welcome, {st.session_state.employee_name} (ID: {st.session_state.employee_id})! 
    How can we assist you today with your HR-related inquiries?
    """)
    
    # Select Assistant
    assistant_choice = st.selectbox("Choose an HR Assistant to interact with:", 
                                    ["Company Policies", "Employee Benefits", "Leave Requests", "Payroll"])

    # Initialize Variables
    assistant_id = assistants[assistant_choice].id

    # User Input Area
    with st.expander("Ask your question here"):
        user_query = st.text_area("Enter your question:")

    if st.button("Submit"):
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            test_assistant(assistant_id, user_query, assistant_choice)
        
        # Display the chat history
        chat_history = ""
        for chat in st.session_state.chat_history:
            chat_history += f"**{chat['role'].capitalize()}**: {chat['content']}\n\n"
            chat_history += "---\n"
        st.markdown(chat_history)

    # Button to Restart
    if st.button("Restart"):
        st.session_state.chat_history = []
        st.experimental_rerun()

    # Button to Log Out
    if st.button("Log Out"):
        st.session_state.clear()
        st.write("Logging out...")
        st.stop()
    st.write("Developed By DeDataDude")