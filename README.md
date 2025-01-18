# Crypto Trading Bot

## Overview
This is a personalized crypto trading bot designed to automate cryptocurrency trading based on predefined logic and strategies. The bot interacts with cryptocurrency exchanges to analyze price data, execute trades, and manage risk without human intervention.

## Table of Contents

- [Features](#features)
- [Features in the pipeline](#features-in-the-pipeline)
- [Technologies used](#technologies-used)
- [Project structure](#project-structure)
- [Known issues](#known-issues)

## Features
- **Automated buy/sell/hold trading logic**: Execute predefined trading actions based on market signals.
- **Integration with crypto exchange APIs**: Fetch real-time market data and execute trades.
- **Flexible configuration options**: Adjust key strategies and parameters to fit different market scenarios.
- **Real-time market data analysis**: Analyze and make decisions based on live price data.
- **Wallet tracking**: Monitor balances and assess portfolio performance.
- **Strategy scoring and evaluation**: Optimize strategies through a detailed scoring system.
- **Unit testing framework**: Ensure code quality and reliability by maintaining testing mechanisms.

## Features in the pipeline
- **24/7 trading framework**: Ensuring the bot continuously monitors the market and executes trades.
- **Multiple risk management strategies**: Introduce a selection of predefined risk strategies.
- **100% test coverage**: Establish comprehensive testing.
- **Enhanced backtesting features**: Develop advanced tools to simulate trading strategies using historical data.
- **Visualization dashboard**: Design a user-friendly dashboard featuring real-time stats, performance analytics, and detailed market insights.

## Technologies used
- **Python**: Primary programming language.
- **Binance API**: For fetching market data and trade execution.
- **TA-Lib**: For technical analysis calculations.
- **Pandas**: For data manipulation and analysis.
- **NumPy**: For numerical computations.
- **Pytest**: For unit testing the application.

## Project structure
```
crypto_bot/
├── config/
│   ├── config.yaml               # General bot configurations (e.g., API details, trading pairs)
│   ├── secrets.yaml              # Sensitive data like API keys (secured)
├── data/
│   ├── analysis/                 # Coin analysis
│   ├── indicators/               # Indicators for analysis
│   ├── logs/                     # Logs generated during runtime
│   ├── market/                   # Raw market data for analysis 
│   ├── wallet/                   # Wallet balance
├── indicators/
│   ├── __init__.py               
│   ├── indicator_base.py         # Base class for indicators
│   ├── trend_indicators.py       # Module for calculating trend-based indicators (e.g., moving averages)
│   ├── momentum_indicators.py    # Module for calculating momentum-based indicators (e.g., RSI, MACD)
│   ├── volatility_indicators.py  # Module for calculating volatility-based indicators (e.g., Bollinger Bands, ATR)
├── order_execution/              
│   ├── __init__.py               
│   ├── executor_base.py          # Base class/interface for executors
├── services/
│   ├── __init__.py               
│   ├── binance_auth.py           # Binance authentication
│   ├── data_fetcher.py           # Fetch market data from exchanges
│   ├── wallet_info.py            # Track portfolio (e.g., balances, PnL)
├── strategies/                   # New folder for all strategies
│   ├── __init__.py               
│   ├── base_strategy.py          # Base class/interface for all strategies
│   ├── scoring_systems.py        # Systems to score and evaluate strategies or trades 
├── tests/
│   ├── test_indicators.py        # Unit tests for indicators
│   ├── test_order_execution.py   # Unit tests for order execution
│   ├── test_services.py          # Unit tests for services
│   ├── test_utils.py             # Unit tests for utils
├── utils/
│   ├── __init__.py               
│   ├── file_utils.py             # Helper functions for file manipulations
│   ├── order_execution.py        # Helper functions for order execution
├── .env                          # Environment variables
├── .gitignore                    # Ignore secrets, logs, etc., for Git
├── main.py                       # Entry point for the bot
├── README.md                     # Project documentation
├── requirements.txt              # Python package dependencies
└── structure.yaml                # Project folder structure
```

## Known issues
- **Error handling**: Comprehensive error handling for API failures and connection issues is limited
- **Floating points imprecision**: The bot calculations might experience floating point inaccuracies during financial computations.
