const request = require('supertest');
const app = require('../server');

describe('IP Classifier API', () => {
  test('classifies valid IPv4 addresses', async () => {
    const response = await request(app).get('/?items=192.168.1.1,8.8.8.8');
    expect(response.status).toBe(200);
    expect(response.body.ipv4_count).toBe(2);
    expect(response.body.ipv6_count).toBe(0);
  });

  test('classifies valid IPv6 addresses', async () => {
    const response = await request(app).get('/?items=2001:db8::1,fe80::1');
    expect(response.body.ipv6_count).toBe(2);
  });

  test('identifies invalid IPs', async () => {
    const response = await request(app).get('/?items=999.999.999.999,invalid');
    expect(response.status).toBe(200);
    expect(response.body.invalid_count).toBe(2);
  });

  test('handles mixed IP types', async () => {
    const response = await request(app).get('/?items=192.168.1.1,2001:db8::1,invalid');
    expect(response.status).toBe(200);
    expect(response.body.total_items).toBe(3);
    expect(response.body.ipv4_count).toBe(1);
    expect(response.body.ipv6_count).toBe(1);
    expect(response.body.invalid_count).toBe(1);
  });

  test('handles empty IP addresses', async () => {
    const response = await request(app).get('/?items=192.168.1.1,,8.8.8.8');
    expect(response.status).toBe(200);
    expect(response.body.invalid_count).toBeGreaterThan(0);
  });

  test('returns usage info when items parameter is missing', async () => {
    const response = await request(app).get('/');
    expect(response.status).toBe(200);  
    expect(response.body.service).toBe('IP Classifier');
    expect(response.body.usage).toBeDefined(); 
  });
});