import unittest
import json
from app import app, is_valid_ipv4, is_valid_ipv6, count_valid_ips

class TestIPValidator(unittest.TestCase):
    # test cases for IP validation service
    
    def setUp(self):
        # set up (client)
        self.app = app.test_client()
        self.app.testing = True
    
    # unit tests for validation functions
    def test_valid_ipv4(self):
        # test with valid IPv4 addresses
        self.assertTrue(is_valid_ipv4('172.217.23.206'))
        self.assertTrue(is_valid_ipv4('1.21.23.206'))
        self.assertTrue(is_valid_ipv4('192.168.1.1'))
    
    def test_invalid_ipv4(self):
        # test with invalid iPv4 addresses
        self.assertFalse(is_valid_ipv4('172.217.23.206.100')) 
        self.assertFalse(is_valid_ipv4('172.217.23'))
        self.assertFalse(is_valid_ipv4(''))
        self.assertFalse(is_valid_ipv4('   '))
    
    def test_valid_ipv6(self):
        # test with valid IPv6 addresses
        self.assertTrue(is_valid_ipv6('2a00:1450:400e:811::200e'))
        self.assertTrue(is_valid_ipv6('2:145:40:811::200e'))
        self.assertTrue(is_valid_ipv6('2:145:40'))
        self.assertTrue(is_valid_ipv6('fe80::1'))
    
    def test_invalid_ipv6(self):
        # test with invalid IPv6 addresses
        self.assertFalse(is_valid_ipv6('2a00:1450:400e:811::200e:xxxx:xx:xxx'))  # 9 groups
        self.assertFalse(is_valid_ipv6('2'))
        self.assertFalse(is_valid_ipv6(''))
    
    def test_count_valid_ips(self):
        # counting
        # test with mixed valid IPs
        items = '172.217.23.206,2a00:1450:400e:811::200e,invalid'
        count, details = count_valid_ips(items)
        self.assertEqual(count, 2)
        
        # test with empty IPs
        items = '172.217.23.206,,2a00:1450:400e:811::200e'
        count, details = count_valid_ips(items)
        self.assertEqual(count, 2)
        
        # test with all invalid
        items = 'invalid1,invalid2,invalid3'
        count, details = count_valid_ips(items)
        self.assertEqual(count, 0)
    
    # API tests
    def test_endpoint_valid_ips(self):
        # test with mixed valid IPs
        response = self.app.get('/?items=172.217.23.206,2a00:1450:400e:811::200e')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['valid_count'], 2)
        self.assertEqual(data['error'], '')
    
    def test_endpoint_with_empty_ips(self):
        # test with empty IPs
        response = self.app.get('/?items=172.217.23.206,,2a00:1450:400e:811::200e')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['valid_count'], 2)
        self.assertEqual(data['total_items'], 3)
    
    def test_endpoint_no_items(self):
        # test with no items
        response = self.app.get('/')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertNotEqual(data['error'], '')
        self.assertEqual(data['valid_count'], 0)
    
    def test_endpoint_invalid_ips(self):
        # test with invalid IPs
        response = self.app.get('/?items=172.217.23.206.100,not-an-ip')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['valid_count'], 0)
    
    def test_health_endpoint(self):
        # test health endpoint
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

if __name__ == '__main__':
    unittest.main()
