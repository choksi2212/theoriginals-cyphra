// Chart.js Configuration - Realistic Indian Market Data
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';

const colors = {
    primary: '#1a365d', secondary: '#2563eb', accent: '#10b981',
    warning: '#f59e0b', danger: '#ef4444', info: '#06b6d4',
    success: '#10b981', purple: '#8b5cf6', pink: '#ec4899',
    textLight: '#e2e8f0', textDark: '#94a3b8'
};

// Home Page - Revenue Chart
const revenueChartCanvas = document.getElementById('revenueChart');
if (revenueChartCanvas) {
    new Chart(revenueChartCanvas, {
        type: 'line',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'Revenue (₹ Lakhs)',
                data: [3.5, 18, 60, 150, 250],
                borderColor: colors.secondary,
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 3, fill: true, tension: 0.4
            }, {
                label: 'Profit (₹ Lakhs)',
                data: [-6.5, -3.3, 12.2, 48.3, 94.5],
                borderColor: colors.accent,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3, fill: true, tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: '5-Year Revenue & Profit (₹ Lakhs)', 
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'top', labels: { color: colors.textLight } }
            },
            scales: {
                y: { beginAtZero: false, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => '₹' + v + 'L' } },
                x: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: colors.textLight } }
            }
        }
    });
}

// Startup Costs - Pie Chart
const fundsChartCanvas = document.getElementById('fundsChart');
if (fundsChartCanvas) {
    new Chart(fundsChartCanvas, {
        type: 'doughnut',
        data: {
            labels: ['Development (₹4.5L)', 'Marketing (₹2L)', 'Legal (₹1L)', 'Operations (₹1L)'],
            datasets: [{
                data: [4.5, 2, 1, 1],
                backgroundColor: [colors.secondary, colors.accent, colors.warning, colors.info],
                borderWidth: 2, borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Startup Cost Breakdown (₹8.5 Lakhs Total)',
                        font: { size: 16, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'bottom', labels: { color: colors.textLight, padding: 15 } }
            }
        }
    });
}

// Revenue Page - User Growth
const userGrowthCanvas = document.getElementById('userGrowthChart');
if (userGrowthCanvas) {
    new Chart(userGrowthCanvas, {
        type: 'bar',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'Free Users',
                data: [9850, 49100, 196000, 588000, 980000],
                backgroundColor: colors.info
            }, {
                label: 'Paying Users',
                data: [150, 900, 4000, 12000, 20000],
                backgroundColor: colors.accent
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'User Growth Projection',
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'top', labels: { color: colors.textLight } }
            },
            scales: {
                x: { stacked: true, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight } },
                y: { stacked: true, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => (v/1000) + 'K' } }
            }
        }
    });
}

// Revenue Page - Revenue by Tier
const revenueTierCanvas = document.getElementById('revenueTierChart');
if (revenueTierCanvas) {
    new Chart(revenueTierCanvas, {
        type: 'bar',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'Pro Monthly (₹29/mo)',
                data: [1.5, 8, 28, 70, 120],
                backgroundColor: colors.secondary
            }, {
                label: 'Pro Annual (₹199/yr)',
                data: [2, 10, 32, 80, 130],
                backgroundColor: colors.accent
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Revenue by Tier (₹ Lakhs)',
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'top', labels: { color: colors.textLight } }
            },
            scales: {
                x: { stacked: true, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight } },
                y: { stacked: true, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => '₹' + v + 'L' } }
            }
        }
    });
}

// Expenses Page - Expense Breakdown
const expenseCanvas = document.getElementById('expenseChart');
if (expenseCanvas) {
    new Chart(expenseCanvas, {
        type: 'bar',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'Salaries',
                data: [6, 12, 24, 45, 60],
                backgroundColor: colors.secondary
            }, {
                label: 'Marketing',
                data: [2, 5, 10, 20, 30],
                backgroundColor: colors.accent
            }, {
                label: 'Infrastructure',
                data: [0.5, 1, 2, 4, 5],
                backgroundColor: colors.warning
            }, {
                label: 'Operations',
                data: [1, 2, 4, 6, 10],
                backgroundColor: colors.info
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Operating Expenses by Category (₹ Lakhs)',
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'top', labels: { color: colors.textLight } }
            },
            scales: {
                x: { stacked: true, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight } },
                y: { stacked: true, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => '₹' + v + 'L' } }
            }
        }
    });
}

// Cash Flow Page - Monthly Cash Flow
const cashFlowCanvas = document.getElementById('cashFlowChart');
if (cashFlowCanvas) {
    new Chart(cashFlowCanvas, {
        type: 'line',
        data: {
            labels: ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12'],
            datasets: [{
                label: 'Monthly Revenue',
                data: [0, 0.1, 0.2, 0.25, 0.28, 0.3, 0.32, 0.35, 0.38, 0.4, 0.42, 0.45],
                borderColor: colors.accent,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2, fill: true, tension: 0.4
            }, {
                label: 'Monthly Expenses',
                data: [1.2, 1, 0.9, 0.85, 0.82, 0.8, 0.78, 0.77, 0.76, 0.75, 0.75, 0.75],
                borderColor: colors.danger,
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 2, fill: true, tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Monthly Cash Flow - Year 1 (₹ Lakhs)',
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'top', labels: { color: colors.textLight } }
            },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: colors.textLight } },
                y: { grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => '₹' + v + 'L' } }
            }
        }
    });
}

// Metrics Page - CAC Trend
const cacTrendCanvas = document.getElementById('cacTrendChart');
if (cacTrendCanvas) {
    new Chart(cacTrendCanvas, {
        type: 'line',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'CAC (₹)',
                data: [1333, 667, 323, 375, 375],
                borderColor: colors.danger,
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 3, fill: true, tension: 0.4
            }, {
                label: 'LTV (₹)',
                data: [360, 380, 400, 420, 450],
                borderColor: colors.accent,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3, fill: true, tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'CAC vs LTV Trend',
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'top', labels: { color: colors.textLight } }
            },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: colors.textLight } },
                y: { grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => '₹' + v } }
            }
        }
    });
}

// Financials Page - Profit Margins
const marginsCanvas = document.getElementById('marginsChart');
if (marginsCanvas) {
    new Chart(marginsCanvas, {
        type: 'line',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'Gross Margin %',
                data: [91, 94, 97, 97, 97],
                borderColor: colors.accent,
                borderWidth: 2, tension: 0.4
            }, {
                label: 'Net Margin %',
                data: [-186, -18, 20, 32, 38],
                borderColor: colors.secondary,
                borderWidth: 2, tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Profit Margins Over Time',
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { position: 'top', labels: { color: colors.textLight } }
            },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: colors.textLight } },
                y: { grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => v + '%' } }
            }
        }
    });
}

// Exit Strategy - Valuation Scenarios
const valuationCanvas = document.getElementById('valuationChart');
if (valuationCanvas) {
    new Chart(valuationCanvas, {
        type: 'bar',
        data: {
            labels: ['Conservative\n(5x Revenue)', 'Base Case\n(6x Revenue)', 'Optimistic\n(8x Revenue)'],
            datasets: [{
                label: 'Valuation (₹ Crore)',
                data: [12.5, 15, 20],
                backgroundColor: [colors.warning, colors.secondary, colors.accent],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Year 5 Valuation Scenarios',
                        font: { size: 18, weight: 'bold' }, color: colors.textLight },
                legend: { display: false }
            },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: colors.textLight } },
                y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: colors.textLight, callback: v => '₹' + v + ' Cr' } }
            }
        }
    });
}
