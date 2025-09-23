// App.js - Hydration logic for SPA functionality
import { interceptNavigation } from "./view-route.js";

// Load contents.json for SPA routing
let contentsData = null;

async function loadContents() {
  try {
    const response = await fetch('/contents.json');
    contentsData = await response.json();
  } catch (error) {
    console.error('Failed to load contents.json:', error);
  }
}

// Initialize SPA functionality
document.addEventListener('DOMContentLoaded', async () => {
  await loadContents();
  interceptNavigation(document.body);
});

// Export for potential external use
window.contentsData = contentsData;
