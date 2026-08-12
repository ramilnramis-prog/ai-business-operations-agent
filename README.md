# AI Business Operations Agent



An AI-powered business operations assistant built with OpenAI, LangGraph, FastAPI, Streamlit, and Pandas.



The agent analyzes structured business data from Excel, selects and executes deterministic business tools, detects sales anomalies, evaluates inventory risks, prioritizes products, calculates revenue exposure, and supports Human-in-the-Loop approval for reorder requests.



## Key Features



- AI agent powered by the OpenAI Responses API

- LangGraph workflow with state, nodes, edges, routing, and memory

- Tool Calling for deterministic business operations

- Excel data ingestion with validation

- Sales analysis by product

- Inventory shortage detection

- Automated reorder planning

- Product prioritization based on revenue and stock shortage

- Revenue exposure analysis

- Statistical sales anomaly detection

- Human-in-the-Loop approval and rejection workflow

- Conversation history and thread-based state

- FastAPI backend

- Streamlit web interface

- Automated pytest test suite

- Error handling and grounding rules to reduce hallucinations



## Architecture

The application is split into several layers:

1. **Frontend - Streamlit**

   * Uploads the Excel business file
   * Sends user requests to the backend
   * Displays conversation history
   * Shows pending Human-in-the-Loop approval requests
   * Allows the user to approve or reject reorder actions
2. **API Layer - FastAPI**

   * Handles file uploads
   * Validates business data
   * Starts agent runs
   * Resumes interrupted LangGraph workflows after user approval or rejection
3. **Agent Orchestration - LangGraph**

   * Stores agent state
   * Routes between the LLM, tools, and approval node
   * Maintains thread-based conversation state
   * Pauses execution when Human-in-the-Loop confirmation is required
4. **LLM Layer - OpenAI Responses API**

   * Understands the user's request
   * Selects the appropriate business tool
   * Interprets tool results
   * Generates grounded natural-language responses
5. **Business Tools - Python + Pandas**

   * Sales analysis
   * Inventory analysis
   * Reorder planning
   * Reorder request creation
   * Business overview analysis
   * Product prioritization
   * Revenue exposure analysis
   * Statistical anomaly detection
6. **Data Layer - Excel**

   * Sales sheet
   * Inventory sheet
   * File structure and required columns are validated before analysis





## Business Data Format



The agent works with a single Excel workbook named `business_data.xlsx`.



The workbook must contain two sheets:



### Sales



Required columns:



| Column | Description |

|---|---|

| `date` | Sale date |

| `product` | Product name |

| `category` | Product category |

| `units` | Units sold |

| `revenue` | Revenue generated |

| `price` | Product price |



### Inventory



Required columns:



| Column | Description |

|---|---|

| `product` | Product name |

| `warehouse` | Warehouse name |

| `stock` | Current stock |

| `reorder_level` | Target inventory level |



The file is validated before it becomes available to the agent. Invalid files are rejected and are not used for analysis.



## How to Run



### 1. Clone the repository



```bash

git clone <repository-url>

cd ai-business-operations-agent

```



### 2. Create and activate a virtual environment



Windows PowerShell:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



### 3. Install dependencies



For application runtime:



```powershell

pip install -r requirements.txt

```



For development and testing:



```powershell

pip install -r requirements-dev.txt

```



### 4. Configure environment variables



Create a `.env` file in the project root:



```env

OPENAI_API_KEY=your_openai_api_key

OPENAI_MODEL=your_model_name

```



The `.env` file is excluded from Git and should never be committed.



### 5. Start the FastAPI backend



```powershell

uvicorn app.main:app --host 127.0.0.1 --port 8000

```



The API will be available at:



```text

http://127.0.0.1:8000

```



### 6. Start the Streamlit frontend



Open a second terminal, activate the virtual environment again, and run:



```powershell

.\\.venv\\Scripts\\Activate.ps1

streamlit run frontend\\app.py

```



### 7. Run automated tests



```powershell

pytest -v

```

