package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"strings"
)

// response structure
type Response struct {
	Error          string          `json:"error"`
	Items          string          `json:"items"`
	TotalItems     int             `json:"total_items"`
	CountryResults []CountryResult `json:"country_results"`
}

type CountryResult struct {
	IP      string `json:"ip"`
	Country string `json:"country"`
	Reason  string `json:"reason,omitempty"`
}

func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	w.Header().Set("Content-Type", "application/json")
}

// check if IP is IPv4
func isIPv4(ip string) bool {
	if ip == "" || strings.TrimSpace(ip) == "" {
		return false
	}

	parts := strings.Split(ip, ".")
	return len(parts) == 4
}

// check if IP is IPv6
func isIPv6(ip string) bool {
	if ip == "" || strings.TrimSpace(ip) == "" {
		return false
	}

	if strings.Contains(ip, ":") {
		parts := strings.Split(ip, ":")
		return len(parts) >= 3 && len(parts) <= 8
	}

	return false
}

// get country from IPv4 address based on first octet
func getCountryFromIPv4(ip string) (string, string) {
	// empty IP
	if ip == "" || strings.TrimSpace(ip) == "" {
		return "Unknown", "empty IP"
	}

	// check if IPv4
	if !isIPv4(ip) {
		return "Unknown", "not IPv4"
	}

	// get first octet
	parts := strings.Split(ip, ".")
	if len(parts) < 1 {
		return "Unknown", "invalid format"
	}

	// parse first octet
	firstOctet, err := strconv.Atoi(parts[0])
	if err != nil {
		return "Unknown", "invalid first octet"
	}

	// enhanced country mapping based on first octet
	switch firstOctet {
	// based on the sample mappings
	case 100:
		return "US", ""
	case 101:
		return "UK", ""
	case 102:
		return "China", ""

	// additional country mappings
	case 103:
		return "Germany", ""
	case 104:
		return "France", ""
	case 105:
		return "Japan", ""
	case 106:
		return "Canada", ""
	case 107:
		return "Australia", ""
	case 108:
		return "Brazil", ""
	case 109:
		return "India", ""
	case 110:
		return "Russia", ""
	case 111:
		return "South Korea", ""
	case 112:
		return "Italy", ""
	case 113:
		return "Spain", ""
	case 114:
		return "Netherlands", ""
	case 115:
		return "Sweden", ""

	// ranges for common IPs
	case 1, 2, 3, 4, 5, 6, 7, 8, 9:
		return "US", ""
	case 172:
		return "Private Network", "RFC1918 private range"
	case 192:
		return "Private Network", "RFC1918 private range"
	case 10:
		return "Private Network", "RFC1918 private range"
	case 127:
		return "Localhost", "loopback address"

	default:
		return "Unknown", "no country mapping"
	}
}

// get country from IPv6 address based on prefix
func getCountryFromIPv6(ip string) (string, string) {
	// empty IP
	if ip == "" || strings.TrimSpace(ip) == "" {
		return "Unknown", "empty IP"
	}

	// check if IPv6
	if !isIPv6(ip) {
		return "Unknown", "not IPv6"
	}

	// get first part (before first colon)
	parts := strings.Split(ip, ":")
	if len(parts) < 1 {
		return "Unknown", "invalid format"
	}

	firstPart := strings.ToLower(parts[0])

	// IPv6 country mapping based on prefix
	// add the sample mappings for IPv6
	switch {
	case strings.HasPrefix(firstPart, "2001"):
		return "Global Unicast", "production IPv6"
	case strings.HasPrefix(firstPart, "2a00"):
		return "Europe", "European IPv6 range"
	case strings.HasPrefix(firstPart, "2a01"):
		return "UK", "UK IPv6 range"
	case strings.HasPrefix(firstPart, "2a02"):
		return "Germany", "German IPv6 range"
	case strings.HasPrefix(firstPart, "2a03"):
		return "France", "French IPv6 range"
	case strings.HasPrefix(firstPart, "2400"):
		return "Asia Pacific", "APNIC IPv6 range"
	case strings.HasPrefix(firstPart, "2600"):
		return "US", "North American IPv6 range"
	case strings.HasPrefix(firstPart, "2800"):
		return "Latin America", "LACNIC IPv6 range"
	case strings.HasPrefix(firstPart, "fe80"):
		return "Link Local", "link-local address"
	case strings.HasPrefix(firstPart, "fc00"), strings.HasPrefix(firstPart, "fd00"):
		return "Private Network", "unique local address"
	case firstPart == "" || firstPart == "::1":
		return "Localhost", "loopback address"
	default:
		return "Country Unavailable", "IPv6 prefix not mapped"
	}
}

// process IP addresses from comma-separated string
func processIPs(itemsString string) []CountryResult {
	if itemsString == "" {
		return []CountryResult{}
	}

	items := strings.Split(itemsString, ",")
	results := make([]CountryResult, 0, len(items))

	for _, item := range items {
		item = strings.TrimSpace(item)

		var country, reason string

		if item == "" {
			// empty IP
			country = "Unknown"
			reason = "empty"
		} else if isIPv4(item) {
			// IPv4
			country, reason = getCountryFromIPv4(item)
		} else if isIPv6(item) {
			// IPv6
			country, reason = getCountryFromIPv6(item)
		} else {
			// neither IPv4 nor IPv6
			country = "unknown"
			reason = "invalid format"
		}

		result := CountryResult{
			IP:      item,
			Country: country,
		}

		if reason != "" {
			result.Reason = reason
		}

		results = append(results, result)
	}

	return results
}

// main handler
func countryHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	// handle options for the CORS
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	// get query parameter
	items := r.URL.Query().Get("items")

	// validate input
	if items == "" {
		response := Response{
			Error:          "No items provided. Please provide IP addresses using ?items=ip1,ip2,ip3",
			Items:          "",
			TotalItems:     0,
			CountryResults: []CountryResult{},
		}
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(response)
		return
	}

	// process IPs
	results := processIPs(items)

	response := Response{
		Error:          "",
		Items:          items,
		TotalItems:     len(strings.Split(items, ",")),
		CountryResults: results,
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

// health check handler
func healthHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	response := map[string]string{
		"status":  "healthy",
		"service": "ipchecker-country",
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	// register handlers
	http.HandleFunc("/", countryHandler)
	http.HandleFunc("/health", healthHandler)

	// start server
	port := ":8080"
	log.Printf("IPChecker Country service starting on port %s\n", port)

	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatal(err)
	}
}
