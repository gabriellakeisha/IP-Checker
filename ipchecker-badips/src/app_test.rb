require 'minitest/autorun'
require 'rack/test'
require_relative 'app'

class AppTest < Minitest::Test
  include Rack::Test::Methods

  def app
    Sinatra::Application
  end

  # test: IPv4 validation
  def test_ipv4_valid
    assert ipv4?('172.217.23.206')
    assert ipv4?('100.200.300.400')
  end

  def test_ipv4_invalid
    refute ipv4?('172.217.23.206.100') 
    refute ipv4?('172.217.23')
    refute ipv4?('')
  end

  # est: bad IP detection
  def test_bad_ip_detection
    assert bad_ip?('100.200.300.400')
    assert bad_ip?('101.201.301.401')
    assert bad_ip?('102.202.302.402')
    assert bad_ip?('103.203.303.403')
    refute bad_ip?('172.217.23.206')
  end

  # test: process IPs
  def test_process_ips_with_bad_and_good
    results = process_ips('172.217.23.206,100.200.300.400,1.2.3.4')
    
    assert_equal 3, results.length
    assert_equal 'Good IP', results[0][:status]
    assert_equal 'Bad IP', results[1][:status]
    assert_equal 'Good IP', results[2][:status]
  end

  def test_process_ips_with_empty
    results = process_ips('172.217.23.206,,100.200.300.400')
    
    assert_equal 3, results.length
    assert_equal 'Unknown', results[1][:status]
  end

  # test: http endpoint with valid IPs
  def test_endpoint_with_valid_ips
    get '/?items=172.217.23.206,100.200.300.400'
    
    assert last_response.ok?
    
    data = JSON.parse(last_response.body, symbolize_names: true)
    assert_equal '', data[:error]
    assert_equal 2, data[:total_items]
    assert_equal 1, data[:bad_ip_count]
    assert_equal 1, data[:good_ip_count]
  end

  # test: http endpoint with no items
  def test_endpoint_with_no_items
    get '/'
    
    assert last_response.ok?
    
    data = JSON.parse(last_response.body, symbolize_names: true)
    refute_equal '', data[:error]
    assert_equal 0, data[:total_items]
  end

  # test: health endpoint
  def test_health_endpoint
    get '/health'
    
    assert last_response.ok?
    
    data = JSON.parse(last_response.body, symbolize_names: true)
    assert_equal 'healthy', data[:status]
    assert_equal 'ipchecker-badips', data[:service]
  end
end
