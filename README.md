# Project Documentation

## Overview

This web application is designed to query and process call logs. It utilizes FastAPI for the backend and simple HTML/CSS/JavaScript for the frontend. The application leverages OpenAI's GPT-4 to extract insights from uploaded call logs based on user queries.

## High-Level Approach
- **API Construction**: Developed with FastAPI to handle asynchronous requests, providing endpoints for submitting documents and retrieving processed facts.
- **Data Processing**: Utilizes OpenAI's GPT-4 model to analyze text from call logs and extract relevant facts based on the user's question. This process involves sorting documents by date to respect the chronological context of the information.
- **User Interface**: A simple frontend built with HTML, CSS, and JavaScript that allows users to input their questions and URLs of the call logs, and displays the extracted facts once processing is complete.

## Setup Instructions

### Backend Setup

To set up the backend, follow these steps:

1. **Navigate to the API Directory:**
   Open your terminal and change to the backend directory where the project files are located.

   ```bash
   cd path/to/api
   ```

2. **Install Dependencies:**
   Ensure that you have Python installed and then run the following command to install the required Python packages.

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Web Application in your root directory:**
   Start the backend server using `uvicorn`. This command will start the server on localhost with hot reload enabled, making it easier to develop and test changes without restarting the server manually.

   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001
   ```
4. **The app is hosted on Render.com:**
   The application is also available online at https://cleric-llm-1.onrender.com. You can access it to interact with the web interface without running it locally.

## Usage

To use the application:

- Open your web browser and navigate to `http://localhost:8001`.
- Use the web interface to submit queries and view the processed call logs as instructed by the UI.



