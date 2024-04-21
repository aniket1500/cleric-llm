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

1. **Navigate to the Backend Directory:**
   Open your terminal and change to the backend directory where the project files are located.

   ```bash
   cd path/to/backend
   ```

2. **Install Dependencies:**
   Ensure that you have Python installed and then run the following command to install the required Python packages.

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Backend Server:**
   Start the backend server using `uvicorn`. This command will start the server on localhost with hot reload enabled, making it easier to develop and test changes without restarting the server manually.

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

### Frontend Setup

To set up the frontend:

1. **Navigate to the Frontend Directory:**
   If your frontend files are located in a different directory, switch to that directory.

   ```bash
   cd path/to/frontend
   ```

2. **Serve the Frontend:**
   You can use a simple static server to serve the frontend files. For instance, you can use Python's HTTP server.

   ```bash
   python -m http.server
   ```

   Now, you can access the frontend by navigating to `http://localhost:8000` in your web browser.

## Usage

To use the application:

- Open your web browser and navigate to `http://localhost:8000`.
- Use the web interface to submit queries and view the processed call logs as instructed by the UI.



