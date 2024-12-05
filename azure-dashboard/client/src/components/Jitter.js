import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Jitter = () => {
    const [metricsData, setMetricsData] = useState({});
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchLatencyData = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/vm-latency');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();

                // Group data by table (client_region + server_region combination)
                const groupedData = data.reduce((acc, item) => {
                    const key = `${item.client_region}-${item.server_region}`;
                    if (!acc[key]) {
                        acc[key] = [];
                    }

                    // Format timestamp in English locale
                    const timestamp = new Date(item.start_time).toLocaleString('en-US', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    });

                    acc[key].push({
                        timestamp,
                        jitter: item.jitter,
                        client_region: item.client_region,
                        server_region: item.server_region
                    });
                    return acc;
                }, {});

                // Sort data within each group
                Object.keys(groupedData).forEach(key => {
                    groupedData[key].sort((a, b) =>
                        new Date(a.timestamp) - new Date(b.timestamp)
                    );
                });

                setMetricsData(groupedData);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch latency data:', err);
                setError(err.message);
            }
        };

        fetchLatencyData();
        const intervalId = setInterval(fetchLatencyData, 60000);

        return () => clearInterval(intervalId);
    }, []);

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="custom-tooltip">
                    <p>Time: {data.timestamp}</p>
                    <p>Jitter: {data.jitter}ms</p>
                    <p>From: {data.client_region}</p>
                    <p>To: {data.server_region}</p>
                </div>
            );
        }
        return null;
    };

    // Function to calculate optimal Y-axis domain for each dataset
    const calculateYAxisDomain = (data) => {
        if (!data || data.length === 0) return [0, 0];

        const latencies = data.map(item => item.latency);
        const minLatency = Math.min(...latencies);
        const maxLatency = Math.max(...latencies);

        // Add 10% padding to the range
        const padding = (maxLatency - minLatency) * 0.1;
        return [
            Math.max(0, Math.floor(minLatency - padding)), // Don't go below 0
            Math.ceil(maxLatency + padding)
        ];
    };

    return (
        <div className="metrics-container">
            <h2 className="metrics-title">
                VM Jitter {error && '(Error: ' + error + ')'}
            </h2>
            <div className="metrics-grid">
                {Object.entries(metricsData).map(([key, data]) => {
                    const [clientRegion, serverRegion] = key.split('-');
                    const yAxisDomain = calculateYAxisDomain(data);

                    return (
                        <div key={key} className="metric-card">
                            <h3 className="metric-card-title">
                                {clientRegion} → {serverRegion}
                            </h3>
                            <div className="metric-chart">
                                <ResponsiveContainer width="100%" height={300}>
                                    <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 65 }}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis
                                            dataKey="timestamp"
                                            angle={-45}
                                            textAnchor="end"
                                            height={70}
                                            tick={{ fontSize: 10 }}
                                        />
                                        <YAxis
                                            domain={yAxisDomain}
                                            label={{
                                                value: 'Jitter (ms)',
                                                angle: -90,
                                                position: 'insideLeft',
                                                style: { fontSize: 12 }
                                            }}
                                            tick={{ fontSize: 12 }}
                                        />
                                        <Tooltip content={CustomTooltip} />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="jitter"
                                            stroke="#2ecc71"
                                            activeDot={{ r: 6 }}
                                            dot={false}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Jitter;