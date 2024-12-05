const mysql = require('mysql2/promise');

const config = {
  host: 'some',
  user: 'fake',
  password: 'login',
  database: 'info',
  port: 3306
};

async function connectAndQuery() {
  try {
    // Establish a connection
    const connection = await mysql.createConnection(config);
    console.log("Connection established");
    
    // Get all tables
    const [tables] = await connection.execute('SHOW TABLES');
    
    // Initialize array to store all data
    let allData = [];
    
    // Iterate through tables and collect data
    for (const table of tables) {
      const tableName = table['Tables_in_server-client-logs'];
      const [rows] = await connection.execute(`SELECT * FROM ${tableName}`);
      
      // Transform timestamps to ISO string format for better display
      const transformedRows = rows.map(row => ({
        ...row,
        start_time: new Date(row.start_time * 1000).toISOString(),
        end_time: new Date(row.end_time * 1000).toISOString(),
      }));
      
      allData = [...allData, ...transformedRows];
    }
    
    // Close the connection
    await connection.end();
    
    // Sort data by start_time
    allData.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    
    return allData;

  } catch (err) {
    if (err.code === 'PROTOCOL_CONNECTION_LOST') {
      throw new Error('Database connection was closed.');
    }
    if (err.code === 'ER_CON_COUNT_ERROR') {
      throw new Error('Database has too many connections.');
    }
    if (err.code === 'ECONNREFUSED') {
      throw new Error('Database connection was refused.');
    }
    throw err;
  }
}

module.exports = { connectAndQuery };