# TalentLens — Job Applicant Shortlisting System

## 🚀 Overview

TalentLens is a full-stack web application designed to streamline the process of **job applicant shortlisting** using efficient algorithms.

It allows recruiters to:

* Add and manage candidates
* Sort applicants using **Quick Sort**
* Search candidates using **Binary Search**
* Filter candidates using **Recursion**
* Shortlist top candidates intelligently

---

## 🧠 Core Algorithms Used

| Algorithm     | Purpose                                         |
| ------------- | ----------------------------------------------- |
| Quick Sort    | Sorting candidates by score, experience, salary |
| Binary Search | Fast search on numeric fields                   |
| Recursion     | Skill filtering & ranking                       |
| Greedy Logic  | Shortlisting top candidates                     |

---

## 🛠 Tech Stack

### Backend

* Python (Flask)
* SQLite Database

### Frontend

* HTML, CSS (Bootstrap)
* JavaScript (Vanilla)
* Chart.js (for analytics)

---

## 📁 Project Structure

```
TalentLens/
│
├── app.py               # Flask backend
├── algorithms.py       # Core algorithms
├── models.py           # Database operations
├── database.db         # SQLite database
├── requirements.txt    # Dependencies
│
├── templates/
│   └── index.html      # Main UI
│
├── static/
│   ├── css/style.css   # Styling
│   └── js/app.js       # Frontend logic
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd TalentLens
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

### 4. Open in browser

```
http://127.0.0.1:5000/
```

---

## ✨ Features

### 📊 Dashboard

* Real-time stats
* Charts (Top candidates, Experience distribution)

### 👤 Candidate Management

* Add / Edit / Delete candidates
* Auto score calculation

### ⚡ Sorting (Quick Sort)

* Sort by score, experience, salary
* O(n log n) average complexity

### 🔍 Search System

* Binary Search (numeric fields)
* Recursive Skill Filtering
* Name-based search

### 🏆 Shortlisting

* Top N candidates selection
* Skill-based filtering

---

## 🧮 Scoring Formula

```
score = (experience × 2) + (skills × 3) − (salary / 10000)
```

---

## 📈 Algorithm Complexity

| Algorithm     | Complexity     |
| ------------- | -------------- |
| Quick Sort    | O(n log n) avg |
| Binary Search | O(log n)       |
| Recursion     | O(n × m)       |
| Greedy        | O(n log n)     |

---

## 🎯 Use Case

* HR systems
* Campus recruitment tools
* Resume filtering systems

---

## 📌 Future Improvements

* Authentication system
* Resume parsing (NLP)
* Machine learning scoring
* Cloud deployment

---

## 👨‍💻 Author

Hardik Aggarwal

---

## ⭐ Conclusion

TalentLens demonstrates how classical algorithms can be applied to solve real-world hiring problems efficiently.
