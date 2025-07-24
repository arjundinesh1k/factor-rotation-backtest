# Factor Rotation Backtest Engine

This project implements a web-based Factor Rotation Backtest Engine using Flask for the backend and Highcharts for interactive data visualization on the frontend. It allows users to simulate a multi-factor investment strategy against the S&P 500 benchmark, providing key performance metrics and cumulative return charts.

---

## Features

- **Simulated Backtesting:** Runs a simulated factor rotation strategy over a 10-year period.
- **Key Performance Metrics:** Displays cumulative return, annualized Sharpe ratio, excess return vs. S&P 500, and maximum drawdown.
- **Interactive Charts:** Visualizes cumulative performance of the Factor Strategy and S&P 500 using Highcharts, with period filtering (1Y, 2Y, 3Y, 5Y, 7Y, 10Y).
- **Drawdown Analysis:** Provides a dedicated chart for strategy drawdown.
- **Factor Contribution Breakdown:** Illustrates the contribution of different factors (Momentum, Value, Quality) to the strategy's performance.
- **Quantitative Factor Analysis:** Displays dummy data for individual stock factor scores (Momentum, Quality, Growth).
- **Responsive Design:** Optimized for various screen sizes.
- **Multi-language Support:** (Placeholder for future implementation, currently English-only with translation infrastructure).

---

## Technologies Used

### Backend

- **Python 3**
- **Flask:** Web framework
- **Pandas:** Data manipulation and analysis
- **NumPy:** Numerical operations
- **SciPy:** Statistical functions (for linear regression in metrics calculation)
- **Gunicorn:** WSGI HTTP Server for production deployment

### Frontend

- **HTML5**
- **CSS3** (with custom CSS variables for theming)
- **JavaScript**
- **Highcharts:** Interactive charting library

---

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```sh
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Create a Virtual Environment

```sh
python -m venv venv
```

### 3. Activate the Virtual Environment

**macOS/Linux:**
```sh
source venv/bin/activate
```

**Windows (Command Prompt):**
```sh
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```sh
venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```sh
pip install -r requirements.txt
```

**requirements.txt:**
```
flask
pandas
numpy
gunicorn
scipy
```

### 5. Run the Application

**a) Development Server (Flask's built-in server):**
```sh
flask run
```
The application will typically be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

**b) Production Server (Gunicorn):**
```sh
gunicorn app:app
```
This will start the Gunicorn server, usually on [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### 6. Access the Application

Open your web browser and navigate to the address provided by the server.

---

## Project Structure

```
.
├── app.py                  # Main Flask application file
├── utils.py                # Contains the backtesting simulation logic
├── requirements.txt        # Python dependencies
├── Procfile                # For deployment to platforms like Heroku (specifies web process)
├── .gitignore              # Specifies files/directories to be ignored by Git
├── static/
│   └── styles.css          # Custom CSS for styling (if not using CDN for all styles)
└── templates/
    └── index.html          # Main HTML template for the dashboard
```

---

## Customization

- **Backend Logic (`utils.py`):** Modify `run_factor_rotation_backtest()` to change the simulation parameters, add more complex strategy logic, or integrate with real market data APIs.
- **Frontend Styling (`static/styles.css` / `templates/index.html`):** Adjust CSS variables or Tailwind classes to change the visual theme, layout, or component styles.
- **Metrics Calculation (`app.py`):** Refine the metric calculation logic in the `index()` function to include more sophisticated financial metrics or adjust existing ones.
- **Highcharts Configuration (`templates/index.html`):** Customize chart types, series, tooltips, and other Highcharts options directly in the JavaScript section of `index.html`.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.