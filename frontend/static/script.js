async function submitDocuments() {
    // let question = document.getElementById('question').value;
    // let documents = document.getElementById('documents').value.split(',').map(s => s.trim());
    let question = document.getElementById('question').value;
    let documents = document.getElementById('documents').value.split(',').map(s => s.trim().replace(/"/g, ''));
    const resultSection = document.getElementById('results');

    resultSection.innerHTML = 'Processing...';

    try {
        const response = await fetch('https://cleric-llm-1.onrender.com:10000/submit_question_and_documents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, documents })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        console.log('Response Data:', responseData);
        if (responseData.task_id !== undefined) {
            getFacts(responseData.task_id, resultSection);
        } else {
            throw new Error('Invalid task ID received from server.');
        }
    } catch (error) {
        resultSection.innerHTML = `Failed to submit documents: ${error.message}`;
    }
}

async function getFacts(taskId, resultSection) {
    try {
        const response = await fetch(`https://cleric-llm-1.onrender.com:10000/get_question_and_facts?task_id=${taskId}`,{
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Log and handle the response based on the status
        if (data.status === 'done' && data.facts) {
            console.log("Facts received:", data.facts);  // Debugging line to log the received facts
            const factsListItems = data.facts.map(fact => `<li>${fact}</li>`).join('');
            resultSection.innerHTML = `<ul>${factsListItems}</ul>`;  // Display the facts in a list format
        } else if (data.status === 'processing') {
            setTimeout(() => getFacts(taskId, resultSection), 1000);  // Polling again if the status is 'processing'
        } else {
            resultSection.innerHTML = 'No facts available or processing not complete';
        }
    } catch (error) {
        resultSection.innerHTML = 'An error occurred while fetching the facts: ' + error.message;
    }
}

