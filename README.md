# 🔍 Insurance Fraud Graph Intelligence Platform

**A comprehensive demonstration of how GraphRAG reveals fraud patterns invisible to traditional relational database approaches.**

Built for P&C Insurance SIU teams and business stakeholders new to graph technology.

![Demo Overview](https://via.placeholder.com/800x400?text=Fraud+Network+Visualization)

## 🎯 What This Demo Shows

Insurance fraud costs **$308 billion annually**, yet traditional detection methods analyze only **5% of claims**. Why? Because fraud operates through *relationships*—organized rings connecting claimants, attorneys, medical providers, and repair shops—that span multiple systems and never appear together in any single database table.

This demo shows how graph databases + LLMs reveal:

| Pattern | Traditional Approach | Graph Approach |
|---------|---------------------|----------------|
| **Provider-Attorney Collusion** | Invisible (different tables) | Shared fax number links 3 "independent" firms |
| **Staged Accident Rings** | Missed (role-based tables) | Same 4 people rotate Driver/Passenger/Witness |
| **Vehicle Recycling** | Clean claimant = approved | VIN totaled 3x in 18 months |
| **Network Migration** | Case closed | Former employee reopens operation |

## ✨ Features

### 🎯 Guided Scenario Walkthroughs
Step-by-step investigation of 4 research-grounded fraud scenarios:
- **Spider Web** - Provider-Attorney Collusion ($162K exposure)
- **Role Chameleon** - Staged Accident Ring ($120K exposure)
- **Immortal Asset** - Vehicle Recycling ($185K exposure)
- **Network Migration** - Post-Prosecution Evolution ($280K+ exposure)

### 💬 AI-Powered Chat Interface
Ask questions in natural language, get Cypher queries + insights:
- "Which providers have unusually high attorney representation?"
- "Are there attorneys sharing fax numbers?"
- "Find people appearing in claims with different roles"

### 🕸️ Interactive Network Visualization
Explore fraud networks with:
- Color-coded entity types
- Interactive zoom/pan
- Hover tooltips with entity details
- Relationship labels

### ⚙️ Administration
- One-click demo data generation
- Database statistics
- Connection management

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Neo4j AuraDB account (free tier works)
- LLM API key: **Groq** (recommended, free) or Google Gemini

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd fraud-graph-demo

pip install -r requirements.txt
```

### 2. Configure Secrets

Create `.streamlit/secrets.toml`:

```toml
# Neo4j AuraDB (required)
[neo4j]
uri = "neo4j+s://your-instance.databases.neo4j.io"
user = "neo4j"
password = "your-password"

# LLM API (choose one)

# Option 1: Groq (Recommended - Free, Fast, Llama 3.3 70B)
# Get free key at: https://console.groq.com/keys
[groq]
api_key = "gsk_your_groq_api_key"

# Option 2: Google Gemini (Alternative)
# Get key at: https://aistudio.google.com/app/apikey
# [gemini]
# api_key = "your-gemini-api-key"
```

**Why Groq?** Free tier with 14,400 requests/day, blazing fast inference (300+ tokens/sec), and Llama 3.3 70B is excellent at structured query generation.

### 3. Generate Demo Data

Option A - Via Streamlit UI:
1. Launch app: `streamlit run app.py`
2. Go to ⚙️ Administration
3. Click "Generate All Scenarios"

Option B - Via command line:
```bash
python scenario_data_generator.py
```

### 4. Explore!

```bash
streamlit run app.py
```

## 📁 Project Structure

```
fraud-graph-demo/
├── app.py                      # Main unified application
├── fraud_graph_chat.py         # Standalone chat interface
├── scenario_data_generator.py  # Demo data generator
├── requirements.txt            # Python dependencies
├── secrets.toml.template       # Configuration template
├── README.md                   # This file
└── .streamlit/
    └── secrets.toml            # Your credentials (gitignored)
```

## 🎓 Fraud Scenarios Explained

### Scenario 1: Spider Web (Provider-Attorney Collusion)

**The Signal:** Metro Care Clinic bills 20% above peer average for soft tissue claims.

**What Traditional Methods See:**
- 45 claims with valid CPT codes
- Multiple referring attorneys (looks diverse)
- 20% variance noted but not actionable

**What Graph Reveals:**
- 100% of patients have attorney representation (vs. 10-15% norm)
- All 45 patients funnel through just 3 law firms
- Those 3 "independent" firms share the same fax number (discovered via OCR)

**Exposure:** $162,000 (all claims now deniable for fraud conspiracy)

### Scenario 2: Role Chameleon (Staged Accident Ring)

**The Signal:** Witness "Darius Thorne" has 1 prior claim as a passenger.

**What Traditional Methods See:**
- 2 claims in different roles = coincidence
- Below frequency threshold
- No flag triggered

**What Graph Reveals:**
- 4 people rotate through Driver/Passenger/Witness roles across 4 claims
- Never in the same role twice (evades per-role frequency counters)
- All 4 previously lived at the same "ghost address" 2+ years ago

**Exposure:** $120,000 (classic Crash-for-Cash ring)

### Scenario 3: Immortal Asset (Vehicle Recycling)

**The Signal:** Clean policyholder files total loss claim 50 days after binding.

**What Traditional Methods See:**
- Claimant has clean record
- Vehicle exists, premium paid
- Claim approved for payment

**What Graph Reveals:**
- This VIN has been "totaled" 3 times in 18 months
- 3 different "owners" (all with clean records)
- All 3 bound policies from the same mobile device fingerprint

**Exposure:** $185,000 (vehicle recycling with identity laundering)

### Scenario 4: Network Migration

**The Signal:** Dr. Bernard's was prosecuted 6 months ago. Case closed.

**What Traditional Methods See:**
- Provider blacklisted
- Claims denied
- Success recorded, resources redeployed

**What Graph Reveals:**
- Attorney Michael Chen (never sanctioned) acquired 34 new clients
- 82% of his new clients treated at "Rapid Recovery Medical"
- Rapid Recovery opened 2 months after Bernard's closure
- Owned by Dr. Patricia Simmons—Bernard's former employee

**Exposure:** $280,000+ in active claims from migrated network

## 🛠️ Technical Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│  Google Gemini  │────▶│    Neo4j        │
│   Frontend      │     │  (NL → Cypher)  │     │    AuraDB       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                                              │
        │         Natural Language Question            │
        │         "Find shared devices"                │
        │                    │                         │
        │                    ▼                         │
        │         MATCH (a)-[:SHARES_DEVICE]->(e)     │
        │         RETURN a, e                         │
        │                    │                         │
        │                    ▼                         │
        └──────────────Graph Visualization─────────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Graph Database** | Store entities + relationships | Neo4j AuraDB (free tier) |
| **LLM** | Convert questions to Cypher | Google Gemini 1.5 Flash |
| **Frontend** | Interactive web interface | Streamlit |
| **Visualization** | Render fraud networks | streamlit-agraph |

## 📊 Graph Schema

### Node Types
- `Claim` - Insurance claims with amounts, dates, types
- `Person` - Claimants, witnesses, adjusters
- `Provider` - Medical clinics, hospitals
- `Attorney` - Legal representatives
- `Vehicle` - Insured vehicles
- `Address` - Physical locations
- `Phone/Entity` - Shared devices (fax, mobile fingerprints)
- `Policy` - Insurance policies
- `Location` - Accident locations

### Key Relationships
- `(Claim)-[:FILED_BY]->(Person)`
- `(Claim)-[:TREATED_AT]->(Provider)`
- `(Claim)-[:REPRESENTED_BY]->(Attorney)`
- `(Attorney)-[:SHARES_DEVICE]->(Entity)` ← The collusion indicator!
- `(Person)-[:LIVES_AT]->(Address)`
- `(Person)-[:FORMER_EMPLOYEE_OF]->(Provider)` ← Network migration link!

## 💡 Example Chat Queries

**Basic Discovery:**
```
"How many claims are in the system?"
"Which providers have the most claims?"
"What are the different incident types?"
```

**Fraud Pattern Detection:**
```
"Which providers have unusually high attorney representation rates?"
"Are there attorneys sharing fax numbers or devices?"
"Find people who appear in claims with different roles"
"Which vehicles have multiple total loss claims?"
```

**Network Investigation:**
```
"Show me the network around Metro Care Clinic"
"Find all claims connected through shared devices"
"Identify addresses where multiple claimants lived"
"Find providers connected to revoked licenses"
```

## 📈 Business Impact

| Metric | Traditional | With GraphRAG | Improvement |
|--------|------------|---------------|-------------|
| Claims flagged for review | 5% | 15%+ | 3x |
| Time to map fraud ring | 3-4 weeks | 45 seconds | 99.9% |
| Missed subrogation | $15-20B/year | Reduced by 20-30% | $3-6B saved |
| Detection rate | Baseline | +135%* | Proven ROI |

*Based on US multinational insurer case study

## 🔐 Security Notes

- Never commit `secrets.toml` to version control
- Use environment variables in production
- Neo4j AuraDB includes encryption in transit
- Consider data masking for real PII

## 📚 Resources

- [Neo4j AuraDB Free](https://neo4j.com/cloud/aura-free/) - Get your graph database
- [Google AI Studio](https://makersuite.google.com/) - Get Gemini API key
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/)

## 🤝 Contributing

This is a demonstration tool. For production use:
1. Add authentication/authorization
2. Implement proper data masking for PII
3. Add audit logging
4. Consider enterprise Neo4j deployment
5. Add rate limiting for LLM calls

## 📄 License

MIT License - Use freely for demos and learning.

---

**Built to demonstrate GraphRAG for P&C Insurance fraud detection.**

*"GraphRAG answers questions your current systems cannot even ask."*
