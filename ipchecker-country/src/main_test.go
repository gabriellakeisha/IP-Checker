package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

// test isIPv4 function
func TestIsIPv4(t *testing.T) {
	tests := []struct {
		ip       string
		expected bool
	}{
		{"100.217.23.206", true},
		{"101.217.23.206", true},
		{"102.217.23.206", true},
		{"172.217.23.206.100", false},
		{"172.217.23", false},
		{"", false},
		{"   ", false},
	}
	
	for _, test := range tests {
		result := isIPv4(test.ip)
		if result != test.expected {
			t.Errorf("isIPv4(%s) = %v; expected %v", test.ip, result, test.expected)
		}
	}
}

// test getCountry function
func TestGetCountry(t *testing.T) {
	tests := []struct {
		ip              string
		expectedCountry string
	}{
		{"100.217.23.206", "US"},
		{"101.217.23.206", "UK"},
		{"102.217.23.206", "China"},
		{"172.217.23.206", "Unknown"},
		{"", "Unknown"},
	}
	
	for _, test := range tests {
		country, _ := getCountry(test.ip)
		if country != test.expectedCountry {
			t.Errorf("getCountry(%s) = %s; expected %s", test.ip, country, test.expectedCountry)
		}
	}
}

// test processIPs function
func TestProcessIPs(t *testing.T) {
	items := "100.217.23.206,101.217.23.206,102.217.23.206"
	results := processIPs(items)
	
	if len(results) != 3 {
		t.Errorf("processIPs returned %d results; expected 3", len(results))
	}
	
	expectedCountries := []string{"US", "UK", "China"}
	for i, result := range results {
		if result.Country != expectedCountries[i] {
			t.Errorf("Result %d: got %s; expected %s", i, result.Country, expectedCountries[i])
		}
	}
}

// test valid IPs
func TestCountryHandlerValidIPs(t *testing.T) {
	req, err := http.NewRequest("GET", "/?items=100.217.23.206,101.217.23.206", nil)
	if err != nil {
		t.Fatal(err)
	}
	
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(countryHandler)
	handler.ServeHTTP(rr, req)
	
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}
	
	var response Response
	err = json.NewDecoder(rr.Body).Decode(&response)
	if err != nil {
		t.Fatal(err)
	}
	
	if response.Error != "" {
		t.Errorf("Expected no error, got: %s", response.Error)
	}
	
	if len(response.CountryResults) != 2 {
		t.Errorf("Expected 2 results, got %d", len(response.CountryResults))
	}
}

// test HTTP endpoint with no items
func TestCountryHandlerNoItems(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}
	
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(countryHandler)
	handler.ServeHTTP(rr, req)
	
	if status := rr.Code; status != http.StatusBadRequest {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusBadRequest)
	}
	
	var response Response
	err = json.NewDecoder(rr.Body).Decode(&response)
	if err != nil {
		t.Fatal(err)
	}
	
	if response.Error == "" {
		t.Error("Expected error message, got empty string")
	}
}

// test empty IPs
func TestCountryHandlerEmptyIPs(t *testing.T) {
	req, err := http.NewRequest("GET", "/?items=100.217.23.206,,102.217.23.206", nil)
	if err != nil {
		t.Fatal(err)
	}
	
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(countryHandler)
	handler.ServeHTTP(rr, req)
	
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}
	
	var response Response
	err = json.NewDecoder(rr.Body).Decode(&response)
	if err != nil {
		t.Fatal(err)
	}
	
	if response.TotalItems != 3 {
		t.Errorf("Expected 3 total items, got %d", response.TotalItems)
	}
	
	if response.CountryResults[1].Country != "Unknown" {
		t.Error("Expected middle item to be Unknown")
	}
}

// test health endpoint
func TestHealthHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/health", nil)
	if err != nil {
		t.Fatal(err)
	}
	
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(healthHandler)
	handler.ServeHTTP(rr, req)
	
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}
	
	var response map[string]string
	err = json.NewDecoder(rr.Body).Decode(&response)
	if err != nil {
		t.Fatal(err)
	}
	
	if response["status"] != "healthy" {
		t.Errorf("Expected status 'healthy', got '%s'", response["status"])
	}
}