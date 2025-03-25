// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // HTMX will handle most of the requests, but we'll process the response data
    document.body.addEventListener('htmx:afterSwap', function(event) {
        const targetId = event.detail.target.id;
        
        if (targetId === 'participation-results' || targetId === 'voting-results') {
            try {
                const data = JSON.parse(event.detail.xhr.responseText);
                
                if (targetId === 'participation-results') {
                    // Render participation results
                    let template = document.getElementById('participation-template').innerHTML;
                    template = template.replace(/{{participation}}/g, data.participation);
                    template = template.replace(/{{voted_students}}/g, data.voted_students);
                    template = template.replace(/{{total_students}}/g, data.total_students);
                    
                    event.detail.target.innerHTML = template;
                }
                
                if (targetId === 'voting-results') {
                    // Render voting results
                    let template = document.getElementById('results-template').innerHTML;
                    let votesList = '';
                    
                    if (Object.keys(data.votes).length === 0) {
                        votesList = '<li class="list-group-item">Noch keine Stimmen abgegeben.</li>';
                    } else {
                        const sortedVotes = Object.entries(data.votes).sort((a, b) => b[1] - a[1]);
                        votesList = sortedVotes.map(([candidate, count]) => {
                            return `<li class="list-group-item d-flex justify-content-between align-items-center">
                                ${candidate}
                                <span class="badge bg-primary rounded-pill">${count} Stimmen</span>
                            </li>`;
                        }).join('');
                    }
                    
                    template = template.replace(/{{votesList}}/g, votesList);
                    event.detail.target.innerHTML = template;
                }
            } catch (error) {
                console.error('Error processing results:', error);
                event.detail.target.innerHTML = `<div class="alert alert-danger">Fehler beim Verarbeiten der Daten: ${error.message}</div>`;
            }
        }
    });
} 