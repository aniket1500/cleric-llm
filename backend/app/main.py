from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import httpx
import openai
from dotenv import load_dotenv
import os
from threading import Thread
import asyncio
from datetime import datetime
import re

from .models import DocumentSubmission, GetQuestionAndFactsResponse

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup template directory within the static folder
templates = Jinja2Templates(directory="frontend/static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #// Double-check this in production for security
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load environment variables
load_dotenv()

# Set OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")
port = int(os.getenv("PORT", "8000"))

# This will hold the tasks and their states
tasks = {}
task_id_counter = 1

@app.post("/submit_question_and_documents", status_code=status.HTTP_200_OK)
async def submit_question_and_documents(data: DocumentSubmission):
    global task_id_counter

    # Reset the entire tasks dictionary to ensure each submission is completely independent
    tasks.clear()
    task_id_counter = 1  # Reset the task ID counter for a fresh start

    task_id = task_id_counter
    task_id_counter += 1

    tasks[task_id] = {"question": data.question, "status": "processing", "facts": None}
    print("Task ID sent to frontend:", task_id)  # Check the task ID output

    thread = Thread(target=lambda: asyncio.run(fetch_and_process_documents(data.question, data.documents, task_id)))
    thread.start()

    return {"message": "Processing started", "task_id": task_id}



def clean_input(text: str) -> str:
    """Clean input text by stripping unwanted characters."""
    return text.strip(' "\'')

def sort_and_clean_urls(urls: List[str]) -> List[str]:
    # Ensure no URL manipulation removes 'https://'
    clean_urls = [url.strip().strip('"') for url in urls]  # Correct handling
    date_pattern = re.compile(r'\d{8}')
    sorted_urls = sorted(
        clean_urls,
        key=lambda x: datetime.strptime(date_pattern.search(x).group(), '%Y%m%d') if date_pattern.search(x) else datetime.min
    )
    return sorted_urls



async def fetch_and_process_documents(question: str, urls: List[str], task_id: int):
    async with httpx.AsyncClient() as client:
        print("URLs being requested:", urls)  # Debug: Print URLs before requesting
        responses = await asyncio.gather(*(client.get(url) for url in urls))

    combined_documents = "\n".join(f"Call Log {i+1}\n{resp.text}" for i, resp in enumerate(responses) if resp.status_code == 200)
    print("combined_documents", combined_documents)

    try:
        print("question-->", question)
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Question: {question}\n\nDocuments: {combined_documents}\n\n\nBased on the above given question and call logs of the meetings. The call logs are provided in a sequential manner from old to most recent calls.  Write facts as a bulleted list, using simple and clear language. You must not have unnecessary facts. Your list of facts must not have double facts (two facts per line). The order of calls changes the list of facts (e.g, the final call is the most important since its the most recent). Below is a detailed example of the entire process. Your task is to give final facts of the entire conversation keeping the above instructions in mind. Make sure to start each fact with 'The team has decided to'. \n\nDesired output format: \nFact 1\nFact 2\nand so on\n\nExample START:\nExample:\nCall Log 1\n\n1\n00:01:11,430 --> 00:01:40,520\nJohn: Hello, everybody. Let's start with the product design discussion. I think we should go with a modular design for our product. It will allow us to easily add or remove features as needed.\n\n2\n00:01:41,450 --> 00:01:49,190\nSara: I agree with John. A modular design will provide us with the flexibility we need. Also, I suggest we use a responsive design to ensure our product works well on all devices. Finally, I think we should use websockets to improve latency and provide real-time updates.\n\n3\n00:01:49,340 --> 00:01:50,040\nMike: Sounds good to me. I also propose we use a dark theme for the user interface. It's trendy and reduces eye strain for users. Let's hold off on the websockets for now since it's a little bit too much work.\n\nCall Log 2\n\n1\n00:01:11,430 --> 00:01:40,520\nJohn: After giving it some more thought, I believe we should also consider a light theme option for the user interface. This will cater to users who prefer a brighter interface.\n\n2\n00:01:41,450 --> 00:01:49,190\nSara: That's a great idea, John. A light theme will provide an alternative to users who find the dark theme too intense.\n\n3\n00:01:49,340 --> 00:01:50,040\nMike: I'm on board with that.\n\nCall Log 3\n\n1\n00:01:11,430 --> 00:01:40,520\nJohn: I've been thinking about our decision on the responsive design. While it's important to ensure our product works well on all devices, I think we should focus on desktop first. Our primary users will be using our product on desktops.\n\n2\n00:01:41,450 --> 00:01:49,190\nSara: I see your point, John. Focusing on desktop first will allow us to better cater to our primary users. I agree with this change.\n\n3\n00:01:49,340 --> 00:01:50,040\nMike: I agree as well. I also think the idea of using a modular design doesn't make sense. Let's not make that decision yet.\n\nQuestion: “What are our product design decisions?”\n\nThe team has decided to focus on a desktop-first design\nThe team has decided to provide both dark and light theme options for the user interface.\nExample END"}
            ]
        )
        print("RESPONSE-->", response)
        response_text = response.choices[0].message.content
        # Ensure the facts are returned as a list
        if isinstance(response_text, str):
            facts = [fact.strip() for fact in response_text.split('\n') if fact.strip()]
        else:
            facts = response_text  # Assuming it's already in list format

        print("FACTS-->", facts)
        tasks[task_id]["facts"] = facts
        tasks[task_id]["status"] = "done"
    except Exception as e:
        tasks[task_id]["status"] = "error"
        print(f"Error with GPT-4 API: {str(e)}")

@app.get("/get_question_and_facts", response_model=GetQuestionAndFactsResponse)
def get_question_and_facts(task_id: int):
    task = tasks.get(task_id)
    if task:
        return JSONResponse(content=task, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content={"message": "Task not found"}, status_code=status.HTTP_404_NOT_FOUND)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
