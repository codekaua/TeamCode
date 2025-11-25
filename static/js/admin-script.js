// Load data from JSON
let adminData = {};

async function loadData() {
    try {
        const response = await fetch('dados.json');
        const data = await response.json();
        adminData = data;
        updateUI();
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    }
}

function updateUI() {
    // Update admin info
    document.getElementById('adminName').textContent = adminData.admin.name;
    document.getElementById('adminEmail').textContent = adminData.admin.email;
    document.getElementById('adminCardName').textContent = adminData.admin.name;
    document.getElementById('adminCardEmail').textContent = adminData.admin.email;
    document.getElementById('adminCardDate').textContent = adminData.admin.joinDate;

    // Update stats
    document.getElementById('stat-visits').textContent = adminData.stats.visits.toLocaleString('pt-BR');
    document.getElementById('stat-clients').textContent = adminData.stats.clients.toLocaleString('pt-BR');
    document.getElementById('stat-products').textContent = adminData.stats.products.toLocaleString('pt-BR');

    // Draw charts
    drawLineChart();
    drawBarChart();
}

function drawLineChart() {
    const ctx = document.getElementById('lineChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: adminData.weeklyData.map(d => d.date),
            datasets: [{
                label: 'Acessos',
                data: adminData.weeklyData.map(d => d.visits),
                borderColor: '#000',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#000',
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#6b7280'
                    },
                    grid: {
                        color: '#e5e7eb'
                    }
                },
                x: {
                    ticks: {
                        color: '#6b7280'
                    },
                    grid: {
                        color: '#e5e7eb'
                    }
                }
            }
        }
    });
}

function drawBarChart() {
    const ctx = document.getElementById('barChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: adminData.weeklyData.map(d => d.date),
            datasets: [{
                label: 'Vendas',
                data: adminData.weeklyData.map(d => d.visits),
                backgroundColor: '#000',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#6b7280'
                    },
                    grid: {
                        color: '#e5e7eb'
                    }
                },
                x: {
                    ticks: {
                        color: '#6b7280'
                    },
                    grid: {
                        color: '#e5e7eb'
                    }
                }
            }
        }
    });
}

// Profile menu toggle
document.getElementById('profileBtn').addEventListener('click', function() {
    const menu = document.getElementById('menu');
    menu.classList.toggle('hidden');
});

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    const menu = document.getElementById('menu');
    const profileBtn = document.getElementById('profileBtn');
    if (!menu.contains(event.target) && !profileBtn.contains(event.target)) {
        menu.classList.add('hidden');
    }
});

// Load data on page load
window.addEventListener('DOMContentLoaded', loadData);
