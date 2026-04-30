# Solana-Based Logistic Management System

A comprehensive blockchain-powered logistics management platform built with FastAPI, featuring real-time delivery tracking, automated reporting, and machine learning predictions for delivery optimization.

Features

- Blockchain Integration: Secure transactions and tracking using Solana blockchain
- Real-Time GPS Tracking: Live delivery monitoring with interactive maps
- Automated Reporting: Generate Excel reports with sales and delivery analytics
- Machine Learning: Predict delivery times using Random Forest regression
- Web Dashboard: Modern UI built with FastAPI and shadcn/ui components
- Authentication System: Secure user management with JWT tokens
- WebSocket Support: Real-time updates for delivery status
- Data Visualization: Interactive charts and analytics

Tech Stack

Backend
- FastAPI: High-performance web framework
- Python 3.8+: Core programming language
- SQLAlchemy: Database ORM
- Alembic: Database migrations
- Solana-py: Blockchain integration
- Pandas: Data processing and analysis
- Scikit-learn: Machine learning models

Frontend
- Jinja2: Template engine
- Tailwind CSS: Utility-first CSS framework
- shadcn/ui: Modern UI components
- Leaflet.js: Interactive maps
- WebSockets: Real-time communication

Database
- SQLite: Development database (easily configurable for PostgreSQL/MySQL)

Prerequisites

- Python 3.8 or higher
- Node.js 16+ (for Tailwind CSS build)
- Git

Installation

1. Clone the Repository
bash
git clone <repository-url>
cd "Solana Based Logistic Management System"


2. Set Up Python Environment
bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt


### 3. Set Up Node.js Dependencies (Optional)
bash
# Install Node.js dependencies for Tailwind CSS
npm install

# Build CSS (if using custom Tailwind build)
npm run build-css

4. Environment Configuration
Create a `.env` file in the root directory:
env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./logistics.db
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your-private-key


Running the Application

Development Modebash
# Run the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


Production Mode
bash
# Using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or using gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000


Visit `http://localhost:8000` in your browser.

Data Processing

Preprocessing Supermarket Data
bash
python preprocess_data.py

This script processes the raw supermarket sales data and prepares it for analysis.

Training Delivery Prediction Model
Open `delivery_tracking_model.ipynb` in Jupyter Notebook and run all cells to train the machine learning model for delivery time prediction

Database Setup

### Initialize Database
bash
# Create database tables
python -c "from app.database import create_tables; create_tables()"

# Or run migrations
alembic upgrade head

API Endpoints

Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

Logistics
- `GET /` - Homepage
- `POST /select_service` - Select service type
- `GET /tracking` - Real-time delivery tracking
- `GET /reports` - Generate reports

### Blockchain
- `POST /blockchain/transaction` - Create blockchain transaction
- `GET /blockchain/verify/{tx_id}` - Verify transaction

### Real-time
- `WebSocket /ws/tracking/{delivery_id}` - Real-time tracking updates

Dependencies

### Python Packages (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
solana==0.32.0
websockets==12.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-decouple==3.8
pandas==2.1.4
openpyxl==3.1.2
matplotlib==3.8.2
scikit-learn==1.3.0
seaborn==0.12.2
requests==2.31.0
```

### Node.js Packages (package.json)
json
{
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "@tailwindcss/forms": "^0.5.7",
    "@tailwindcss/typography": "^0.5.10"
  }
}


Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── dependencies.py         # Dependency injection
│   ├── auth/                   # Authentication module
│   │   ├── auth_models.py
│   │   ├── auth_routes.py
│   │   └── auth_service.py
│   ├── blockchain/             # Solana blockchain integration
│   │   ├── solana_client.py
│   │   ├── solana_transactions.py
│   │   └── solana_verifier.py
│   ├── logistics/              # Logistics management
│   │   ├── delivery_service.py
│   │   ├── gps_tracker.py
│   │   ├── logistics_models.py
│   │   └── logistics_routes.py
│   ├── realtime/               # WebSocket handlers
│   │   ├── realtime_routes.py
│   │   └── websocket_manager.py
│   ├── reports/                # Report generation
│   │   ├── report_generator.py
│   │   ├── report_models.py
│   │   └── report_routes.py
│   ├── users/                  # User management
│   │   ├── user_models.py
│   │   ├── user_routes.py
│   │   └── user_service.py
│   ├── static/                 # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── maps/
│   └── templates/              # Jinja2 templates
├── migrations/                 # Database migrations
├── delivery_tracking_model.ipynb  # ML model notebook
├── preprocess_data.py          # Data preprocessing script
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies
├── tailwind.config.js          # Tailwind configuration
└── README.md                   # This file


Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Contact

For questions or support, please contact the development team.

Future Enhancements

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Integration with more blockchain networks
- [ ] AI-powered route optimization
- [ ] Real-time notifications via SMS/Email