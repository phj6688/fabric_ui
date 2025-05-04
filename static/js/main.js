// Helper function for tooltips on select options
function initializeTooltips() {
  const selects = document.querySelectorAll('select');
  
  selects.forEach(select => {
    select.addEventListener('mouseover', function(e) {
      if (e.target.tagName === 'OPTION') {
        const title = e.target.getAttribute('title');
        if (title) {
          const tooltip = document.createElement('div');
          tooltip.className = 'tooltip';
          tooltip.textContent = title;
          
          // Position tooltip
          const rect = e.target.getBoundingClientRect();
          tooltip.style.position = 'absolute';
          tooltip.style.top = rect.bottom + 5 + 'px';
          tooltip.style.left = rect.left + 'px';
          tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
          tooltip.style.padding = '5px 10px';
          tooltip.style.borderRadius = '4px';
          tooltip.style.zIndex = 1000;
          
          document.body.appendChild(tooltip);
          
          e.target.addEventListener('mouseout', function() {
            document.body.removeChild(tooltip);
          }, { once: true });
        }
      }
    });
  });
}

// Initialize functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeTooltips();
  
  // Automatically hide flash messages after 5 seconds
  const flashMessages = document.querySelectorAll('.alert');
  flashMessages.forEach(message => {
    setTimeout(() => {
      message.style.opacity = '0';
      setTimeout(() => {
        message.style.display = 'none';
      }, 500);
    }, 5000);
  });
});
