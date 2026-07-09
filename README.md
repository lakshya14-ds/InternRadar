# 🚀 InternRadar – AI-Powered Internship Discovery Platform

<div align="center">

![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?logo=typescript)
![License](https://img.shields.io/badge/License-MIT-green)

### One Platform. Every Internship.

*A modern AI-powered internship aggregation platform that collects internships from multiple ATS platforms and company career pages into one searchable dashboard.*

</div>

---

# 📌 Overview

InternRadar is a full-stack internship discovery platform built to solve the problem of searching across dozens of career portals.

Instead of manually browsing multiple websites, students can discover internships from various ATS platforms, startups, and company career pages through a single modern interface.

The platform currently aggregates internships from:

- Greenhouse
- Lever
- Workday
- Ashby
- SmartRecruiters
- Manual Career Sources

with support for additional connectors planned.

---

# ✨ Features

## 🔍 Internship Search

- Search internships
- Filter by company
- Filter by category
- Filter by location
- Latest internships
- Category-based discovery

---

## 🤖 Automated Internship Aggregation

InternRadar automatically discovers internships from multiple sources using modular connectors.

Current connectors:

- ✅ Greenhouse
- ✅ Lever
- ✅ Workday
- ✅ Ashby
- ✅ SmartRecruiters
- ✅ Manual Sources

---

## 📊 Dashboard

View:

- Total internships
- Companies
- Categories
- Source distribution
- Latest opportunities
- Scraper status

---

## 👤 User Authentication

- JWT Authentication
- Login
- Registration
- User Profile
- Bookmarks
- Personalized dashboard

---

## ⭐ Bookmark System

Users can

- Save internships
- Remove bookmarks
- View saved internships

---

## 🔄 Background Scheduler

Uses APScheduler to

- Automatically scrape internships
- Update database
- Track scraping status
- Support manual refresh

---

## 📱 Responsive UI

Built with

- Next.js 15
- React
- Tailwind CSS
- Framer Motion

Supports

- Desktop
- Tablet
- Mobile

---

# 🏗️ Tech Stack

## Frontend

- Next.js 15
- React
- TypeScript
- Tailwind CSS
- Framer Motion
- TanStack Query
- NextAuth

---

## Backend

- FastAPI
- Python
- Motor
- MongoDB
- APScheduler
- JWT Authentication
- AsyncIO

---

## Database

MongoDB

Collections

- internships
- users
- companies

---

# 📂 Project Structure

```
InternRadar

├── internradar-frontend
│
│   ├── app
│   ├── components
│   ├── hooks
│   ├── lib
│   ├── store
│   └── types
│
└── internradar-backend
    │
    ├── app
    │   ├── connectors
    │   ├── routers
    │   ├── scheduler
    │   ├── services
    │   ├── search
    │   ├── models
    │   ├── notifications
    │   └── database
    │
    └── requirements.txt
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/InternRadar.git

cd InternRadar
```

---

# Backend Setup

```bash
cd internradar-backend
```

Create virtual environment

```bash
python -m venv .venv
```

Activate

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create `.env`

```env
MONGODB_URI=YOUR_MONGODB_URI

DATABASE_NAME=internradar

JWT_SECRET=your_secret

SCRAPER_INTERVAL_MINUTES=30
```

Run

```bash
python -m uvicorn app.main:app --reload
```

Backend

```
http://localhost:8000
```

---

# Frontend Setup

```bash
cd internradar-frontend
```

Install

```bash
npm install
```

Create

```
.env.local
```

```env
NEXTAUTH_URL=http://localhost:5000

NEXTAUTH_SECRET=your_secret

NEXT_PUBLIC_API=http://localhost:8000
```

Run

```bash
npm run dev
```

Frontend

```
http://localhost:5000
```

---

# API Endpoints

## Authentication

```
POST /api/auth/register

POST /api/auth/login
```

---

## Internships

```
GET /internships

GET /internships/latest

GET /internships/search

GET /internships/{id}
```

---

## Scraper

```
GET /api/scraper/status

POST /api/scraper/trigger
```

---

## Statistics

```
GET /api/stats
```

---

# Current Architecture

```
Career Sites

        │

        ▼

 ATS Connectors

        │

        ▼

 Internship Normalizer

        │

        ▼

 Duplicate Detection

        │

        ▼

 MongoDB

        │

        ▼

 FastAPI APIs

        │

        ▼

 Next.js Frontend
```

---

# Current Progress

## Completed

- Full Stack Architecture
- Internship Database
- Authentication
- Bookmarks
- Dashboard
- Search
- Filters
- Background Scheduler
- Multi-Connector Support
- Statistics API
- Responsive UI

---

## In Progress

- Feed Diversification
- Company Logos
- Startup Discovery
- Company Profiles
- Better Ranking Engine
- Faster Connectors
- Recommendation Engine

---

## Planned

- Wellfound Connector
- YC Jobs Connector
- Simplify Connector
- Handshake Connector
- RippleMatch Connector
- AI Resume Matching
- Internship Recommendation Engine
- Email Notifications
- Company Analytics
- Resume Scoring
- AI Career Assistant

---

# Screenshots

> Add screenshots of:

- Homepage
- Dashboard
- Internship Search
- Internship Details
- Login
- Analytics

---

# Future Roadmap

- AI-powered internship recommendations
- Resume-job matching
- Semantic search
- Company intelligence
- Internship quality scoring
- Salary insights
- Student profile personalization
- Email alerts
- WhatsApp notifications
- Browser extension

# 🚀 Production Deployment Guide

This project is a monorepo containing a Next.js frontend and a FastAPI backend. This section details how to deploy the backend on Railway and the frontend on Vercel.

---

## 🛠️ Railway Backend Deployment

The backend application is configured to build using **Nixpacks** and start using `uvicorn`.

### 1. Project Configuration
* **Root Directory**: Set the Service Root Directory to `internradar-backend` in the Railway dashboard settings. This ensures Railway compiles and runs the backend directory instead of the monorepo root.
* **Build Configuration**: Configured automatically via `railway.json` and `Procfile`.
* **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* **Restart Policy**: Enabled to automatically restart on failure (`ON_FAILURE`).

### 2. Environment Variables
Add the following variables in the Railway Service dashboard:

| Variable | Description | Example / Recommended Value |
| :--- | :--- | :--- |
| `MONGO_URI` | MongoDB Connection String | `mongodb+srv://...` |
| `DB_NAME` | Database Name | `internradar` |
| `JWT_SECRET` | Secret key for JWT hashing | Any secure string |
| `SCRAPER_INTERVAL_MINUTES` | Frequency of recruiter scans | `30` |
| `PORT` | Listening port (injected by Railway) | `$PORT` (Do not set manually) |

### 3. Common Errors
* **`503 Service Unavailable`**: Usually indicates that the backend is unable to connect to MongoDB. Check that your `MONGO_URI` is correct and that MongoDB Atlas allows connections from all IPs (`0.0.0.0/0`) since Railway uses dynamic outbound IPs.
* **`ModuleNotFoundError`**: Ensure `requirements.txt` contains all core libraries (`fastapi`, `uvicorn`, `motor`, etc.).

---

## 📐 Vercel Frontend Deployment

The frontend application is a modern Next.js 15 site deployed on Vercel.

### 1. Project Configuration
* **Framework Preset**: Set explicitly to **`Next.js`** in Vercel settings.
* **Root Directory**: Set to `internradar-frontend`.
* **Build Command**: `next build`
* **Output Directory**: `.next`

### 2. Environment Variables
Add the following variables in the Vercel Dashboard:

| Variable | Description | Example / Recommended Value |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Live URL of the Railway backend | `https://internradar-backend.up.railway.app` |
| `NEXTAUTH_URL` | Live URL of your Vercel deployment | `https://intern-radar-tau.vercel.app` |
| `NEXTAUTH_SECRET` | Secret key for session cryptography | Any secure string |
| `GOOGLE_CLIENT_ID` | OAuth Google Client ID | `<id>.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | OAuth Google Client Secret | `<secret>` |

### 3. Custom Domains
* To configure your custom domain, navigate to **Settings > Domains** in your Vercel dashboard and add your domain. Ensure your DNS provider points `A` or `CNAME` records to Vercel's servers.

---

# Contributing

Contributions are welcome!

1. Fork the repository

2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit changes

```bash
git commit -m "Added new feature"
```

4. Push

```bash
git push origin feature-name
```

5. Open Pull Request

---

# Author

## Lakshya Arora

B.Tech CSE (Data Science)

Manipal Institute of Technology Bengaluru

GitHub:

https://github.com/lakshya14-ds

LinkedIn:
https://www.linkedin.com/in/lakshya-arora-8520ba341/

---

# License

This project is licensed under the MIT License.

---

⭐ If you found this project useful, consider giving it a star!
