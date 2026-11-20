# 📦 Autonomous India Supply Chain Operations Agent

A deterministic, offline demonstration of **Agentic AI tool use** for supply-chain disruption triage and inventory rebalancing. The project uses a fictional Indian ERP network with simulated data; it does not connect to a production ERP, supplier, or carrier.

The sample network contains **5 SKUs across 5 Indian regional hubs**: Mumbai, Delhi NCR, Bengaluru, Chennai, and Kolkata. Inventory includes on-hand and reserved balances, daily demand, item-level safety stock, pack sizes, reorder points, product criticality, INR unit economics, and service-level penalty estimates. Three fictional India-based spot suppliers include SKU coverage, capacity, lead times, rush premiums, freight estimates, and reliability scores. Freight distances and quotes are planning estimates in kilometres and INR.

---

## 🎯 Use case: India supply-chain disruption and inventory rebalancing

### The problem

Indian manufacturers and distributors can face port congestion, monsoon flooding, supplier shortages, and inter-state transport delays. An operations team may need to check ERP stock, calculate demand cover and service exposure, compare regional hubs with suppliers, then arrange a transfer before a line or customer order is affected.

### The agentic AI solution

`Nexus-Ops` takes a disruption alert, evaluates the affected Indian destination, compares replenishment choices, and can reserve a simulated transfer through three tools:

```text
[Disruption alert]
       ↓
Tool 1: check_inventory_impact()
       → Checks available stock, demand, days of cover, deficit, and estimated INR exposure
       ↓
Tool 2: find_replenishment_options()
       → Compares Indian regional hubs and qualified suppliers by capacity, transit, and cost
       ↓
Tool 3: execute_stock_rebalance_order()
       → Reserves a simulated transfer, books freight, and creates order/BOL/tracking records
       ↓
[Executive summary with the decision and estimated impact]
```

The default walkthrough models a 12-day inbound delay affecting Mumbai's SKU-402 stock. The snapshot has 40 available units at 20 units of daily demand (2 days of cover), creating a 200-unit projected deficit. Delhi NCR has 530 units of transferable surplus; the agent can move the 200 needed units on an estimated 2-business-day route at ₹650 per unit (₹1,30,000 simulated freight). The displayed exposure is an estimate, not booked revenue or accounting profit.

---

## 🛠️ The three enterprise tool calls

| # | Tool | Role | Output |
|---|---|---|---|
| 1 | `check_inventory_impact` | Reads destination stock, reservations, demand, safety stock, and reorder point | Estimates days of cover, deficit units, revenue context, and service-level exposure in INR |
| 2 | `find_replenishment_options` | Scans other Indian hubs and qualified suppliers | Compares transferable capacity, pack size, safety buffers, kilometres, business-day transit, reliability, and estimated INR cost |
| 3 | `execute_stock_rebalance_order` | Commits a simulated transfer or emergency supplier order | Validates source capacity and pack sizes, reserves units, estimates ETA, and generates simulated order, BOL, and tracking IDs |

---

## 🧭 Dashboard tabs

- **Disruption Overview:** Choose the SKU, destination hub, delay, and incident details; run the three-step agent and review its decision.
- **Inventory Network:** Browse stock and demand across Mumbai, Delhi NCR, Bengaluru, Chennai, and Kolkata.
- **Transfer Orders:** Review simulated transfer orders, reservations, BOLs, carriers, and tracking details.
- **Replenishment Sources:** Compare available inter-hub transfers and supplier quotes for the selected SKU and destination.
- **Stockout Exposure:** Inspect days of cover, projected deficit, and estimated financial/service exposure in INR.
- **Agent Activity:** Follow the agent's reasoning, tool calls, observations, and outcome.
- **Scenario Settings:** Configure Indian disruption scenarios and optional periodic monitoring with simulated auto-orders.

All monetary amounts use Indian rupee formatting. The data and shipment records are fictional demonstration values; carrier names, where shown, are labels in the simulation and do not represent live bookings or quotes.

---

## 🛡️ Demo reliability and safety

- The default engine runs locally without a network connection or API key and follows a deterministic three-tool sequence against the simulated ERP snapshot.
- The dashboard optionally supports OpenAI Responses API tool calling. Local validation checks proposed tool arguments against incident and ERP data before execution.
- If an API call fails before dispatch, the workflow falls back to the local engine. The CLI always uses offline mode.
- Invalid SKU, source, destination, quantity, supplier qualification, or source capacity is surfaced without committing an order.
- A successful simulated dispatch reserves source stock for the lifetime of the app process. It does not contact an ERP, supplier, or carrier.
- Periodic monitoring runs only while the Streamlit session remains open; it is not a background service. Incident IDs prevent duplicate simulated orders.

### Optional OpenAI tool calling

1. Install dependencies: `pip install streamlit plotly requests`.
2. In **Disruption Overview**, enable **Use OpenAI tool calling** and enter an API key, or set `OPENAI_API_KEY` before starting Streamlit.
3. Optionally set `OPENAI_MODEL` (default: `gpt-4.1-mini`). API usage is billed to the account associated with the key.

The third tool is the only write operation. It runs only after the workflow identifies a source that can cover the need and arrive before the projected stockout, subject to local validation.

---

## 🚀 Run in VS Code

### Terminal demo

```powershell
python DEMO.py
```

The India scenario runs automatically. Use `python DEMO.py --custom` to change the inbound delay.

### Web dashboard

```powershell
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`. Select a disruption scenario and destination hub in **Scenario Settings**, then run the agent from **Disruption Overview**. Monitoring and simulated auto-orders are also configured in **Scenario Settings**.

### VS Code Run and Debug

Use the **Run and Debug** panel and select either `Run Terminal Demo (DEMO.py)` or `Run Streamlit Dashboard (app.py)`, then press **F5**.

---

## 🎤 Presenter talking points

1. **Set the context:** “This agent helps an Indian supply-chain operations team respond to a disruption by checking inventory, comparing replenishment paths, and preparing a simulated transfer.”
2. **Tool 1:** “Mumbai has 40 available units against daily demand of 20, so it has about two days of cover. A 12-day inbound delay implies a 200-unit deficit and ₹1,72,00,000 estimated exposure across projected unfulfilled revenue and SLA penalties.”
3. **Tool 2:** “The agent compares Indian hubs and qualified suppliers. Delhi NCR has 530 transferable surplus units; it can cover the 200-unit need in an estimated two business days.”
4. **Tool 3:** “The simulation reserves 200 units and estimates priority freight at ₹650 per unit, or ₹1,30,000. The ₹1,70,70,000 exposure-less-freight figure is a rough scenario comparison, not profit or a booked financial saving. The generated transfer order and tracking details are simulated.”

---

## 📁 Project structure

```text
Agentic AI/
├── DEMO.py              # Offline terminal walkthrough
├── app.py               # Streamlit dashboard and tab views
├── tools.py             # Three simulated ERP tools and India data
├── agent.py             # Agent loop and optional OpenAI tool calling
├── .vscode/launch.json  # VS Code Run and Debug profiles
└── README.md            # Project guide
```
