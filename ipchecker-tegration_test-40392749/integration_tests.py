#!/usr/bin/env python3

import requests
import json
import sys
from typing import Dict, Any

# service URLs
SERVICES = {
    'Total IPs (PHP)': 'http://localhost:70',
    'Total Empty IPs (PHP)': 'http://localhost:90',
    'Valid IPs (Python)': 'http://localhost:3000',
    'Classifier (Node.js)': 'http://localhost:3001',
    'Country (Go)': 'http://localhost:8080',
    'Bad IPs (Ruby)': 'http://localhost:8081',
}

# test IP sets
TEST_SETS = {
    'basic_ipv4': '172.217.23.206,192.168.1.1,8.8.8.8',
    'with_empty': '172.217.23.206,,192.168.1.1',
    'mixed_ipv4_ipv6': '172.217.23.206,2001:db8::1,192.168.1.1',
    'bad_ips': '100.200.300.400,101.201.301.401',
    'invalid': 'invalid,999.999.999.999',
    'comprehensive': '172.217.23.206,100.200.300.400,,2001:db8::1,invalid,2a00:1450:400e:811::200e'
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

# test if service is running and healthy
def test_service_health(name: str, url: str) -> bool:
    try:
        response = requests.get(f'{url}/health', timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ {name}: Healthy{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ {name}: Unhealthy (Status {response.status_code}){Colors.END}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}❌ {name}: Cannot connect - {str(e)}{Colors.END}")
        return False

# test service with specific IP set
def test_service_endpoint(name: str, url: str, test_name: str, items: str) -> Dict[str, Any]:
    try:
        response = requests.get(f'{url}/?items={items}', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ {name} - {test_name}: OK{Colors.END}")
            return {'success': True, 'data': data}
        else:
            print(f"{Colors.RED}❌ {name} - {test_name}: Failed (Status {response.status_code}){Colors.END}")
            return {'success': False, 'error': f'Status {response.status_code}'}
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}❌ {name} - {test_name}: Timeout{Colors.END}")
        return {'success': False, 'error': 'Timeout'}
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}❌ {name} - {test_name}: Error - {str(e)}{Colors.END}")
        return {'success': False, 'error': str(e)}
    except json.JSONDecodeError:
        print(f"{Colors.RED}❌ {name} - {test_name}: Invalid JSON response{Colors.END}")
        return {'success': False, 'error': 'Invalid JSON'}
    
# test consistency across services
def test_consistency(items: str):

    print(f"\n{Colors.YELLOW}Testing consistency across services...{Colors.END}")
    
    expected_total = len(items.split(','))
    results = {}
    
    # test services that return total_items
    test_services = {
        'Python': 'http://localhost:3000',
        'Node.js': 'http://localhost:3001',
        'Go': 'http://localhost:8080',
        'Ruby': 'http://localhost:8081',
    }
    
    for name, url in test_services.items():
        try:
            response = requests.get(f'{url}/?items={items}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_items', 0)
                results[name] = total
                
                if total == expected_total:
                    print(f"{Colors.GREEN}✅ {name}: Correct total ({total}){Colors.END}")
                else:
                    print(f"{Colors.RED}❌ {name}: Wrong total (expected {expected_total}, got {total}){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ {name}: Error - {str(e)}{Colors.END}")
    
    # check if all services agree
    if len(set(results.values())) == 1:
        print(f"{Colors.GREEN}✅ All services agree on total count!{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Services disagree on total count: {results}{Colors.END}")

# run integration tests
def run_integration_tests():
    
    print_header("🧪 IPChecker Integration Tests")
    
    # test 1: health Checks
    print_header("Test 1: Service Health Checks")
    health_results = {}
    for name, url in SERVICES.items():
        health_results[name] = test_service_health(name, url)
    
    # check if all services are healthy
    all_healthy = all(health_results.values())
    if not all_healthy:
        print(f"\n{Colors.RED}⚠️  Some services are not running. Please start all services before running integration tests.{Colors.END}")
        sys.exit(1)
    
    # test 2: basic functionality
    print_header("Test 2: Basic Endpoint Testing")
    for name, url in SERVICES.items():
        test_service_endpoint(name, url, "Basic IPv4", TEST_SETS['basic_ipv4'])
    
    # test 3: edge cases
    print_header("Test 3: Edge Cases (Empty IPs)")
    for name, url in SERVICES.items():
        test_service_endpoint(name, url, "With Empty", TEST_SETS['with_empty'])
    
    # test 4: mixed IPv4/IPv6
    print_header("Test 4: Mixed IPv4 and IPv6")
    test_service_endpoint('Python', SERVICES['Valid IPs (Python)'], "Mixed IPs", TEST_SETS['mixed_ipv4_ipv6'])
    test_service_endpoint('Node.js', SERVICES['Classifier (Node.js)'], "Mixed IPs", TEST_SETS['mixed_ipv4_ipv6'])
    test_service_endpoint('Go', SERVICES['Country (Go)'], "Mixed IPs", TEST_SETS['mixed_ipv4_ipv6'])
    test_service_endpoint('Ruby', SERVICES['Bad IPs (Ruby)'], "Mixed IPs", TEST_SETS['mixed_ipv4_ipv6'])
    
    # test 5: bad IPs
    print_header("Test 5: Bad IP Detection")
    result = test_service_endpoint('Ruby', SERVICES['Bad IPs (Ruby)'], "Bad IPs", TEST_SETS['bad_ips'])
    if result['success']:
        bad_count = result['data'].get('bad_ip_count', 0)
        if bad_count == 2:
            print(f"{Colors.GREEN}✅ Bad IP detection working correctly (found {bad_count} bad IPs){Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Expected 2 bad IPs, found {bad_count}{Colors.END}")
    
    # test 6: consistency check
    print_header("Test 6: Cross-Service Consistency")
    test_consistency(TEST_SETS['comprehensive'])
    
    # test 7: comprehensive test
    print_header("Test 7: Comprehensive Test (All Features)")
    for name, url in SERVICES.items():
        test_service_endpoint(name, url, "Comprehensive", TEST_SETS['comprehensive'])
    
    # summary
    print_header("✅ Integration Tests Complete!")
    print(f"{Colors.GREEN}All tests finished. Check results above.{Colors.END}\n")

if __name__ == '__main__':
    try:
        run_integration_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error running tests: {str(e)}{Colors.END}")
        sys.exit(1)