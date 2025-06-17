# 📜 Matrusri Daily Standup Reports

A lightweight Streamlit web app for developer interns at **Matrusri** to submit and track their daily standup reports. Designed to be simple, efficient, and admin-manageable with no external database.

---

## 🚀 Features

* 🧑‍💻 Submit daily reports with GitLab username
* 📊 View all submitted reports in a searchable, sortable interface
* 🔐 Admin-only panel to:

  * 📅 Download all reports as CSV
  * 🗑️ Clear all report history with one click
* 📁 Stores data locally in a CSV file (no database required)
* 💡 Built using [Streamlit](https://streamlit.io)

---

## 📂 Project Structure

```
standup-app/
│
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
└── .streamlit/
    └── secrets.toml        # Admin credentials (secure)
```

---

## 🔧 Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/siddhardha-mns/Standup-Report.git
cd Standup-Report
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Create admin secrets**

Create a `.streamlit/secrets.toml` file:

```toml
# .streamlit/secrets.toml
admin_password = "your_secure_admin_password"
```

4. **Run the app**

```bash
streamlit run app.py
```

---

## 🔐 Admin Panel

Accessible via the **Admin Password** (stored in `secrets.toml` or set via Streamlit Cloud Secrets):

* 📅 Download all reports as a `.csv` file
* 🗑️ Clear all reports from the system after archiving

---

## 📦 Deployment

To deploy on [Streamlit Cloud](https://streamlit.io/cloud):

1. Push this repo to GitHub or GitLab
2. Sign in to Streamlit Cloud and create a new app from your repo
3. Go to **App → Settings → Secrets** and add:

```toml
admin_password = "your_secure_admin_password"
```

---

## 💠 Tech Stack

* [Python](https://www.python.org/)
* [Streamlit](https://streamlit.io)
* [Pandas](https://pandas.pydata.org/)

---

## 📄 License

This project is licensed under the **Matrusri Academic Team (MAT) License**. Redistribution or modification is permitted **only** within Matrusri-affiliated projects or by authorized contributors. For more details, refer to the `LICENSE` file in this repository.

---

## 💬 Feedback

For bugs, feature requests, or improvements, open an issue or contact the project maintainers via the [GitHub repo](https://github.com/siddhardha-mns/Standup-Report).

---
