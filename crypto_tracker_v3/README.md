# Crypto Portfolio Tracker v3.0.0

Advanced cryptocurrency portfolio management, tax calculation, and reporting system.

## Features

- 🏦 **Multi-Exchange Support**: Binance, Coinbase, Kraken, Blockchain
- 📊 **Portfolio Management**: Track wallets, balances, transactions
- 💰 **Tax Calculation**: FIFO, LIFO, Average Cost methods
- 📈 **DeFi Integration**: Uniswap V2/V3, Aave, Curve
- 📝 **Reporting**: Detailed portfolio and tax reports
- 🔒 **Secure**: Local-first architecture, encrypted secrets

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/mgenrique/crypto_tracker.git
cd crypto_tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/init_db.py

# Run tests
pytest -v
```

### Running the Server

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Access

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health/live

## Project Structure

```
crypto_tracker_v3/
├── src/
│   ├── api/              # Exchange connectors
│   ├── api/v1/           # FastAPI endpoints
│   ├── database/         # ORM and migrations
│   ├── models/           # Domain models
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── config/               # Configuration files
├── tests/                # Test suite
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
└── setup.py             # Package configuration
```

## Configuration

See `config/README.md` for detailed configuration instructions.

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test class
pytest tests/test_api.py::TestWalletEndpoints -v
```

## Documentation

- [Configuration Guide](config/README.md)
- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Development

### Adding a new exchange connector

1. Create new file in `src/api/`
2. Inherit from `BaseConnector`
3. Implement required methods
4. Add configuration to `config/networks.yaml`

### Running with Docker

```bash
docker-compose up -d
```

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/mgenrique/crypto_tracker/issues
- Email: your.email@example.com

---

**Status**: v3.0.0 (Beta)
**Last Updated**: December 2025
