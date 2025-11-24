require 'sinatra'
require 'sinatra/base'
require 'json'

# list of bad IPv4 IPs (based on the guidance)
BAD_IPV4_IPS = [
  '100.200.300.400',
  '101.201.301.401',
  '102.202.302.402',
  '103.203.303.403'
].freeze

# list of bad IPv6 IPs (additional sample assign as malicious IPs)
BAD_IPV6_IPS = [
  '2001:db8:bad1::1',
  '2001:db8:bad2::1',
  'fe80::bad:cafe',
  '2a00:bad:bad:bad::1'
].freeze

# Helper: Check if IP is IPv4
def ipv4?(ip)
  return false if ip.nil? || ip.strip.empty?
  parts = ip.split('.')
  parts.length == 4
end

# helper: check if IP is IPv6
def ipv6?(ip)
  return false if ip.nil? || ip.strip.empty?
  # IPv6 has colons
  return false unless ip.include?(':')
  parts = ip.split(':')
  parts.length >= 3 && parts.length <= 8
end

# helper: check if IPv4 is bad
def bad_ipv4?(ip)
  BAD_IPV4_IPS.include?(ip)
end

# helper: check if IPv6 is bad
def bad_ipv6?(ip)
  BAD_IPV6_IPS.include?(ip)
end

# helper: process IPs
def process_ips(items_string)
  return [] if items_string.nil? || items_string.empty?
  
  items = items_string.split(',')
  results = []
  
  items.each do |item|
    item = item.strip
    
    if item.empty?
      # empty IP is BAD
      results << { ip: '', status: 'Bad IP', reason: 'empty IP address' }
    elsif ipv4?(item)
      # IPv4 check
      if bad_ipv4?(item)
        results << { ip: item, status: 'Bad IP', reason: 'known malicious IPv4' }
      else
        results << { ip: item, status: 'Good IP' }
      end
    elsif ipv6?(item)
      # IPv6 check
      if bad_ipv6?(item)
        results << { ip: item, status: 'Bad IP', reason: 'known malicious IPv6' }
      else
        results << { ip: item, status: 'Good IP' }
      end
    else
      # invalid format = BAD IP
      results << { ip: item, status: 'Bad IP', reason: 'invalid IP format' }
    end
  end
  
  results
end

# helper: count IPs
def count_ips(results)
  bad_count = results.count { |r| r[:status] == 'Bad IP' }
  good_count = results.count { |r| r[:status] == 'Good IP' }
  [bad_count, good_count]
end

# configure sinatra
set :port, ENV['PORT'] || 8081
set :bind, '0.0.0.0'

# enable CORS
before do
  headers 'Access-Control-Allow-Origin' => '*',
          'Access-Control-Allow-Methods' => ['GET', 'OPTIONS'],
          'Access-Control-Allow-Headers' => 'Content-Type'
end

# OPTIONS handler for CORS
options '*' do
  200
end

# main endpoint
get '/' do
  content_type :json
  
  items = params[:items]
  
  # validate input
  if items.nil? || items.empty?
    return {
      error: 'No items provided. Please provide IP addresses using ?items=ip1,ip2,ip3',
      items: '',
      total_items: 0,
      bad_ip_count: 0,
      good_ip_count: 0,
      results: []
    }.to_json
  end
  
  # process IPs
  results = process_ips(items)
  bad_count, good_count = count_ips(results)
  
  # return response
  {
    error: '',
    items: items,
    total_items: items.split(',').length,
    bad_ip_count: bad_count,
    good_ip_count: good_count,
    results: results
  }.to_json
end

# health check endpoint
get '/health' do
  content_type :json
  {
    status: 'healthy',
    service: 'ipchecker-badips',
    bad_ipv4_count: BAD_IPV4_IPS.length,
    bad_ipv6_count: BAD_IPV6_IPS.length
  }.to_json
end
