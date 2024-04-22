from fastapi import FastAPI, HTTPException, Request, status, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import httpx
import openai
from dotenv import load_dotenv
import os
from threading import Lock, Thread
import asyncio
from datetime import datetime
import re
from .models import DocumentSubmission, GetQuestionAndFactsResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
port = int(os.getenv("PORT", "8000"))

tasks: Dict[int, Any] = {}
task_id_counter = 1
lock = Lock()

# @app.post("/submit_question_and_documents", status_code=status.HTTP_200_OK)
# @app.post("/submit_question_and_documents", status_code=200)
# async def submit_question_and_documents(data: DocumentSubmission):
#     print("Received data:", data.json())
#     global task_id_counter
#     with lock:
#         task_id = task_id_counter
#         task_id_counter += 1

#     task = {"question": data.question, "status": "processing", "facts": None}
#     with lock:
#         tasks[task_id] = task

#     thread = Thread(target=lambda: asyncio.run(fetch_and_process_documents(data.question, data.documents, task_id)))
#     thread.start()
#     # return {"message": "Processing started", "task_id": task_id}
#     return JSONResponse(content={"message": "Processing started", "task_id": task_id})

@app.post("/submit_question_and_documents", status_code=200)
async def submit_question_and_documents(data: DocumentSubmission = Body(...)):
    global task_id_counter
    with lock:
        task_id = task_id_counter
        task_id_counter += 1

    task = {"question": data.question, "status": "processing", "facts": None}
    tasks[task_id] = task

    thread = Thread(target=lambda: asyncio.run(fetch_and_process_documents(data.question, data.documents, task_id)))
    thread.start()

    return {"message": "Processing started", "task_id": task_id}

def sort_and_clean_urls(urls: List[str]) -> List[str]:
    clean_urls = [url.strip().strip('"') for url in urls]
    date_pattern = re.compile(r'\d{8}')
    return sorted(clean_urls, key=lambda x: datetime.strptime(date_pattern.search(x).group(), '%Y%m%d') if date_pattern.search(x) else datetime.min)


async def fetch_and_process_documents(question: str, urls: List[str], task_id: int):
    try:
        async with httpx.AsyncClient() as client:
            print("URLs being requested:", urls)  # Debug: Print URLs before requesting
            responses = await asyncio.gather(*(client.get(url) for url in urls))

        combined_documents = "\n".join(f"Call Log {i+1}\n{resp.text}" for i, resp in enumerate(responses) if resp.status_code == 200)
        print("combined_documents", combined_documents)
        print("question-->", question)
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Question: {question}\n\nDocuments: {combined_documents}\n\n\nBased on the above given question and call logs of the meetings. The call logs are provided in a sequential manner from old to most recent calls.  Write facts as a bulleted list without any dashes(-), using simple and clear language. You must not have unnecessary facts. Your list of facts must not have double facts (two facts per line). The order of calls changes the list of facts (e.g, the final call is the most important since its the most recent). Below is a detailed example of the entire process. Your task is to give final facts of the entire conversation keeping the above instructions in mind. Make sure to start each fact with 'The team has decided to'. \n\nDesired output format: \nFact 1\nFact 2\nand so on\n\nExample START:\nExample:\nCall Log 1\n\n1\n00:01:11,430 --> 00:01:40,520\nJohn: Hello, everybody. Let's start with the product design discussion. I think we should go with a modular design for our product. It will allow us to easily add or remove features as needed.\n\n2\n00:01:41,450 --> 00:01:49,190\nSara: I agree with John. A modular design will provide us with the flexibility we need. Also, I suggest we use a responsive design to ensure our product works well on all devices. Finally, I think we should use websockets to improve latency and provide real-time updates.\n\n3\n00:01:49,340 --> 00:01:50,040\nMike: Sounds good to me. I also propose we use a dark theme for the user interface. It's trendy and reduces eye strain for users. Let's hold off on the websockets for now since it's a little bit too much work.\n\nCall Log 2\n\n1\n00:01:11,430 --> 00:01:40,520\nJohn: After giving it some more thought, I believe we should also consider a light theme option for the user interface. This will cater to users who prefer a brighter interface.\n\n2\n00:01:41,450 --> 00:01:49,190\nSara: That's a great idea, John. A light theme will provide an alternative to users who find the dark theme too intense.\n\n3\n00:01:49,340 --> 00:01:50,040\nMike: I'm on board with that.\n\nCall Log 3\n\n1\n00:01:11,430 --> 00:01:40,520\nJohn: I've been thinking about our decision on the responsive design. While it's important to ensure our product works well on all devices, I think we should focus on desktop first. Our primary users will be using our product on desktops.\n\n2\n00:01:41,450 --> 00:01:49,190\nSara: I see your point, John. Focusing on desktop first will allow us to better cater to our primary users. I agree with this change.\n\n3\n00:01:49,340 --> 00:01:50,040\nMike: I agree as well. I also think the idea of using a modular design doesn't make sense. Let's not make that decision yet.\n\nQuestion: “What are our product design decisions?”\n\nThe team has decided to focus on a desktop-first design\nThe team has decided to provide both dark and light theme options for the user interface.\nExample END"}
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

# @app.get("/get_question_and_facts", response_model=GetQuestionAndFactsResponse)
# def get_question_and_facts(task_id: int):
#     task = tasks.get(task_id)
#     if task:
#         return JSONResponse(content=task, status_code=status.HTTP_200_OK)
#     else:
#         return JSONResponse(content={"message": "Task not found"}, status_code=status.HTTP_404_NOT_FOUND)

# @app.get("/get_question_and_facts")
# def get_question_and_facts(task_id: int = Query(..., description="The ID of the task to retrieve")):
#     task = tasks.get(task_id)
#     if task:
#         return JSONResponse(content=task, status_code=status.HTTP_200_OK)
#     else:
#         return JSONResponse(content={"message": "Task not found"}, status_code=status.HTTP_404_NOT_FOUND)
@app.get("/get_question_and_facts", response_model=GetQuestionAndFactsResponse)
def get_question_and_facts(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task['status'] == 'processing':
        return JSONResponse(status_code=202, content={"message": "Task still processing", "status": "processing"})
    
    if task['status'] == 'done':
        return task  # This assumes the task structure matches the response model directly

    raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    if request.method == "HEAD":
        # For HEAD requests, prepare the response but don't actually send content
        response = templates.TemplateResponse("index.html", {"request": request})
        response.body = b""  # Set response body to empty so nothing is sent
        return response
    # Normal GET request, return full page content
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

