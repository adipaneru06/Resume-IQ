/**
 * Resumely AI — Results Page Controller
 * Handles Chart.js radar chart visualization and clipboard copy helpers.
 */

function copyToClipboard(button, text) {
  navigator.clipboard.writeText(text).then(() => {
    const originalText = button.innerHTML;
    button.innerHTML = `
      <span class="material-symbols-outlined text-[16px] text-primary">check</span>
      <span class="text-primary font-semibold">Copied!</span>
    `;
    setTimeout(() => {
      button.innerHTML = originalText;
    }, 2000);
  }).catch(() => {
    alert("Unable to copy to clipboard.");
  });
}

function initRadarChart(sectionLabels, sectionScores) {
  const ctx = document.getElementById('sectionRadarChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: sectionLabels,
      datasets: [{
        label: 'Section Score',
        data: sectionScores,
        fill: true,
        backgroundColor: 'rgba(0, 86, 62, 0.12)',
        borderColor: '#00563e',
        pointBackgroundColor: '#00563e',
        pointBorderColor: '#ffffff',
        pointHoverBackgroundColor: '#ffffff',
        pointHoverBorderColor: '#00563e',
        pointRadius: 4,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          angleLines: {
            color: '#E6E2DA'
          },
          grid: {
            color: '#E6E2DA'
          },
          pointLabels: {
            font: {
              family: 'Inter',
              size: 12,
              weight: '500'
            },
            color: '#1c1b1b'
          },
          suggestedMin: 0,
          suggestedMax: 100,
          ticks: {
            stepSize: 20,
            display: false,
            backdropColor: 'transparent'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#1c1b1b',
          titleFont: { family: 'Inter', size: 12 },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 8,
          cornerRadius: 6,
          displayColors: false,
          callbacks: {
            label: function(context) {
              return ` Score: ${context.raw} / 100`;
            }
          }
        }
      }
    }
  });
}

