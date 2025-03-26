// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    
    // Delay initial load slightly to ensure DOM is fully ready
    setTimeout(() => {
        // Initial load of data
        fetchResults();
        fetchVotedStudents();
    }, 100);
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
            // Add spinner effect to button when clicked
            this.classList.add('disabled');
            const originalText = this.innerHTML;
            this.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Lade...`;
            
            const targetId = this.getAttribute('hx-target').substring(1); // Remove the # from the ID
            fetchResults(targetId).finally(() => {
                // Restore button after fetch completes (whether successful or not)
                setTimeout(() => {
                    this.classList.remove('disabled');
                    this.innerHTML = originalText;
                }, 500);
            });
        });
    });
    
    // Add click animation to votedStudents button
    document.getElementById('load-voted-students').addEventListener('click', function() {
        this.classList.add('disabled');
        const originalText = this.innerHTML;
        this.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Lade...`;
        
        fetchVotedStudents().finally(() => {
            // Restore button
            setTimeout(() => {
                this.classList.remove('disabled');
                this.innerHTML = originalText;
            }, 500);
        });
    });
}

function fetchResults(targetId = null) {
    // Add a slight shimmer effect to cards during loading
    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0.8';
    });
    
    // Fetch results manually in case HTMX doesn't work
    return fetch('/results')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Reset card opacity
            document.querySelectorAll('.card').forEach(card => {
                card.style.opacity = '1';
            });
            
            // Update the stats boxes
            updateStatCounters(data);
            
            if (targetId) {
                // Update specific target
                processResultsData(data, targetId);
            } else {
                // Update both targets
                processResultsData(data, 'participation-results');
                processResultsData(data, 'voting-results');
            }
            
            return data;
        })
        .catch(error => {
            console.error('Error fetching results:', error);
            
            // Reset card opacity on error
            document.querySelectorAll('.card').forEach(card => {
                card.style.opacity = '1';
            });
            
            if (targetId) {
                document.getElementById(targetId).innerHTML = 
                    `<div class="alert alert-danger">Fehler beim Abrufen der Daten: ${error.message}</div>`;
            }
            
            throw error;
        });
}

// Function to update stats counters
function updateStatCounters(data) {
    // Update stats counters with animation
    const totalStudentsElement = document.getElementById('total-students-count');
    const votedStudentsElement = document.getElementById('voted-students-count');
    const participationElement = document.getElementById('participation-percentage');
    
    if (totalStudentsElement) {
        animateValue(totalStudentsElement, parseInt(totalStudentsElement.innerText) || 0, data.total_students, 1000);
    }
    
    if (votedStudentsElement) {
        animateValue(votedStudentsElement, parseInt(votedStudentsElement.innerText) || 0, data.voted_students, 1000);
    }
    
    if (participationElement) {
        const currentParticipation = parseFloat(participationElement.innerText) || 0;
        const targetParticipation = parseFloat(data.participation) || 0;
        animateValue(participationElement, currentParticipation, targetParticipation.toFixed(1), 1000, '%');
    }
}

