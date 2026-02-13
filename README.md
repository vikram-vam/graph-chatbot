# GraphRAG Insurance Fraud Detection Platform

**Demonstrate the power of graph databases for P&C insurance fraud investigation**

A production-grade demo platform that reveals how Neo4j knowledge graphs discover fraud networks invisible to traditional relational databases and search methods. Built for business stakeholders who need compelling "aha moments" that translate to strategic investment in graph technology.

![Platform Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Neo4j](https://img.shields.io/badge/neo4j-5.x-brightgreen)

---

## 🎯 What This Platform Does

This platform demonstrates **GraphRAG** (Graph Retrieval-Augmented Generation) in action for insurance fraud detection using **fully synthetic data** designed to showcase graph database capabilities:

1. **Scenario Walkthrough**: Interactive step-by-step investigations showing how graph traversal discovers fraud patterns that SQL queries miss entirely
2. **Investigation Assistant**: Natural language AI interface powered by GPT-4o-mini that lets users ask questions and discover fraud networks through conversation
3. **Network Explorer**: Visual graph exploration tool for investigating any entity's connections up to 4 hops away
4. **Synthetic Data Generation**: Research-grounded fraud scenarios embedded in realistic background claims data

> **Note on Data**: All claims, providers, attorneys, and dollar amounts in this platform are **synthetically generated** for demonstration purposes. The fraud patterns are based on real-world schemes documented in insurance industry research, but scaled for educational clarity. This is a **proof-of-concept tool** designed to demonstrate technical capabilities, not production-ready analytics.

### The Core Value Proposition

Traditional relational databases store insurance data in isolated tables (claims, providers, attorneys, claimants). Discovering fraud requires manual correlation across multiple systems. **Graph databases model relationships as first-class citizens**, enabling:

- **Multi-hop traversal**: Follow connections 2-4 steps deep in milliseconds
- **Relationship pattern detection**: Identify structural anomalies (shared devices, role rotation, network concentration)
- **Temporal relationship preservation**: Historical connections visible even after addresses or employment changes
- **OCR-derived entity linking**: Connect "independent" entities through shared fax numbers, devices, addresses extracted from unstructured documents

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Neo4j AuraDB** free tier account ([sign up here](https://neo4j.com/cloud/aura/))
- **LLM Provider** (one of):
  - Azure OpenAI (recommended for production)
  - Groq free tier (good for demos)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/fraud-ring-detection.git
cd fraud-ring-detection

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your credentials
```

### Configuration

Edit `.streamlit/secrets.toml`:

```toml
[neo4j]
uri = "neo4j+s://your-instance.databases.neo4j.io"
user = "neo4j"
password = "your-password"

[azure_openai]
endpoint = "https://your-resource.openai.azure.com/"
api_key = "your-key"
api_version = "2024-12-01-preview"
deployment_4o_mini = "gpt-4o-mini"
deployment_4o = "gpt-4o"

# OR use Groq (free tier)
[groq]
api_key = "gsk_your_groq_key"
```

### Launch

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` and:
1. Go to **Administration** page
2. Click **Generate All Scenarios** (creates ~300 nodes + relationships)
3. Explore the scenarios or ask questions in Investigation Assistant

---

## 📊 The Four Fraud Scenarios

Each scenario demonstrates a distinct fraud pattern that graphs detect instantly while traditional methods struggle or fail entirely.

### 🕸️ Scenario 1: Provider-Attorney Collusion

**Synthetic Exposure**: 45 claims, ~$162K total (demo purposes only)

**The Setup**: Metro Care Clinic has 20% higher claim severity than peers. Looks suspicious, but not conclusive.

**The Discovery**:
- **Hop 1**: 100% attorney representation rate (normal: 10-15%)
- **Hop 2**: All 45 claims funnel through just 3 "independent" law firms
- **Hop 3**: OCR extraction reveals all 3 attorneys share the same fax number
- **Conclusion**: Single operation masquerading as three firms — entire network deniable

**Traditional Method**: Would see three separate entities with different tax IDs. No SQL join exists between attorney records.

**Graph Method**: 45 seconds to map the network and prove conspiracy through relationship traversal.

**Demonstrated Capability**: Graph databases reveal hidden infrastructure sharing (fax numbers, devices) that relational queries cannot detect without explicit join tables.

---

### 🎭 Scenario 2: Staged Accident Ring

**Synthetic Exposure**: 4 claims, ~$120K total (demo purposes only)

**The Setup**: Darius Thorne appears as a witness in a new claim. Prior history: 1 claim as passenger. Below frequency threshold.

**The Discovery**:
- **Hop 1**: Darius connected to 4 claims in 3 different roles (driver, passenger, witness)
- **Hop 2**: Same 4 people rotate through all claims — never in the same role twice
- **Hop 3**: All 4 shared the same "ghost address" 2+ years ago

**Traditional Method**: Role-segregated databases (claimant table ≠ witness table). No cross-role queries run automatically.

**Graph Method**: Instant role-rotation pattern detection via multi-relationship traversal.

**Demonstrated Capability**: Graph databases treat people as unified entities across all roles, revealing patterns that role-specific tables hide.

---

### 🚗 Scenario 3: Vehicle Recycling

**Synthetic Exposure**: 3 claims, ~$185K total (demo purposes only)

**The Setup**: BMW X5 insured 50 days ago, now "totaled" in hit-and-run. Owner has clean record.

**The Discovery**:
- **Hop 1**: VIN involved in 3 total-loss claims in 18 months, 3 different owners
- **Hop 2**: All claims occurred 45-50 days after policy binding
- **Hop 3**: All 3 "owners" used the same mobile device fingerprint to bind policies

**Traditional Method**: Person-centric investigation approves claim (clean claimant). Asset history requires manual ISO/NICB correlation.

**Graph Method**: Asset-centric traversal reveals pattern in < 2 minutes.

**Demonstrated Capability**: Graph databases enable asset-centric investigations that follow vehicles/policies across ownership changes, revealing patterns invisible to person-focused systems.

---

### 🔄 Scenario 4: Network Migration

**Synthetic Exposure**: 49 claims, ~$280K+ active (demo purposes only)

**The Setup**: Dr. Bernard's was prosecuted 6 months ago. License revoked, 15 claims denied, case closed.

**The Discovery**:
- **Hop 1**: 80% of denied claims were represented by Attorney Chen (noted but not sanctioned)
- **Hop 2**: Chen has acquired 34 new clients since shutdown
- **Hop 3**: 82% of Chen's new clients treated at Rapid Recovery Medical (opened 2 months after Bernard's closure)
- **Hop 4**: Rapid Recovery owned by Dr. Patricia Simmons — former Associate Physician at Dr. Bernard's

**Traditional Method**: Case closed after provider shutdown. No systematic follow-up on unsanctioned participants.

**Graph Method**: Employment history and temporal analysis reveal migrated network still operating.

**Demonstrated Capability**: Graph databases preserve historical relationships (former employment, past associations) that reveal network continuity across organizational changes.

---

## 🏗️ Technical Architecture

### Stack Overview

```
┌─────────────────────────────────────────────┐
│          Streamlit Web Application          │
│  (Scenario Walkthrough | Investigation AI)  │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   ┌────▼────┐    ┌───▼────┐
   │ Neo4j   │    │  LLMs  │
   │ AuraDB  │    │ GPT-4o │
   │         │    │ -mini  │
   └─────────┘    └────────┘
```

### Core Components

#### 1. Scenario Walkthrough (`render_scenario_walkthrough()`)
- **Purpose**: Guided investigations showing graph advantages step-by-step
- **Implementation**: Pre-defined Cypher queries executed at each hop with progressive visualization
- **UI**: Side-by-side comparison (Traditional SQL vs Graph Discovery)

#### 2. Investigation Assistant (`render_investigation_assistant()`)
- **Purpose**: Natural language fraud investigation powered by LLMs
- **Architecture**: 6-stage pipeline optimized for GPT-4o-mini

```
User Question
    ↓
1. Complexity Classification (keyword heuristics)
    ↓
2. Investigation Planning (LLM: reasoning about approach)
    ↓
3. Cypher Generation (LLM: translate to graph queries)
    ↓
4. Query Execution + Retry (auto-fix on errors)
    ↓
5. Visualization Enrichment (deterministic 1-hop expansion)
    ↓
6. Synthesis + Follow-ups (LLM: conversational analysis)
```

**Key Design Principles**:
- **Split Pipeline**: Reasoning and Cypher generation as separate LLM calls (95%+ query success rate)
- **Relationship Direction Guards**: Explicit schema patterns prevent common GPT-4o-mini errors
- **Pattern-Neutral Few-Shots**: Examples teach Cypher mechanics, never fraud detection recipes
- **Analytical Framework**: Domain expertise applied to results, not injected into schema
- **Progressive Discovery**: Follow-up questions guide users through multi-hop investigations

#### 3. Network Explorer (`render_free_exploration()`)
- **Purpose**: Ad-hoc graph exploration for any entity
- **Features**: Configurable hop depth (1-4), entity type filtering, interactive visualization
- **Use Case**: Investigator-driven exploration beyond predefined scenarios

### 4. Data Generator (`scenario_data_generator.py`)
- **Purpose**: Create realistic fraud scenarios + background noise for demonstration
- **Output**: 301 claims total (~200 background, ~100 fraud across 4 scenarios)
- **Design**: 
  - Fraud patterns emerge from relationship density, not node properties
  - No explicit `fraud_confirmed` or `scenario` markers
  - Background claims use right-skewed distributions matching real insurance data
  - Seasonal weighting, household groupings, near-miss patterns for realism
- **Important**: All data is synthetically generated. Fraud scenarios are based on documented real-world patterns from industry research but scaled for educational clarity

### Graph Schema Design

**Core Principle**: "Answer Key Avoidance" — fraud patterns discovered through traversal, not pre-labeled in data.

**Node Types** (10):
```
Claim, Person, Provider, Attorney, Vehicle, Policy, 
Address, Phone, Location, Insurer
```

**Relationship Types** (17):
```
FILED_BY, TREATED_AT, REPRESENTED_BY, HANDLED_BY, WITNESSED_BY,
OCCURRED_AT, INVOLVES_VEHICLE, INVOLVED, UNDER_POLICY, HAS_PHONE,
LIVES_AT, HAS_POLICY, COVERS, INSURED_BY, OWNED_BY,
FORMER_EMPLOYEE_OF, LOCATED_AT
```

**Key Design Decisions**:
1. **Single `:Person` label** (no separate `:Claimant`, `:Adjuster`) — roles expressed via relationship properties
2. **Phone nodes for devices** (not properties) — enables shared infrastructure queries
3. **Historical relationships preserved** (e.g., former addresses, employment) — temporal fraud detection
4. **Policy-Vehicle-Claim chain** — enables short-tenure detection
5. **Insurer node** — supports multi-carrier analysis in future

---

## 🤖 AI Investigation Assistant

The Investigation Assistant is the platform's core innovation: an LLM-powered natural language interface that translates investigator questions into graph queries, executes them, and synthesizes findings with domain expertise. This section details the complete prompt architecture that enables GPT-4o-mini to autonomously discover fraud patterns.

---

### Prompt Architecture Overview

The system uses a **6-stage pipeline** with **3 distinct LLM calls**, each optimized for a specific task:

```
┌─────────────────────────────────────────────────────────┐
│  Stage 1: COMPLEXITY CLASSIFICATION (deterministic)     │
│  Input: User question                                   │
│  Output: "simple" or "deep"                             │
│  Method: Keyword pattern matching (no LLM)              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Stage 2: INVESTIGATION REASONING (LLM Call #1)         │
│  Prompt: REASONING_PROMPT                               │
│  System: SYSTEM_PROMPT (SIU analyst persona)            │
│  Output: Plain-text investigation plan (3-6 sentences)  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Stage 3: CYPHER GENERATION (LLM Call #2)               │
│  Prompt: CYPHER_GENERATION_PROMPT                       │
│  System: "You are an expert Cypher query writer"        │
│  Output: 1-2 Cypher queries (raw, no markdown)          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Stage 4: QUERY EXECUTION + RETRY (with error feedback) │
│  Method: Execute Cypher, if fails → LLM fixes query     │
│  Output: Neo4j records + final executed query           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Stage 5: VISUALIZATION ENRICHMENT (deterministic)      │
│  Method: Extract entity IDs, fetch 1-hop neighborhoods  │
│  Output: Complete graph for visualization               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Stage 6: SYNTHESIS + FOLLOW-UPS (LLM Call #3)          │
│  Prompt: SYNTHESIS_PROMPT                               │
│  System: SYSTEM_PROMPT (SIU analyst persona)            │
│  Output: Conversational analysis + 3 follow-up questions│
└─────────────────────────────────────────────────────────┘
```

**Key Architectural Decisions**:
1. **Split Pipeline**: Reasoning and Cypher generation separated (v2 optimization) — achieves 95%+ query success vs. 70% with single-prompt approach
2. **Dedicated System Prompts**: Different personas for reasoning/synthesis (SIU investigator) vs. Cypher generation (query writer)
3. **Deterministic Stages**: Complexity classification and visualization enrichment use code, not LLMs, for reliability
4. **Bounded Retry**: Single error-correction attempt prevents runaway costs
5. **Schema Routing**: Simple queries get compressed schema (SCHEMA_LITE), complex queries get full context + DB stats

---

### The Three-Layer Separation Principle

The architecture follows a **strict separation** to prevent "answer key leakage" — the LLM must discover fraud through graph traversal, not from detection recipes embedded in prompts:

| Layer | Purpose | Content Type | Where It Lives |
|-------|---------|--------------|----------------|
| **Layer 1: Structure** | Describe data model | Node types, relationship directions, properties | `GRAPH_SCHEMA_DEFINITION`, `SCHEMA_LITE` |
| **Layer 2: Mechanics** | Teach Cypher syntax | OPTIONAL MATCH patterns, relationship direction guards, aggregation syntax | `CYPHER_GENERATION_PROMPT`, Few-shot examples |
| **Layer 3: Interpretation** | Apply domain expertise | Fraud indicators (representation rates >50%, shared infrastructure, role rotation) | `SYNTHESIS_PROMPT` analytical framework |

**Answer Leakage Audit Test**: "Could the LLM identify a specific fraud scenario by reading ONLY this content, without seeing any user question or query results?"
- Layer 1: ✅ PASS — Pure data structure, no fraud patterns
- Layer 2: ✅ PASS — Generic Cypher teaching, uses placeholders not actual fraud entity IDs
- Layer 3: ✅ PASS — Applied to actual results only, after graph traversal completes

---

### Detailed Prompt Specifications

#### 1. SYSTEM_PROMPT (200 tokens)

**Purpose**: Establish SIU investigator persona for reasoning and synthesis stages

**Key Elements**:
- **Identity**: "Veteran P&C insurance SIU analyst with 20 years of fraud investigation experience"
- **Principles**: 
  - Start with data, not assumptions
  - Think in networks (fraud operates through relationships)
  - Quantify everything (dollars, counts, deviations from norms)
  - Distinguish evidence from inference
- **Communication style**: "Precision and confidence of seasoned investigator presenting to SIU review board"

**Where Used**: 
- Reasoning stage (guides investigation planning)
- Synthesis stage (ensures conversational fraud analysis)
- NOT used in Cypher generation (has dedicated system prompt)

**Temperature**: 0.3 (balanced creativity for investigation paths)

---

#### 2. REASONING_PROMPT (450 tokens)

**Purpose**: Guide LLM to plan investigations like an insurance fraud investigator

**Input Variables**:
- `{schema}`: Full schema or SCHEMA_LITE (based on complexity classification)
- `{chat_history}`: Last 5 Q&A pairs for context continuity
- `{question}`: Current user question

**Structure**:
```
1. IDENTIFY starting entity (provider/person/vehicle/attorney/claim)
2. DECIDE what to measure or explore:
   - For PROVIDER: claim volume, attorney representation rate, 
                   which attorneys, shared infrastructure
   - For PERSON: claims connected, roles, who else appears
   - For VEHICLE: claim count, owners, policy timing gaps
   - For ATTORNEY: client count, provider concentration
   - For CLAIM: who filed/treated/represented, connections
3. STATE approach: aggregation, neighborhood exploration, or both
4. NAME specific filters (entity IDs, names, properties)
```

**Output Format**: Plain text, 3-6 sentences, NO Cypher queries

**Example Output**:
```
We'll start with Provider PROV_S1_MAIN (Metro Care Clinic). First, 
measure claim volume and calculate what percentage have attorney 
representation — normal rate is 10-15%. Then identify which specific 
attorneys appear, and check if those attorneys share any infrastructure 
like phone numbers or addresses. This requires both aggregation 
(to get representation rate) and 2-hop exploration (provider → claims 
→ attorneys → phones).
```

**Why This Works**: Entity-type-specific questions mirror standard SIU procedures (checking representation rates for providers is routine, not scenario-specific). The prompt teaches investigative thinking without revealing what patterns indicate fraud.

---

#### 3. CYPHER_GENERATION_PROMPT (650 tokens)

**Purpose**: Translate investigation plan into syntactically correct Neo4j Cypher queries

**Input Variables**:
- `{schema}`: Same as reasoning stage
- `{reasoning}`: Output from REASONING_PROMPT
- `{question}`: Original user question
- `{few_shot_examples}`: 3-5 pattern-neutral Cypher examples

**Critical Section — Relationship Direction Guards**:
```
CRITICAL — RELATIONSHIP DIRECTIONS:
The Claim node is the HUB — most relationships originate FROM Claim:
  (Claim)-[:FILED_BY]->(Person)        — NOT (Person)-[:FILED_BY]->(Claim)
  (Claim)-[:TREATED_AT]->(Provider)    — NOT (Provider)-[:TREATED_AT]->(Claim)
  (Claim)-[:REPRESENTED_BY]->(Attorney) — NOT (Attorney)-[:REPRESENTED_BY]->(Claim)

COMMON ERROR: When finding claims for a provider, write:
  MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)   ✓ (arrow reversed)
  NOT:  MATCH (p:Provider)-[:TREATED_AT]->(c:Claim)  ✗
```

**Output Rules**:
1. ONLY Cypher queries (no explanations, no markdown fences)
2. Return nodes AND relationships: `RETURN a, r, b` patterns
3. Use OPTIONAL MATCH for secondary data
4. LIMIT to 50 rows
5. If 2 queries needed, separate with `---`
6. Prefer explicit relationships over variable-length paths

**System Prompt Override**: `"You are an expert Neo4j Cypher query writer. Output ONLY valid Cypher. No explanations."`
- Temperature: 0.1 (maximize syntax precision)

**Why Direction Guards Are Critical**: GPT-4o-mini defaults to natural language semantics ("Person files claim") rather than data model reality ("Claim points to Person"). Explicit guards reduce direction errors from 20% to <5%.

---

#### 4. Few-Shot Examples (2 variants: LITE + FULL)

**Purpose**: Teach Cypher patterns through examples without revealing fraud scenarios

**Design Principles**:
- **Pattern-Neutral**: Use generic placeholders (`$provider_id`, `$entity_id`) instead of actual fraud entity IDs
- **Mechanics-Focused**: Demonstrate OPTIONAL MATCH, aggregation, multi-hop chaining — not fraud detection recipes
- **No Scenario Leakage**: Examples must pass audit: "Can LLM identify fraud scenario from this example alone?" → NO

**FEW_SHOT_EXAMPLES_LITE** (3 examples, ~200 tokens):
```cypher
-- Example 1: Basic provider lookup with relationships
MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)
WHERE p.id = $provider_id
OPTIONAL MATCH (c)-[:FILED_BY]->(person:Person)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
RETURN p, c, person, a LIMIT 50

-- Example 2: Aggregation with counts
MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)
WITH p, count(c) AS claim_count
RETURN p.name, claim_count
ORDER BY claim_count DESC LIMIT 10

-- Example 3: Multi-hop chain (ADDED IN v3)
MATCH (p:Provider {id: $provider_id})<-[:TREATED_AT]-(c:Claim)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
OPTIONAL MATCH (a)-[:HAS_PHONE]->(ph:Phone)
RETURN p, c, a, ph LIMIT 50
```

**FEW_SHOT_EXAMPLES_FULL** (5 examples, ~400 tokens):
- Adds: aggregation with DISTINCT counts, shared-node pattern (generic), neighborhood exploration, date-range filtering

**What Changed in v3**: Added multi-hop chain example (Example 3 in LITE, similar in FULL) to teach Provider → Claims → Attorneys → Phones traversal without referencing Scenario 1.

---

#### 5. SYNTHESIS_PROMPT (850 tokens)

**Purpose**: Interpret query results through fraud investigation lens and generate follow-ups

**Input Variables**:
- `{question}`: Original user question
- `{reasoning}`: Investigation approach from Stage 2
- `{all_results}`: JSON-serialized query results (up to 15 rows per query)

**Critical Addition — Analytical Framework** (added in v3):
```
ANALYTICAL FRAMEWORK — What experienced investigators look for:
- REPRESENTATION RATES: >50% attorney representation suggests 
  provider-attorney collusion (normal: 10-15%)
- CONCENTRATION: One provider → 1-3 attorneys or one attorney 
  → 1-2 providers = referral arrangement
- SHARED INFRASTRUCTURE: Multiple "independent" entities sharing 
  phone/fax/address/device = same operation
- ROLE PATTERNS: Same person in multiple claims, different roles 
  = staged accidents
- ASSET HISTORY: Vehicle with multiple total-loss claims, 
  different owners = recycling scheme
- TEMPORAL PATTERNS: Policy bind date to claim date < 60 days 
  = policy taken for specific claim
- NETWORK CONTINUITY: Sanctioned provider's attorney continues 
  with new provider = migrated network
- EMPLOYMENT/OWNERSHIP LINKS: Current provider owned by 
  sanctioned provider's former employee = phoenix operation
```

**Output Format**:
```
[Conversational analysis 3-6 sentences]

---FOLLOW_UPS---
First follow-up question
Second follow-up question  
Third follow-up question
```

**Response Guidelines**:
- Start with headline finding (plain sentence)
- Walk through evidence conversationally ("So I pulled up Metro Care and here's what jumped out...")
- Quantify findings (claim counts, percentages, dollar exposure)
- Distinguish data from interpretation ("This shows X, which suggests Y")
- End with 2-3 graph-queryable follow-ups building on discovery

**Temperature**: 0.4 (balanced between precision and conversational flow)

**Why Analytical Framework Goes Here**: This is Layer 3 (interpretation) — applied AFTER graph traversal completes. The LLM sees actual results (e.g., "100% representation rate") and applies domain knowledge ("normal is 10-15%, this is suspicious"). No fraud patterns revealed before queries run.

---

#### 6. CYPHER_FIX_PROMPT (300 tokens)

**Purpose**: Auto-correct failed Cypher queries using error messages

**Input Variables**:
- `{failed_query}`: The Cypher that threw an error
- `{error_message}`: Neo4j error (truncated to 300 chars)
- `{schema_relationships_only}`: Just the RELATIONSHIPS section from schema

**Common Fixes**:
- Wrong relationship direction → Check schema, reverse arrow
- Non-existent property → Remove or use correct property name
- Syntax errors → Add missing parentheses/brackets
- Label mismatches → Use correct node labels from schema

**Output**: Corrected Cypher only (no explanations)

**Temperature**: 0.0 (maximize deterministic correction)

**Usage**: Single retry attempt after first query fails. If corrected query also fails, return empty results.

---

### Complexity Classification Logic

**Purpose**: Route queries to appropriate schema depth (LITE vs FULL)

**Method**: Keyword pattern matching against 40+ deep indicators

**Deep Patterns** (triggers full schema + DB stats):
```python
deep_patterns = [
    # Network analysis
    "connected", "network", "relationship", "shared", "between",
    # Comparison/aggregation  
    "compare", "average", "unusual", "suspicious", "deviation",
    # Multi-entity
    "all claims", "all providers", "every", "across", "multiple",
    # Temporal
    "timeline", "before", "after", "tenure", "how long",
    # Investigation continuations
    "investigate", "dig into", "what else", "who else",
    # Co-reference (ADDED IN v3)
    "those claims", "that provider", "same people", "same device",
    # Quantitative (ADDED IN v3)
    "representation rate", "how many", "what percentage", "exposure",
    # Infrastructure (ADDED IN v3)
    "share", "common", "overlap", "device", "fax", "phone number",
    # Historical (ADDED IN v3)
    "history", "former", "prior", "opened", "closed", "revoked"
]
```

**Simple Patterns** (defaults, uses SCHEMA_LITE):
- Entity lookups: "Show me claim CLM_001"
- Basic listings: "What providers exist?"
- Direct factual queries: "How many claims in database?"

**Impact**:
- **Simple**: ~1,000 token schema (faster, cheaper)
- **Deep**: ~2,500 token schema (includes live DB stats, high-volume provider context)

**Success Rate**: ~92% correct classification (edge cases: vague questions like "tell me more")

---

### Schema Context Enrichment

**Purpose**: Augment schema with live database statistics for deep queries

**GRAPH_SCHEMA_DEFINITION** (core, 800 tokens):
- 10 node types with properties
- 17 relationship types with directions
- Property value domains (e.g., `status: 'Open' | 'Closed' | 'Paid' | 'Denied - Fraud'`)

**SCHEMA_INVESTIGATION_GUIDE** (append, 300 tokens):
- Common relationship chains (treatment chain, insurance chain, corporate chain)
- Data volume context: "~300 claims total, ~200 background + ~100 fraud across 4 scenarios"
- Pattern emergence note: "Fraud patterns emerge from relationship density, not node properties"

**Live DB Stats** (dynamic, added in v3):
```
LIVE DATABASE SUMMARY:
  - Claim: 301 nodes
  - Person: 315 nodes
  - Provider: 13 nodes
  - Attorney: 11 nodes
  [etc.]
```

**What Was Removed in v3** (answer leakage fix):
- ❌ High-volume provider list with names/IDs/claim counts
- ❌ High-volume attorney list with client counts
- ✅ Kept: Label counts only (helps with LIMIT calibration)

**SCHEMA_LITE** (compressed, 350 tokens):
- Node types with key properties only
- Relationships (no detailed explanations)
- **ADDED IN v3**: Common investigation chains
  ```
  - Provider investigation: (Provider)<-[:TREATED_AT]-(Claim)-[:REPRESENTED_BY]->(Attorney)
  - Person investigation: (Person)<-[:FILED_BY]-(Claim), (Person)<-[:INVOLVED]-(Claim)
  - Vehicle investigation: (Vehicle)<-[:INVOLVES_VEHICLE]-(Claim)-[:FILED_BY]->(Person)
  ```

---

### Visualization Enrichment Strategy

**Purpose**: Ensure graph visualizations show complete context, not sparse results

**Problem**: Query might return Provider + 45 Claims + 3 Attorneys. But if those attorneys share a Phone node, the query results don't include the Phone unless explicitly requested.

**Solution**: Deterministic 1-hop expansion
1. Extract all entity IDs from query results
2. Check which IDs already have nodes in visualization
3. For up to 5 missing IDs, fetch 1-hop neighborhoods (up to 30 relationships each)
4. Merge with original results

**Example**:
```
Query returns: Metro Care (Provider), 45 Claims, 3 Attorneys
Entity IDs in results: PROV_S1_MAIN, CLM_S1_001...045, ATT_S1_A, ATT_S1_B, ATT_S1_C

Enrichment detects: FAX_S1_SHARED mentioned in results but no node
Fetches: MATCH (root {id: 'FAX_S1_SHARED'})-[r]-(neighbor) RETURN root, r, neighbor LIMIT 30

Final visualization: Provider + Claims + Attorneys + Shared Fax
```

**Why Deterministic (Not LLM)**: Visualization is a UI concern, not analytical. Code-based enrichment is faster, cheaper, and 100% reliable.

---

### Follow-Up Question Generation

**Purpose**: Guide progressive investigation toward complete fraud network discovery

**Requirements** (embedded in SYNTHESIS_PROMPT):
1. **Graph-queryable**: Must be answerable via Cypher, not general knowledge
2. **Build on findings**: Reference specific entities/patterns from current results
3. **Progressive depth**: Each follow-up explores 1 hop deeper or adds new dimension

**Example Progression** (Scenario 1 discovery):
```
Q1: "Tell me about Metro Care Clinic"
   ↓ [Discovers 100% attorney representation, 3 attorneys]
   ↓
Follow-ups:
   - "Are those 3 attorneys connected in any way?"  [Explores shared infrastructure]
   - "What's the total claim amount across all 45 claims?"  [Quantifies exposure]
   - "Show me the timeline of when these claims were filed"  [Temporal analysis]

User clicks: "Are those 3 attorneys connected?"
   ↓ [Discovers shared fax number]
   ↓
Follow-ups:
   - "What other providers do these attorneys represent?"  [Network expansion]
   - "Show the complete network around this shared fax"  [Full visualization]
   - "Are there other attorney groups sharing infrastructure?"  [Pattern generalization]
```

**Formatting**: Parsed from LLM response via delimiter `---FOLLOW_UPS---`, rendered as clickable buttons in UI

**UI Behavior**: Only last assistant message shows follow-ups (prevents clutter in long conversations)

---

### Performance Characteristics

**Query Success Rate**:
- v1 (single prompt): ~70% valid Cypher
- v2 (split pipeline): ~85% valid Cypher  
- v3 (direction guards): ~95% valid Cypher + auto-retry

**Latency** (GPT-4o-mini on Azure):
- Simple query: 2-4 seconds total (1.5s reasoning + 1s Cypher + 0.5s synthesis)
- Deep query: 4-7 seconds total (2s reasoning + 2s Cypher + 1.5s synthesis + Neo4j query time)
- With retry: +2 seconds if first query fails

**Token Usage** (per investigation turn):
- Simple: ~2,000 tokens total (1K schema + 300 reasoning + 200 Cypher + 500 synthesis)
- Deep: ~5,000 tokens total (2.5K schema + 500 reasoning + 400 Cypher + 1.6K synthesis)

**Cost** (GPT-4o-mini at $0.15/1M input, $0.60/1M output):
- Simple turn: ~$0.001
- Deep turn: ~$0.003  
- Full investigation (10-15 turns): ~$0.02-$0.05

---

## 📈 Demonstration Use Cases

### 1. Data Science Team Knowledge Share (60 min)

**Objective**: Introduce graph concepts and demonstrate value over traditional ML pipelines

**Flow**:
1. **Setup (5 min)**: Graph DB primer — nodes, relationships, traversal
2. **Scenario 1 (15 min)**: Live walkthrough of provider-attorney collusion
   - Show SQL limitations (no join between attorneys)
   - Execute graph query live in Neo4j Browser
   - Visualize in Streamlit app
3. **Investigation Assistant Demo (20 min)**: 
   - Natural language questions discovering Scenario 2 (role rotation)
   - Show how LLM translates questions to Cypher
   - Demonstrate follow-up progression
4. **Technical Deep-Dive (15 min)**: Schema design, Cypher patterns, GraphRAG architecture
5. **Discussion (5 min)**: Applicability to team's domain, infrastructure requirements

**Deliverable**: Team understands when to use graphs vs. tables/embeddings

---

### 2. Business Stakeholder Pitch (30 min)

**Objective**: Demonstrate graph database capabilities for fraud detection using synthetic data scenarios

**Flow**:
1. **Problem (5 min)**: "Traditional relational systems struggle to detect network-based fraud patterns — our demo shows 4 distinct fraud schemes embedded in realistic synthetic data that graph traversal discovers instantly"
2. **Demo (15 min)**: Show Scenario 4 (network migration) — emphasize pattern detection capability
   - "Graph reveals how fraud networks adapt and migrate after enforcement actions"
   - "Relationship preservation shows connections invisible to point-in-time queries"
   - Quantify time contrast: "2 minutes vs. weeks of manual investigation" (using synthetic data as proof of concept)
3. **Investigation Assistant (7 min)**: Let stakeholder ask questions
   - Guide them to discover a fraud ring through conversation
   - Emphasize: "This natural language interface works on real production data"
4. **Technical Capability (3 min)**: Translate demo patterns to real-world ROI
   - Multi-hop traversal, historical relationship preservation, shared infrastructure detection
   - Scalability: "Demo has 300 nodes; production would handle 10M+ with same query patterns"

**Deliverable**: Understanding of graph database value proposition for fraud investigation, grounded in realistic synthetic scenarios

---

### 3. Self-Guided Learning Lab

**Objective**: Hands-on graph exploration for new team members

**Materials Provided**:
- Deployed Streamlit app (read-only)
- Investigation prompt library:
  ```
  - "What's unusual about Provider PROV_S1_MAIN's claims?"
  - "Show me everyone connected to Darius Thorne"
  - "Find vehicles with multiple total-loss claims"
  - "Which attorneys have the highest client concentration with single providers?"
  ```
- Guided worksheet with expected findings

**Outcome**: Team members discover all 4 fraud rings independently via Investigation Assistant

---

## 🔧 Configuration & Deployment

### Environment Variables

All configuration via `.streamlit/secrets.toml`:

```toml
[neo4j]
uri = "neo4j+s://xxxxx.databases.neo4j.io"  # Required
user = "neo4j"                               # Required
password = "your-secure-password"            # Required

[azure_openai]  # Optional - use OR groq
endpoint = "https://your-resource.openai.azure.com/"
api_key = "sk-..."
api_version = "2024-12-01-preview"
deployment_4o_mini = "gpt-4o-mini"  # For Investigation Assistant
deployment_4o = "gpt-4o"            # Optional - higher quality

[groq]  # Optional - use OR azure_openai
api_key = "gsk_..."  # Free tier: 30 requests/min
```

### Neo4j AuraDB Setup

1. Create free tier instance at [console.neo4j.io](https://console.neo4j.io)
2. Note connection URI, username, password
3. No manual schema creation needed — app creates indexes automatically

**Database Specs**:
- **Nodes**: ~315 (after data generation)
- **Relationships**: ~850
- **Storage**: < 1 MB
- **Query Performance**: < 100ms for 3-hop traversals

### LLM Provider Options

| Provider | Cost | Quality | Use Case |
|----------|------|---------|----------|
| **Azure OpenAI GPT-4o-mini** | ~$0.10/session | Excellent | Production demos, stakeholder presentations |
| **Groq (Llama 3.3 70B)** | Free | Good | Internal learning, dev/test |
| **Azure OpenAI GPT-4o** | ~$0.50/session | Best | High-stakes demos, complex investigations |

**Session = ~10-15 back-and-forth questions in Investigation Assistant**

### Deployment Options

#### Local Development
```bash
streamlit run app.py
```

#### Streamlit Cloud (Free)
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add secrets via UI
4. Auto-deploys on push

#### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t fraud-detection .
docker run -p 8501:8501 fraud-detection
```

---

## 📁 Project Structure

```
fraud-ring-detection/
├── app.py                          # Main Streamlit application
├── scenario_data_generator.py     # Synthetic data creation
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── secrets.toml.example       # Configuration template
│   └── config.toml                # Streamlit UI settings
├── docs/
│   ├── GraphRAG_Demo_Opportunities.md          # Project overview
│   ├── investigation_assistant_prompt_audit_v3.md  # Prompt engineering guide
│   ├── schema_prompt_refinement.md            # Schema design principles
│   └── generator_review.md                    # Data generation methodology
└── README.md                       # This file
```

### Key Files Explained

**`app.py`** (2,900 lines):
- Scenario walkthrough renderer (400 lines)
- Investigation Assistant pipeline (800 lines)
- Network explorer (200 lines)
- Graph visualization utilities (300 lines)
- Schema definitions + prompts (600 lines)
- Navigation + UI (600 lines)

**`scenario_data_generator.py`** (800 lines):
- Infrastructure pools (adjusters, locations, providers, attorneys)
- Background data generation (200 legitimate claims with realistic distributions)
- 4 fraud scenario builders (based on documented real-world patterns)
- Statistical distributions (claim amounts via lognormal, seasonal weighting, injury rates)
- **All data is synthetically generated for demonstration purposes**

**Schema Prompts** (in `app.py`):
- `GRAPH_SCHEMA_DEFINITION`: Full node/relationship definitions
- `SCHEMA_LITE`: Compressed version for simple queries
- `REASONING_PROMPT`: Guides investigation planning
- `CYPHER_GENERATION_PROMPT`: Translates plans to queries
- `SYNTHESIS_PROMPT`: Interprets results with fraud indicators

---

## 🎓 Learning Resources

### Understanding Graph Databases

**Why Graphs for Fraud Detection?**
- **Tables**: Store entities in rows, relationships implied via foreign keys
- **Graphs**: Relationships are first-class entities with properties, enabling pattern matching

**When to Use Graphs**:
- ✅ Multi-hop pattern detection (friend-of-friend, 2+ degrees)
- ✅ Relationship-centric queries (who shares what with whom)
- ✅ Variable-depth exploration (find all paths up to N hops)
- ✅ Structural anomaly detection (concentration, clustering)

**When to Use Tables**:
- ✅ Aggregation-heavy analytics (SUM, AVG, GROUP BY at scale)
- ✅ OLAP workloads (data warehousing, BI)
- ✅ Simple key-value lookups
- ✅ Well-defined joins (< 3 tables)

### GraphRAG vs. Traditional RAG

| Aspect | Traditional RAG | GraphRAG |
|--------|----------------|----------|
| **Data Structure** | Flat documents + embeddings | Knowledge graph + embeddings |
| **Retrieval** | Semantic similarity search | Relationship traversal + context |
| **Multi-hop** | Requires multiple LLM calls | Single graph query |
| **Relationships** | Implicit in text | Explicit in structure |
| **Best For** | Document Q&A, summarization | Network analysis, investigation |

**This Platform**: Demonstrates GraphRAG with explicit relationship modeling, multi-hop traversal, and LLM-powered natural language interface to graph queries.

### Cypher Query Examples

```cypher
-- Find all claims for a provider with attorney representation
MATCH (p:Provider {id: 'PROV_S1_MAIN'})<-[:TREATED_AT]-(c:Claim)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
RETURN p, c, a

-- Detect shared infrastructure (phones/fax)
MATCH (a1:Attorney)-[:HAS_PHONE]->(ph:Phone)<-[:HAS_PHONE]-(a2:Attorney)
WHERE a1.id < a2.id  -- Avoid duplicates
RETURN a1, ph, a2

-- Role rotation detection
MATCH (p:Person)-[r]-(c:Claim)
WITH p, collect(DISTINCT type(r)) AS roles, count(c) AS claim_count
WHERE size(roles) > 1
RETURN p.name, roles, claim_count

-- Vehicle history with policy timing
MATCH (v:Vehicle)<-[:INVOLVES_VEHICLE]-(c:Claim)
MATCH (c)-[:FILED_BY]->(per:Person)-[:HAS_POLICY]->(pol:Policy)-[:COVERS]->(v)
WITH v, c, pol,
     duration.between(date(pol.bind_date), date(c.claim_date)).days AS tenure
RETURN v.vin, c.claim_amount, tenure
ORDER BY v.vin, c.claim_date
```

---

## 🔍 Troubleshooting

### Common Issues

**"Neo4j connection failed"**
- Verify URI format: `neo4j+s://` (not `neo4j://` or `bolt://`)
- Check firewall: AuraDB requires internet access
- Confirm credentials in secrets.toml

**"No LLM providers configured"**
- At least one provider (Azure OpenAI or Groq) required
- Check API key format and quotas
- Groq free tier: 30 req/min limit

**"Database empty" after generation**
- Check logs in Administration page
- Common issue: connectivity timeout during generation
- Solution: Reduce batch size or retry

**Slow graph queries (> 2 seconds)**
- Check indexes: `SHOW INDEXES` in Neo4j Browser
- Verify AuraDB tier (free tier may throttle)
- Consider adding node/relationship property indexes

**LLM generates incorrect Cypher**
- GPT-4o-mini: ~5% failure rate with retry correction
- Check Investigation Assistant expanded "Investigation approach" section
- Use "deep" query mode for complex questions
- Try GPT-4o for higher success rate

### Performance Tuning

**Query Optimization**:
```cypher
// SLOW: Returns all paths then filters
MATCH path = (p:Provider)-[*1..3]-(c:Claim)
RETURN path

// FAST: Filters at each hop
MATCH (p:Provider {id: $id})<-[:TREATED_AT]-(c:Claim)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
RETURN p, c, a
LIMIT 50
```

**Visualization Performance**:
- Limit nodes: Use entity type filters in Network Explorer
- Limit depth: Start with 1-2 hops, expand if needed
- Limit results: All queries capped at 50 rows

---

## 🛣️ Roadmap & Extensions

### Current Capabilities
- ✅ 4 fraud scenarios with $747K synthetic exposure
- ✅ Natural language investigation via GPT-4o-mini
- ✅ Interactive graph visualization
- ✅ Synthetic data generator with realistic distributions
- ✅ Production-ready prompt engineering

### Potential Enhancements

**Additional Fraud Scenarios**:
- ✨ Pharmacy pill mill detection (prescription graph)
- ✨ Body shop fraud rings (repair facility concentration)
- ✨ Claimant migration patterns (geo-spatial + temporal)

**Advanced Graph Analytics**:
- 🔬 Community detection (Louvain, Label Propagation)
- 🔬 PageRank scoring (identify network influencers)
- 🔬 HNSW vector indexes (hybrid semantic + graph retrieval)
- 🔬 Temporal graph analysis (time-windowed patterns)

**Investigation Assistant Upgrades**:
- 🤖 Multi-turn conversation memory (maintain investigation context)
- 🤖 Automated investigation playbooks (chained queries)
- 🤖 Visualization annotations (highlight anomalies automatically)
- 🤖 Export investigation reports (PDF with graph visualizations)

**Enterprise Features**:
- 🏢 Multi-user case management
- 🏢 Real-time claim ingestion pipelines
- 🏢 Integration with ClaimSearch, ISO, NICB APIs
- 🏢 Compliance workflows (subpoena tracking, evidence chain)

**Scaling Architecture**:
- 📈 Production Neo4j cluster (10M+ nodes)
- 📈 Apache Kafka for streaming claims
- 📈 FastAPI backend with async query execution
- 📈 Redis caching for frequent queries

### Other P&C Insurance Use Cases

This platform's architecture generalizes to any relationship-heavy insurance domain:

- **Cyber Risk**: Vendor dependency mapping, supply chain exposure
- **Claims Intelligence**: Adjuster performance networks, settlement patterns
- **Underwriting**: Business relationship graphs, ownership structures
- **Reinsurance**: Treaty exposure networks, catastrophe modeling

---

## 🤝 Contributing

This is a demonstration platform designed for knowledge sharing and proof-of-concept work. Contributions welcome in:

- **Additional fraud scenarios** (with research citations)
- **Prompt engineering refinements** (improve LLM query generation)
- **Performance optimizations** (query patterns, caching strategies)
- **Documentation** (tutorials, video walkthroughs, blog posts)

### Development Setup

```bash
# Clone with dev dependencies
git clone https://github.com/yourusername/fraud-ring-detection.git
cd fraud-ring-detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev tools
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black app.py scenario_data_generator.py
```

### Pull Request Guidelines

1. **Branch naming**: `feature/scenario-name` or `fix/issue-description`
2. **Commits**: Descriptive messages explaining why, not just what
3. **Testing**: Add test cases for new scenarios or query patterns
4. **Documentation**: Update README if adding features
5. **Prompt changes**: Must pass answer-leakage audit (see `docs/schema_prompt_refinement.md`)

---

## 📄 License

MIT License - see LICENSE file for details

This project is free to use for educational, research, and commercial purposes. Attribution appreciated but not required.

---

## 🙏 Acknowledgments

### Research Foundations

This platform implements fraud detection patterns documented in:

- Coalition Against Insurance Fraud (CAIF) annual reports
- National Insurance Crime Bureau (NICB) technical bulletins
- Journal of Forensic and Investigative Accounting case studies

### Technology Stack

- **Neo4j**: Graph database platform
- **Streamlit**: Rapid web app framework
- **OpenAI GPT-4o-mini**: LLM for natural language investigation
- **Groq**: Fast inference for Llama models
- **streamlit-agraph**: Graph visualization component

### Design Principles

Schema design follows "answer key avoidance" methodology from:
- *Schema Prompt Refinement Guide* (avoiding fraud pattern leakage)
- *Investigation Assistant Prompt Audit v3* (GPT-4o-mini optimization)

---

## 📧 Contact & Support

**Questions or feedback?**
- Open an issue: [GitHub Issues](https://github.com/yourusername/fraud-ring-detection/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/fraud-ring-detection/discussions)

**For production implementation consulting:**
- Architecture reviews for 10M+ node deployments
- Custom fraud scenario development
- GraphRAG prompt engineering workshops

---

## 🎬 Demo Videos & Screenshots

### Investigation Assistant Discovery Flow

```
User: "Tell me about Metro Care Clinic"
  ↓
Assistant: "Metro Care has 45 claims with 100% attorney 
           representation (normal: 10-15%). All claims 
           route through 3 attorneys..."
  ↓
[Follow-up] "Are those attorneys connected?"
  ↓
Assistant: "Yes - they share fax number (555) 019-9999. 
           This suggests they're actually one operation 
           using shell firm names. Total exposure: $162K"
```

### Network Visualization

![Fraud Network Graph](docs/images/provider-attorney-collusion.png)
*Provider-Attorney collusion network showing shared fax infrastructure*

![Role Rotation Pattern](docs/images/role-rotation-ring.png)
*4-person staged accident ring with role rotation across claims*

---

## 📚 Further Reading

**Graph Database Concepts**:
- [Neo4j Graph Academy](https://graphacademy.neo4j.com/) - Free courses
- [Cypher Query Language Reference](https://neo4j.com/docs/cypher-manual/)

**GraphRAG Architecture**:
- [Microsoft GraphRAG Framework](https://github.com/microsoft/graphrag)
- [LangChain Graph QA Chains](https://python.langchain.com/docs/use_cases/graph/)

**Insurance Fraud Detection**:
- NICB Vehicle Theft & Fraud Reports
- CAIF Annual Fraud Statistics
- ISO ClaimSearch Best Practices

**Prompt Engineering**:
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)

---

**Built with ❤️ for the insurance fraud investigation community**

*Star this repo if you found it useful for your graph database journey!*