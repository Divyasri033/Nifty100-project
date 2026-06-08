// static/js/charts.js
// Helper functions for charts (optional)
function createRevenueChart(ctx, years, revenues) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Revenue (₹ Cr)',
                data: revenues,
                borderColor: 'rgb(59, 130, 246)',
                tension: 0.1
            }]
        }
    });
}