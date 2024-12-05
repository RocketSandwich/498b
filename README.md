# 498b
Includes traffic generator code for analyzing performance in geo-distributed VM Infrastructure (CMSC498B Capstone)
Maybe also vm image config for azure provisioning

To initialize dashboard:
- In a terminal, run "npm install" in both the azure-dashboard folder and the client folder in the azure-dashboard folder


To run dashboard:
- In a terminal, run "node server.js" in the azure-dashboard folder
- In another terminal, run "npm run start" in the client folder


TODOs:
- Implement periodic messaging with x second intervals
- Implement in C to test language traffic differences
- Use UDP datagram connections on top of streams
- Test traceroute & iperf and how to potentially integarate them
- What should the payload be?
    - something meaningful?
    - Self-defined header
    - timestamp...
- p2p network