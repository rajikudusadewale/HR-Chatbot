# HR Chatbot

Welcome to the HR Chatbot repository! This project is designed to streamline HR inquiries for employees by leveraging the power of OpenAI's API and Streamlit for a user-friendly web application.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Customization](#customization)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

## Overview

The FutureTech Solutions HR Chatbot is an AI-powered assistant designed to help employees with their HR-related inquiries. It provides comprehensive information on company policies, employee benefits, leave requests, and payroll information.

## Features

- **Personalized Assistance**: The chatbot greets employees by their name and ID.
- **HR Inquiries**: Handles questions related to company policies, employee benefits, leave requests, and payroll.
- **User-Friendly Interface**: Built with Streamlit for an intuitive and easy-to-use web application.
- **Secure**: Uses environment variables to securely manage API keys.

## Setup

### Prerequisites

- Python 3.6 or higher
- An OpenAI API key
- An OpenAI Assistant
- Streamlit

### Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/rajikudusadewale/hr-chatbot.git
    cd HR-chatbot
    ```

2. **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements
    ```

4. **Set up environment variables**
    - Create a `.env` file in the root directory of the project.
    - Add your OpenAI API key to the `.env` file:
        ```
        OPENAI_API_KEY=your_openai_api_key
        ```

## Usage

1. **Run the Streamlit app**
    ```bash
    streamlit run app.py
    ```

2. **Interacting with the Chatbot**
    - Open your web browser and go to `http://localhost:8501`.
    - Enter your name and employee ID to start interacting with the chatbot.
    - Select the type of HR inquiry you need help with and ask your question.

## File Structure

```
hr-chatbot/
│
├── base/
│   ├── company_policies.txt
│   ├── employee_benefits.txt
│   ├── leave_request.txt
│   └── payroll.txt
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── ...
```

## Customization

To customize the chatbot for your organization, you can modify the text files in the `base/` directory with your specific company policies, benefits, leave request processes, and payroll information.

### Adding More Assistants

To add more assistants, you can follow the structure in the `HrWebApp.py` file, defining new assistants with their respective instructions and vector store IDs.

## Future Enhancements

1. **Assisting in Recruitment Process**
    - **Implementation**: Use the Assistant API to analyze and screen job applications submitted through the company’s career portal.
    - **Functionality**: The Assistant can parse resumes and cover letters, match the extracted data against job requirements, and create a shortlist of candidates for further review by HR.
    - **Outcome**: Expedite the screening process, reduce human error, and allow HR professionals to focus on interviewing and hiring the best candidates.

2. **Guiding New Employees Through Onboarding**
    - **Implementation**: Incorporate the Assistant API into the onboarding portal or an app specifically designed for new hires.
    - **Functionality**: The Assistant can provide a checklist of tasks to complete, offer tutorials or training materials, answer questions, and schedule reminders for onboarding meetings and training sessions.
    - **Outcome**: Create a structured and seamless onboarding experience, ensuring all necessary steps are completed timely and helping new employees feel more welcomed and prepared.

## Contributing

We welcome contributions! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.


## Acknowledgements

- [OpenAI](https://www.openai.com/) for providing the API to build this chatbot.
- [Streamlit](https://www.streamlit.io/) for creating an easy-to-use framework for deploying web applications.

---