// Function to animate counting for stat counters
function animateValue(element, start, end, duration, suffix = '') {
    if (isNaN(start) || start === '-') start = 0;
    if (isNaN(end)) end = 0;
    
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.innerHTML = value + suffix;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            element.innerHTML = end + suffix;
        }
    };
    window.requestAnimationFrame(step);
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
        
        // Ensure participation is properly formatted
        const participation = parseFloat(data.participation) || 0;
        const votedStudents = parseInt(data.voted_students) || 0;
        const totalStudents = parseInt(data.total_students) || 0;
        
        template = template.replace(/{{participation}}/g, participation.toFixed(1));
        template = template.replace(/{{voted_students}}/g, votedStudents);
        template = template.replace(/{{total_students}}/g, totalStudents);
        template = template.replace(/{{currentTime}}/g, currentTime);
        
        targetElement.innerHTML = template;
        
        // Also directly set the values in case the templating fails
        const progressBar = targetElement.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = participation + '%';
            progressBar.textContent = participation.toFixed(1) + '%';
            
            // Add color-based classes based on participation percentage
            progressBar.classList.remove('bg-danger', 'bg-warning', 'bg-success');
            if (participation < 30) {
                progressBar.classList.add('bg-danger');
            } else if (participation < 70) {
                progressBar.classList.add('bg-warning');
            } else {
                progressBar.classList.add('bg-success');
            }
        }
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
                
                // Calculate percentage for progress bar
                const totalVotes = Object.values(data.votes).reduce((sum, c) => sum + c, 0);
                const percentage = totalVotes > 0 ? Math.round((count / totalVotes) * 100) : 0;
                
                // Add progress bar representing percentage of votes
                const progressBar = `
                    <div class="progress mt-1">
                        <div class="progress-bar" role="progressbar" 
                            style="width: ${percentage}%; height: 8px" 
                            aria-valuenow="${percentage}" 
                            aria-valuemin="0" 
                            aria-valuemax="100"></div>
                    </div>
                `;
                
                return `<li class="list-group-item d-flex flex-column ${winnerClass}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-user-circle me-2" style="color: var(--primary-color);"></i>
                            ${candidate}${winnerBadge}
                        </div>
                        <span class="badge bg-primary rounded-pill">${count} Stimmen (${percentage}%)</span>
                    </div>
                    ${progressBar}
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
    
    // Generate better brand colors instead of random ones
    const predefinedColors = [
        'rgba(67, 97, 238, 0.7)',   // Primary
        'rgba(76, 201, 240, 0.7)',  // Success
        'rgba(247, 37, 133, 0.7)',  // Accent
        'rgba(58, 12, 163, 0.7)',   // Deep purple
        'rgba(114, 9, 183, 0.7)',   // Purple
        'rgba(255, 87, 51, 0.7)',   // Orange
        'rgba(255, 195, 0, 0.7)',   // Yellow
        'rgba(0, 180, 216, 0.7)',   // Teal
    ];
    
    // Ensure we have enough colors by repeating the predefined colors if needed
    const backgroundColors = candidates.map((_, index) => 
        predefinedColors[index % predefinedColors.length]
    );
    
    // Check if chart instance already exists and destroy it
    if (window.votingPieChart) {
        window.votingPieChart.destroy();
    }
    
    // Create new chart with animations
    window.votingPieChart = new Chart(chartCanvas, {
        type: 'doughnut', // Changed from pie to doughnut for a more modern look
        data: {
            labels: candidates,
            datasets: [{
                data: voteCounts,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                borderWidth: 2,
                hoverBackgroundColor: backgroundColors.map(color => color.replace('0.7', '0.9')),
                hoverBorderColor: 'white',
                hoverBorderWidth: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1000,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                            size: 12
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
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
                    },
                    titleFont: {
                        family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                        size: 14
                    },
                    bodyFont: {
                        family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                        size: 14
                    },
                    padding: 12,
                    cornerRadius: 8
                }
            }
        }
    });
}

// Function to fetch and display who has voted
function fetchVotedStudents() {
    // Add loading effect
    const votedListElement = document.getElementById('voted-students-list');
    if (votedListElement) {
        votedListElement.innerHTML = `
            <div class="d-flex justify-content-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }
    
    return fetch('/voted-students')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!votedListElement) return;
            
            if (data.voted_students.length === 0) {
                votedListElement.innerHTML = '<li class="list-group-item text-center">Noch niemand hat abgestimmt.</li>';
            } else {
                // Add with animation
                votedListElement.innerHTML = '';
                
                // Add students with a staggered animation
                data.voted_students.forEach((student, index) => {
                    setTimeout(() => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item animate__animated animate__fadeInRight';
                        li.innerHTML = `<i class="fas fa-user-check me-2" style="color: var(--success-color);"></i>${student}`;
                        votedListElement.appendChild(li);
                    }, index * 100); // Stagger the animations
                });
            }
        })
        .catch(error => {
            console.error('Error fetching voted students:', error);
            if (votedListElement) {
                votedListElement.innerHTML = 
                    `<div class="alert alert-danger">Fehler beim Abrufen der Daten: ${error.message}</div>`;
            }
            throw error;
        });
} 