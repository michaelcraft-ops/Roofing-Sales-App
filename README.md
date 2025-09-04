# Roofing Sales App

A full-stack web application for roofing salespeople to manage their sales funnel and forecast goals.

**Live Application:** [https://roofing-sales-app-mcraft.onrender.com/](https://roofing-sales-app-mcraft.onrender.com/)

---

## 🎯 Purpose & Problem

This application was built to solve a common problem for commission-based salespeople: a lack of clarity on the daily activities required to meet a specific income goal. This tool provides a complete sales funnel tracker (Leads -> Deals) and a unique "Projector" feature that calculates the daily work needed based on the user's personal sales metrics and income targets.

---

## ✨ Features

* **Secure User Authentication:** Users can register, log in, and log out to access their private sales data.
* **Sales Funnel Management:** A complete CRUD (Create, Read, Update, Delete) interface for managing leads and deals.
* **Data-Driven Projector:** A unique tool that forecasts the daily "doors knocked" and "appointments set" required to reach a user-defined income goal.
* **Production-Ready Database:** Deployed with a robust PostgreSQL database, migrated from an initial SQLite implementation.
* **Cloud Deployment:** Fully deployed on Render with a continuous integration/continuous deployment (CI/CD) pipeline connected to this GitHub repository.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Gunicorn
* **Frontend:** HTML, CSS, Bootstrap
* **Database:** PostgreSQL (Production), SQLite (Development)
* **Deployment:** Render, Git

---

## 📸 Screenshots

*(We will add screenshots here in the next step!)*

---

## 🚀 How to Run Locally

To run this project on your local machine:

1.  Clone the repository:
    `git clone https://github.com/michaelcraft-ops/Roofing-Sales-App.git`
2.  Navigate to the project directory:
    `cd Roofing-Sales-App`
3.  Create and activate a virtual environment:
    `python -m venv .venv`
    `source .venv/bin/activate`  # On Windows, use `.venv\Scripts\activate`
4.  Install the dependencies:
    `pip install -r requirements.txt`
5.  Initialize the database:
    `flask db upgrade`
6.  Run the application:
    `flask run`

---
