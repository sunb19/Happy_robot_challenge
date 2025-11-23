# HappyRobot Inbound Carrier Sales Challenge

A full inbound carrier sales automation system integrating HappyRobot Inbound Voice Agents with a FastAPI backend deployed on Fly.io.
This project implements automated MC verification, load search, negotiation (3 rounds), call classification, sentiment detection, and dashboard analytics.

Production base URL: https://happy-robot-challenge.fly.dev
Docs: https://happy-robot-challenge.fly.dev/docs


#🚀 Features

#🔐 Carrier Authentication
	•	Extract MC number from caller
	•	Validate via backend API (/auth-carrier)
	•	Simple FMCSA mock:
	•	Non-numeric → ineligible
	•	Starts with "9" → ineligible
	•	Others → eligible

#📦 Load Search
	•	AI extracts load preferences
	•	POST /loads/search returns matching JSON loads
	•	Carrier hears lane, miles, rate, pickup time

#💵 3-Round Automated Negotiation

POST /negotiate
	•	Round-based logic:
	•	Offer >= 95% → accept
	•	Offer <= 85% with round >= 3 → reject
	•	Otherwise → counter
	•	Designed for realistic freight brokerage negotiation rules

#📞 Call Logging

POST /call-log
	•	Outcome
	•	Sentiment
	•	Rate agreed
	•	Summary

#📊 Dashboard

GET /dashboard
	•	Total calls
	•	Accept / reject %
	•	Sentiment breakdown
	•	Average agreed rate
	•	Eligible / ineligible counts

#🧠 HappyRobot Workflow Overview

Your Inbound Voice Agent follows this flow:
	1.	Extract MC → POST /auth-carrier
	2.	IF eligible → extract load info → POST /loads/search
	3.	Pitch load → extract offer → POST /negotiate (round 1)
	4.	Continue negotiation up to 3 rounds
	5.	If accepted → transfer to live rep
	6.	Extract outcome + sentiment → POST /call-log

All done using:
	•	AI Extract blocks
	•	Webhook (Call HTTP API) blocks
	•	Condition routing

#🏗 Tech Stack
	•	FastAPI
	•	Python 3.13
	•	Uvicorn
	•	Fly.io
	•	Docker
	•	HappyRobot AI Platform
	•	JSON load data store

#📁 Project Structure
.
├── app/
│   ├── main.py
│   ├── config.py
│   ├── load_store.py
│   ├── call_store.py
│   ├── schemas.py
│   └── loads.json
├── Dockerfile
├── fly.toml
├── requirements.txt
└── README.md
