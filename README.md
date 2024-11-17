tree -I "venv|*.pyc|__pycache__"


# Project Directory Structure

```plaintext
├── README.md                          # Project overview and instructions.
├── assistants                         # Core logic for handling assistant functionalities.
│   ├── __init__.py                    # Module initialization file.
│   ├── expert_assistant.py            # Implements task delegation and advanced assistant logic.
│   └── logs                           # Assistant-related log files.
│       ├── application.log            # General assistant operation logs.
│       └── audit.log                  # Audit logs for sensitive assistant actions.
├── data                               # Directory for storing project data.
│   ├── __init__.py                    # Module initialization file.
│   └── ecommerce.db                   # SQLite database containing project data (e.g., carts, orders).
├── dev_tools                          # Tools for development and debugging.
│   ├── __init__.py                    # Module initialization file.
│   ├── logs                           # Logs generated during tool usage.
│   │   ├── application.log            # Logs tool activities.
│   │   └── audit.log                  # Logs sensitive tool operations.
│   └── visualize_state_graph_in_notebook.ipynb  # Jupyter notebook for state graph visualization.
├── main.py                            # Main entry point for the project.
├── scripts                            # Scripts for setting up and processing data.
│   ├── __init__.py                    # Module initialization file.
│   ├── initialize_data.py             # Populates the database with initial data.
│   ├── initialize_db.py               # Sets up database schemas.
│   ├── initialze_data_from_csv.py     # Imports data from CSV files.
│   └── main.py                        # Entry point for running all scripts.
├── state                              # Manages state and workflow of the application.
│   ├── __init__.py                    # Module initialization file.
│   ├── graph.py                       # Contains logic for state and workflow graphs.
│   └── state.py                       # Implements state persistence and updates.
├── tests                              # Contains unit tests and integration tests.
│   ├── __init__.py                    # Module initialization file.
│   ├── logs                           # Logs generated during test execution.
│   │   ├── application.log            # General test activity logs.
│   │   └── audit.log                  # Audit logs generated during tests.
│   ├── test_assistant.py              # Tests for assistant functionality.
│   └── test_database.py               # Tests for database operations.
├── tools                              # Provides modular utilities for specific tasks.
│   ├── __init__.py                    # Module initialization file.
│   ├── cart_tools.py                  # Tools for managing shopping cart operations.
│   ├── logs                           # Logs for tools usage.
│   │   ├── application.log            # Logs general tool activities.
│   │   └── audit.log                  # Logs sensitive tool actions.
│   ├── order_tools.py                 # Tools for managing orders.
│   ├── policy_tools.py                # Tools for querying policies or rules.
│   └── product_tools.py               # Tools for product searches and recommendations.
└── utils                              # General-purpose utilities for the project.
    ├── __init__.py                    # Module initialization file.
    ├── complete_or_escalate.py        # Logic for escalating or completing tasks.
    ├── logger.py                      # Provides logging capabilities.
    └── utilities.py                   # Miscellaneous utility functions.
```


Start chatbot

1. install requirements.txt


python3 -m venv venv

MACOS:
source venv/bin/activate

WIN:
.\venv\Scripts\activate

pip install -r requirements.txt

python tests/test_assistant.py


