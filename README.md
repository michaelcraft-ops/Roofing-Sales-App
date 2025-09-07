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

<img width="1920" height="991" alt="Screenshot (310)" src="https://github.com/user-attachments/assets/f36460f2-1342-4310-8fd8-636d0f580e75" />
<img width="1920" height="996" alt="Screenshot (309)" src="https://github.com/user-attachments/assets/7d1b7386-e447-4443-9609-3ff8fb75bc34" />
<img width="1920" height="995" alt="Screenshot (308)" src="https://github.com/user-attachments/assets/4fb46156-f075-491f-9bca-fde0582c4070" />
<img width="1920" height="991" alt="Screenshot (307)" src="https://github.com/user-attachments/assets/7d8a53c9-5af4-453a-bfb7-a73d9228e949" />
<img width="1920" height="1003" alt="Screenshot (306)" src="https://github.com/user-attachments/assets/336c1c61-a794-4f4e-9914-44c0a6d36f77" />
<img width="1920" height="988" alt="Screenshot (305)" src="https://github.com/user-attachments/assets/55ba7b00-8af6-43bb-887d-47bcdc9118eb" />
<img width="1920" height="1003" alt="Screenshot (304)" src="https://github.com/user-attachments/assets/7a7dc9a4-a6c9-4790-8c7b-737259068d9b" />
<img width="1920" height="1011" alt="Screenshot (302)" src="https://github.com/user-attachments/assets/93f89c1e-a0a2-4ed8-bc29-50bf96c15de4" />
<img width="1920" height="996" alt="Screenshot (301)" src="https://github.com/user-attachments/assets/4513fbfd-477b-4888-a358-c5ef4d4c68fc" />
 

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
