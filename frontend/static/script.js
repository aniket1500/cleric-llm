// document.addEventListener('DOMContentLoaded', function () {
//     // const baseUrl = window.location.origin;
//     const baseUrl = `${window.location.protocol}//${window.location.host}`;
//     console.log("baseUrl-->",baseUrl); 

//     async function submitDocuments() {
//         let question = document.getElementById('question').value;
//         let documents = document.getElementById('documents').value.split(',').map(s => s.trim().replace(/"/g, ''));
//         const resultSection = document.getElementById('results');
//         resultSection.innerHTML = 'Processing...';

//         try {
//             console.log("baseUrl-->",baseUrl); 
//             const response = await fetch(`${baseUrl}/submit_question_and_documents`, {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ question, documents })
//             });

//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }

//             const responseData = await response.json();
//             if (responseData.task_id !== undefined) {
//                 getFacts(responseData.task_id, resultSection);
//             } else {
//                 throw new Error('Invalid task ID received from server.');
//             }
//         } catch (error) {
//             resultSection.innerHTML = `Failed to submit documents: ${error.message}`;
//         }
//     }

//     async function getFacts(taskId, resultSection) {
//         try {
//             const response = await fetch(`${baseUrl}/get_question_and_facts?task_id=${taskId}`, {
//                 method: 'GET'
//             });

//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }

//             const data = await response.json();
//             if (data.status === 'done' && data.facts) {
//                 const factsListItems = data.facts.map(fact => `<li>${fact}</li>`).join('');
//                 resultSection.innerHTML = `<ul>${factsListItems}</ul>`;
//             } else if (data.status === 'processing') {
//                 setTimeout(() => getFacts(taskId, resultSection), 1000);
//             } else {
//                 resultSection.innerHTML = 'No facts available or processing not complete';
//             }
//         } catch (error) {
//             resultSection.innerHTML = 'An error occurred while fetching the facts: ' + error.message;
//         }
//     }

//     document.querySelector('button').addEventListener('click', submitDocuments);
// });

document.addEventListener('DOMContentLoaded', function () {
    const baseUrl = `${window.location.protocol}//${window.location.host}`;
    console.log("baseUrl-->",baseUrl);

    async function submitDocuments() {
        let question = document.getElementById('question').value.trim();
        let documents = document.getElementById('documents').value.split(',')
                        .map(s => s.trim())
                        .filter(s => s !== ''); // Ensure no empty strings are sent
        const resultSection = document.getElementById('results');
        resultSection.innerHTML = 'Processing...';

        try {
            console.log("Submitting documents with data:", { question, documents });
            const response = await fetch(`${baseUrl}/submit_question_and_documents`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, documents })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Directly initiate fact fetching since there is no task_id involved
            getFacts(resultSection);
        } catch (error) {
            resultSection.innerHTML = `Failed to submit documents: ${error.message}`;
        }
    }

    async function getFacts(resultSection) {
        try {
            console.log("Fetching facts from server");
            const response = await fetch(`${baseUrl}/get_question_and_facts`, {
                method: 'GET'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.status === 'done' && data.facts) {
                const factsListItems = data.facts.map(fact => `<li>${fact}</li>`).join('');
                resultSection.innerHTML = `<ul>${factsListItems}</ul>`;
            } else if (data.status === 'processing') {
                setTimeout(() => getFacts(resultSection), 1000); // Re-poll after 1 second
            } else {
                resultSection.innerHTML = 'No facts available or processing not complete';
            }
        } catch (error) {
            resultSection.innerHTML = `An error occurred while fetching the facts: ${error.message}`;
        }
    }

    document.querySelector('button').addEventListener('click', submitDocuments);
});
