const express = require('express');
const app = express();
const port = process.env.PORT || 3001;


app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// helper function to validate IPv4
function isValidIPv4(ip) {
  const ipv4Pattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
  const match = ip.match(ipv4Pattern);
  if (!match) return false;
  
  // check each octet is 0-255
  for (let i = 1; i <= 4; i++) {
    const num = parseInt(match[i], 10);
    if (num < 0 || num > 255) return false;
  }
  return true;
}

// helper function to validate IPv6 -- options possibility of :: compression
function isValidIPv6(ip) {
  // IPv6 regex that handles :: compression and various formats
  const ipv6Patterns = [
    // full address (8 groups)
    /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/,
    // compressed with :: at the end
    /^([0-9a-fA-F]{1,4}:){1,7}:$/,
    // compressed with :: at the start
    /^:([0-9a-fA-F]{1,4}:){1,7}$/,
    // compressed with :: in the middle
    /^([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}$/,
    /^([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}$/,
    /^([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}$/,
    /^([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}$/,
    /^([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}$/,
    /^[0-9a-fA-F]{1,4}:(:[0-9a-fA-F]{1,4}){1,6}$/,
    // :: only (all zeros)
    /^::$/,
    // :: with one group
    /^::([0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}$/,
    /^([0-9a-fA-F]{1,4}:){1,6}::$/
  ];
  
  return ipv6Patterns.some(pattern => pattern.test(ip));
}

// helper function to classify IP type
function classifyIP(ip) {
  if (!ip || ip.trim() === '') {
    return { type: 'invalid', reason: 'empty' };
  }
  
  // check IPv4
  if (isValidIPv4(ip)) {
    return { type: 'IPv4', valid: true };
  }
  
  // check IPv6
  if (isValidIPv6(ip)) {
    return { type: 'IPv6', valid: true };
  }
  
  return { type: 'invalid', reason: 'malformed' };
}

// main endpoint
app.get('/', (req, res) => {
  const items = req.query.items || '';
  
  // if no items parameter, show usage info
  if (!items) {
    return res.json({
      service: 'IP Classifier',
      version: '1.0.0',
      student: '40392749',
      description: 'Classifies IP addresses as IPv4, IPv6, or invalid',
      usage: '/?items=ip1,ip2,ip3',
      examples: [
        '/?items=192.168.1.1',
        '/?items=192.168.1.1,8.8.8.8',
        '/?items=192.168.1.1,2001:db8::1,999.999.999.999',
        '/?items=fe80::1,2001:0db8:85a3:0000:0000:8a2e:0370:7334'
      ],
      endpoints: {
        main: '/?items=comma,separated,ips',
        health: '/health'
      }
    });
  }
  
  // split by comma and process each IP
  const ipList = items.split(',').map(ip => ip.trim());
  const results = ipList.map(ip => {
    const classification = classifyIP(ip);
    return {
      ip: ip || '(empty)',
      ...classification
    };
  });
  
  // count valid IPs by type
  const ipv4Count = results.filter(r => r.type === 'IPv4').length;
  const ipv6Count = results.filter(r => r.type === 'IPv6').length;
  const invalidCount = results.filter(r => r.type === 'invalid').length;
  
  res.json({
    total_items: ipList.length,
    ipv4_count: ipv4Count,
    ipv6_count: ipv6Count,
    unknown_count: invalidCount,
    details: results
  });
});

// health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'ipchecker-classifier',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// export for testing
module.exports = app;

// only start server if not in test mode
if (require.main === module) {
  app.listen(port, '0.0.0.0', () => {
    console.log(`IP Classifier service listening on port ${port}`);
  });
}