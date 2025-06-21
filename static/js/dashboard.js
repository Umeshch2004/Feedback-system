// Dashboard JavaScript functionality

function initSentimentChart(sentimentData) {
    const ctx = document.getElementById('sentimentChart');
    if (!ctx) return;
    
    // Process sentiment data
    const labels = [];
    const data = [];
    const colors = [];
    
    sentimentData.forEach(item => {
        const sentiment = item[0];
        const count = item[1];
        
        labels.push(sentiment.charAt(0).toUpperCase() + sentiment.slice(1));
        data.push(count);
        
        // Set colors based on sentiment
        if (sentiment === 'positive') {
            colors.push('#28a745');
        } else if (sentiment === 'neutral') {
            colors.push('#ffc107');
        } else {
            colors.push('#dc3545');
        }
    });
    
    // If no data, show empty state
    if (data.length === 0) {
        labels.push('No Data');
        data.push(1);
        colors.push('#6c757d');
    }
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        color: '#ffffff'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Add smooth scrolling for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Auto-refresh functionality for real-time updates
function refreshDashboard() {
    // Only refresh if user is still on the page
    if (document.visibilityState === 'visible') {
        fetch('/api/sentiment-data')
            .then(response => response.json())
            .then(data => {
                if (data.labels && data.data) {
                    updateSentimentChart(data);
                }
            })
            .catch(error => {
                console.log('Failed to refresh dashboard data:', error);
            });
    }
}

function updateSentimentChart(data) {
    const chart = Chart.getChart('sentimentChart');
    if (chart) {
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.data;
        chart.update();
    }
}

// Set up periodic refresh (every 5 minutes)
setInterval(refreshDashboard, 300000);
