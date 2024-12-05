const axios = require('axios'); // HTTP client for requests

// Define the server URL and endpoint
const SERVER_URL = 'http://localhost:5000/api/vm-latency'; // Adjust path as needed

async function fetchData() {
  try {
    // Send GET request to the server
    const response = await axios.get(SERVER_URL);

    // Print the data from the response
    console.log('Data fetched from server:', response.data);
  } catch (error) {
    // Handle errors
    console.error('Error fetching data:', error.message);
  }
}

// Call the fetchData function
fetchData();
