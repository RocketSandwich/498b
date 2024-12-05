const express = require('express');
const app = express();
const cors = require('cors');
const { connectAndQuery } = require('./dbConfig');

const PORT = process.env.PORT || 5000;

// Middleware
app.use(express.json());
app.use(cors());

// Route for VM Latency
app.get('/api/vm-latency', async (req, res) => {
  try {
    const latencyData = await connectAndQuery();
    console.log('VM Latency Data:', latencyData);
    res.json(latencyData);
  } catch (error) {
    console.error('Error fetching VM latency data:', error);
    res.status(500).json({ 
      error: 'Failed to retrieve latency data', 
      details: error.message 
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});