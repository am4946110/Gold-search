# Gold Search 🪙

A powerful Python-based search engine application that fetches Google search results using the Serper API and stores them locally in an SQLite database for fast searching and history tracking.

---

## ✨ Features

* 🔍 Search Google directly from terminal
* 💾 Save search results into SQLite database
* 📚 Search previously stored results
* 🕘 Search history tracking
* 📊 Database statistics
* 📄 Table-formatted output
* ⚡ Fast local searching
* 🧩 JSON API output support

---

## 🛠 Built With

* Python 3
* SQLite3
* Google Serper API
* JSON
* HTTP Client

---

## 📂 Project Structure

```bash id="0g5u8n"
Gold-search/
│
├── pyGetDate.py          # Main application
├── search_results.db     # SQLite database
├── Get_News.bat          # Windows batch runner
├── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

* Python 3 installed
* Internet connection
* Serper API key

Check Python version:

```bash id="v8vmy0"
python --version
```

---

## ⚙️ Installation

Clone the repository:

```bash id="6tyjlwm"
git clone https://github.com/am4946110/Gold-search.git
```

Move into the project directory:

```bash id="z9fzwo"
cd Gold-search
```

Install dependencies (if needed):

```bash id="w4h1tm"
pip install requests
```

---

## 🔑 API Configuration

The project uses the Google Serper API.

Inside `pyGetDate.py`:

```python id="bh4bx0"
headers = {
    "X-API-KEY": "YOUR_API_KEY",
    "Content-Type": "application/json"
}
```

Replace:

```text id="h4c6vb"
YOUR_API_KEY
```

with your actual Serper API key.

Get your API key from:

### [Serper API Official Website](https://serper.dev?utm_source=chatgpt.com)

---

## ▶️ Usage

### Run Interactive Menu

```bash id="3kqv7w"
python pyGetDate.py
```

---

### Search Directly From Command Line

```bash id="15qz0g"
python pyGetDate.py "gold price today"
```

Example JSON response:

```json id="v4x8q4"
{
  "ok": true,
  "status": 200,
  "query": "gold price today",
  "results": []
}
```

---

## 📋 Menu Options

When running interactively, the application provides:

```text id="jlwm1y"
1. Search Google
2. Search Database by Title
3. Search Database by Snippet
4. Search Database (Title + Snippet)
5. View Search History
6. View Database Statistics
7. Exit
```

---

## 🗄 Database Structure

### searches Table

| Column       | Type      |
| ------------ | --------- |
| id           | INTEGER   |
| query        | TEXT      |
| search_date  | TIMESTAMP |
| result_count | INTEGER   |

---

### results Table

| Column    | Type    |
| --------- | ------- |
| id        | INTEGER |
| search_id | INTEGER |
| title     | TEXT    |
| link      | TEXT    |
| snippet   | TEXT    |
| rank      | INTEGER |

---

## 📊 Example Output

```text id="5nd0fu"
--------------------------------------------
# | Title | Link | Snippet
--------------------------------------------
1 | Gold Prices Today | example.com | Live gold prices...
--------------------------------------------
```

---

## 🔎 Search Features

You can search stored results by:

* Title
* Snippet
* Both title and snippet

This makes the application work like a mini offline search engine.

---

## 📈 Future Improvements

* 🌐 GUI interface
* 📱 Web version
* 🔔 Notifications
* 📊 Search analytics
* 🌙 Dark mode
* 🌍 Multi-language support

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create your feature branch

```bash id="v1l9x4"
git checkout -b feature/new-feature
```

3. Commit your changes

```bash id="3e0tgi"
git commit -m "Add new feature"
```

4. Push to GitHub

```bash id="l83g77"
git push origin feature/new-feature
```

5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

### [Amr Maher GitHub Profile](https://github.com/am4946110?utm_source=chatgpt.com)

---

## 🌟 Repository

### [Gold Search Repository](https://github.com/am4946110/Gold-search?utm_source=chatgpt.com)

---

## ⭐ Support

If you like this project:

* Give it a ⭐ on GitHub
* Share it with friends
* Contribute to improve it

---
