// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    // Initial load of data
    fetchResults();
    fetchVotedStudents(); // Load voted students immediately
});

function setupEventListeners() {
    // HTMX will handle most of the requests, but we'll process the response data manually
    document.body.addEventListener('htmx:afterSwap', function(event) {
        const targetId = event.detail.target.id;
        
        if (targetId === 'participation-results' || targetId === 'voting-results') {
            try {
                const data = JSON.parse(event.detail.xhr.responseText);
                processResultsData(data, targetId);
            } catch (error) {
                console.error('Error processing results:', error);
                event.detail.target.innerHTML = `<div class="alert alert-danger">Fehler beim Verarbeiten der Daten: ${error.message}</div>`;
            }
        }
    });

    // Add manual click handlers as backup
    document.querySelectorAll('[hx-get="/results"]').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('hx-target').substring(1); // Remove the # from the ID
            fetchResults(targetId);
        });
    });
}

function fetchResults(targetId = null) {
    // Fetch results manually in case HTMX doesn't work
    fetch('/results')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (targetId) {
                // Update specific target
                processResultsData(data, targetId);
            } else {
                // Update both targets
                processResultsData(data, 'participation-results');
                processResultsData(data, 'voting-results');
            }
        })
        .catch(error => {
            console.error('Error fetching results:', error);
            if (targetId) {
                document.getElementById(targetId).innerHTML = 
                    `<div class="alert alert-danger">Fehler beim Abrufen der Daten: ${error.message}</div>`;
            }
        });
}

function processResultsData(data, targetId) {
    const targetElement = document.getElementById(targetId);
    if (!targetElement) return;

    // Get current time for update timestamp
    const now = new Date();
    const currentTime = now.toLocaleTimeString();

    if (targetId === 'participation-results') {
        // Render participation results
        let template = document.getElementById('participation-template').innerHTML;
        template = template.replace(/{{participation}}/g, data.participation);
        template = template.replace(/{{voted_students}}/g, data.voted_students);
        template = template.replace(/{{total_students}}/g, data.total_students);
        template = template.replace(/{{currentTime}}/g, currentTime);
        
        targetElement.innerHTML = template;
    }
    
    if (targetId === 'voting-results') {
        // Render voting results
        let template = document.getElementById('results-template').innerHTML;
        let votesList = '';
        
        if (Object.keys(data.votes).length === 0) {
            votesList = '<li class="list-group-item">Noch keine Stimmen abgegeben.</li>';
        } else {
            const sortedVotes = Object.entries(data.votes).sort((a, b) => b[1] - a[1]);
            
            // Find the winner (highest vote count)
            const highestVoteCount = sortedVotes.length > 0 ? sortedVotes[0][1] : 0;
            
            votesList = sortedVotes.map(([candidate, count], index) => {
                // Add winner class to the candidate with the highest vote count
                const isWinner = count === highestVoteCount;
                const winnerClass = isWinner ? 'winner' : '';
                const winnerBadge = isWinner ? '<span class="badge bg-success ms-2">Gewinner</span>' : '';
                
                return `<li class="list-group-item d-flex justify-content-between align-items-center ${winnerClass}">
                    ${candidate}${winnerBadge}
                    <span class="badge bg-primary rounded-pill">${count} Stimmen</span>
                </li>`;
            }).join('');
            
            // Create or update the pie chart
            setTimeout(() => {
                createVotingPieChart(data.votes);
            }, 100);
        }
        
        template = template.replace(/{{votesList}}/g, votesList);
        template = template.replace(/{{currentTime}}/g, currentTime);
        targetElement.innerHTML = template;
    }
}

// Create a pie chart for voting results
function createVotingPieChart(votes) {
    const chartCanvas = document.getElementById('voting-pie-chart');
    if (!chartCanvas) return;
    
    // Extract data for the chart
    const candidates = Object.keys(votes);
    const voteCounts = Object.values(votes);
    
    // Generate random colors for each candidate
    const backgroundColors = candidates.map(() => 
        `rgba(${Math.floor(Math.random() * 200)}, ${Math.floor(Math.random() * 200)}, ${Math.floor(Math.random() * 200)}, 0.7)`
    );
    
    // Check if chart instance already exists and destroy it
    if (window.votingPieChart) {
        window.votingPieChart.destroy();
    }
    
    // Create new chart
    window.votingPieChart = new Chart(chartCanvas, {
        type: 'pie',
        data: {
            labels: candidates,
            datasets: [{
                data: voteCounts,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} Stimmen (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Function to fetch and display who has voted
function fetchVotedStudents() {
    fetch('/voted-students')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const votedListElement = document.getElementById('voted-students-list');
            if (!votedListElement) return;
            
            if (data.voted_students.length === 0) {
                votedListElement.innerHTML = '<li class="list-group-item">Noch niemand hat abgestimmt.</li>';
            } else {
                votedListElement.innerHTML = data.voted_students
                    .map(student => `<li class="list-group-item">${student}</li>`)
                    .join('');
            }
        })
        .catch(error => {
            console.error('Error fetching voted students:', error);
            document.getElementById('voted-students-list').innerHTML = 
                `<div class="alert alert-danger">Fehler beim Abrufen der Daten: ${error.message}</div>`;
        });
} 