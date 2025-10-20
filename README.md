# AI Crypto Trading Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

A web-based cryptocurrency trading simulation platform with AI-powered decision making.

## Features

- Real-time crypto market data integration
- AI-driven trading strategies using LLM APIs
- Portfolio management with leverage support
- Interactive dashboard with live charts
- Trade history and performance tracking

## Tech Stack

- Backend: Python/Flask
- Frontend: Vanilla JS, ECharts
- Database: SQLite
- APIs: OpenAI-compatible (OpenAI, DeepSeek, Claude via OpenRouter)

## Installation

```bash
pip install -r requirements.txt
python app.py
```

Access at `http://localhost:5000`

## Configuration

Add trading models through the web interface:
- Model name
- API key
- API endpoint
- Model identifier
- Initial capital

## Project Structure

```
trading_bot/
├── app.py              # Flask application
├── trading_engine.py   # Trading logic
├── ai_trader.py        # AI integration
├── database.py         # Data layer
├── market_data.py      # Market API
├── static/             # CSS/JS
├── templates/          # HTML
└── requirements.txt
```

## API Support

Compatible with OpenAI-format APIs:
- OpenAI (gpt-4, gpt-3.5-turbo)
- DeepSeek (deepseek-chat)
- Claude (via OpenRouter)

## Usage

1. Start the server
2. Add an AI model configuration
3. System starts trading automatically
4. Monitor portfolio in real-time

## Notes

- This is a simulation platform (paper trading only)
- Requires valid API keys for AI models
- Internet connection needed for market data

## Screenshots

![Dashboard](docs/images/dashboard.png)

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [FAQ](docs/FAQ.md)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

MIT - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Market data from CoinGecko API
- Charts powered by ECharts
- AI integration via OpenAI-compatible APIs

---

**Disclaimer**: This is a simulation platform for educational purposes only. Not financial advice.
