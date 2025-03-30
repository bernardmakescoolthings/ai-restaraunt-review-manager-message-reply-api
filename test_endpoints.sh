#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL from environment variable or default to localhost
API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}

echo -e "${BLUE}Testing API endpoints with base URL: ${API_BASE_URL}${NC}\n"

# Test root endpoint
echo -e "${GREEN}Testing root endpoint (GET /)${NC}"
curl -s "${API_BASE_URL}/" | json_pp

#echo -e "\n${GREEN}Testing message response endpoint (POST /message/get_response)${NC}"
#curl -s -X POST "${API_BASE_URL}/message/get_response" \
#  -H "Content-Type: application/json" \
#  -d '{
#    "profile": "You are a friendly and professional restaurant manager",
#    "message_id": "ChdDSUhNMG9nS0VJQ0FnSURYeXRYQ3lBRRAB"
#  }' | json_pp

echo -e "\n${GREEN}Testing reviews fetch endpoint (POST /reviews/fetch)${NC}"
curl -s -X POST "${API_BASE_URL}/reviews/fetch" \
  -H "Content-Type: application/json" \
  -d '{
    "business_url": "https://www.google.com/maps/place/Simmer+%26+Steamer/@37.7936754,-122.4023789,17z/data=!3m1!4b1!4m6!3m5!1s0x808581d05100c267:0x2c87808f97097934!8m2!3d37.7936712!4d-122.399804!16s%2Fg%2F11wj5pksrn?entry=ttu&g_ep=EgoyMDI1MDMyNS4xIKXMDSoASAFQAw%3D%3"
  }' | json_pp 