"""
Insurance Fraud Scenario Data Generator
========================================

Generates research-grounded fraud scenarios for demonstrating graph DB advantages:

1. "Spider Web" - Provider-Attorney Collusion via Shared Fax (45 claims)
2. "Role Chameleon" - Crash-for-Cash Ring with Role Rotation (4 claims)
3. "Immortal Asset" - Vehicle Recycling & Policy Hopping (3 claims)
4. "Network Migration" - Post-Prosecution Network Evolution (49 claims)

Plus ~200 background claims to create a realistic "haystack"

Total exposure: ~$747,000+ in fraud scenarios

Version: 3.0 - Refined per scenario_schema_audit.md and schema_prompt_refinement.md
  - Replaced :Entity with :Phone {type:'Fax'}, SHARES_DEVICE with HAS_PHONE
  - Replaced INSURES_VEHICLE with COVERS
  - Added Insurer node, UNDER_POLICY, INSURED_BY relationships
  - Added Vehicle + Policy to background claims
  - Removed explicit fraud markers (scenario, total_loss_count, fraud_confirmed, etc.)
  - Added missing properties: npi, bar_number, policy_number, claim_type, phone.type
  - Uses single :Person label (no :Claimant or :Adjuster dual labels)
"""

import random
import time
from datetime import datetime, timedelta
from neo4j import GraphDatabase, exceptions

# Try to import streamlit for secrets, fall back to env vars
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    import os


class ScenarioDataGenerator:
    """Generate fraud detection demo data for Neo4j graph database."""
    
    def __init__(self, uri=None, user=None, password=None):
        """Initialize generator with Neo4j connection."""
        try:
            # Get credentials from Streamlit secrets or parameters
            if uri and user and password:
                pass  # Use provided credentials
            elif HAS_STREAMLIT and hasattr(st, "secrets"):
                uri = st.secrets["neo4j"]["uri"]
                user = st.secrets["neo4j"]["user"]
                password = st.secrets["neo4j"]["password"]
            else:
                # Fall back to environment variables
                uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
                user = os.getenv('NEO4J_USERNAME', 'neo4j')
                password = os.getenv('NEO4J_PASSWORD', 'password')
            
            self.driver = GraphDatabase.driver(
                uri, 
                auth=(user, password),
                max_connection_lifetime=200
            )
            self.driver.verify_connectivity()
            print(f"✅ Connected to Neo4j at {uri}")
            
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise e
        
        # Initialize counters and pools
        self.counters = {}
        self.adjuster_pool = []
        self.background_providers = []
        self.background_attorneys = []
        self.background_locations = []
        self.insurer_id = "INS_001"
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'driver'):
            self.driver.close()
            print("Connection closed.")
    
    def _run_query(self, query, **kwargs):
        """Execute a Cypher query with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.driver.session() as session:
                    session.run(query, **kwargs)
                return
            except exceptions.ServiceUnavailable:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise
            except Exception as e:
                print(f"Query failed: {e}")
                raise e
    
    def _get_id(self, prefix):
        """Generate unique IDs with counters."""
        key = prefix.split('_')[0]
        if key not in self.counters:
            self.counters[key] = 0
        self.counters[key] += 1
        return f"{prefix}_{self.counters[key]:05d}"
    
    def _generate_npi(self):
        """Generate a realistic 10-digit NPI number."""
        return f"{random.randint(1000000000, 9999999999)}"
    
    def _generate_bar_number(self):
        """Generate a realistic state bar number."""
        states = ['GA', 'FL', 'TX', 'CA', 'NY', 'IL', 'PA', 'OH']
        return f"{random.choice(states)}-{random.randint(2005, 2023)}-{random.randint(10000, 99999)}"
    
    def _generate_policy_number(self):
        """Generate a policy number in PA-XXXXXX format."""
        return f"PA-{random.randint(100000, 999999)}"
    
    def _generate_vin(self):
        """Generate a realistic-looking VIN."""
        chars = '0123456789ABCDEFGHJKLMNPRSTUVWXYZ'
        return ''.join(random.choice(chars) for _ in range(17))
    
    def clear_database(self):
        """Remove all nodes and relationships."""
        print("🗑️ Clearing existing data...")
        self._run_query("MATCH (n) DETACH DELETE n")
    
    def create_indexes(self):
        """Create indexes for better query performance."""
        print("📇 Creating indexes...")
        indexes = [
            "CREATE INDEX claim_id IF NOT EXISTS FOR (c:Claim) ON (c.id)",
            "CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id)",
            "CREATE INDEX provider_id IF NOT EXISTS FOR (p:Provider) ON (p.id)",
            "CREATE INDEX vehicle_id IF NOT EXISTS FOR (v:Vehicle) ON (v.id)",
            "CREATE INDEX attorney_id IF NOT EXISTS FOR (a:Attorney) ON (a.id)",
            "CREATE INDEX address_id IF NOT EXISTS FOR (a:Address) ON (a.id)",
            "CREATE INDEX phone_id IF NOT EXISTS FOR (p:Phone) ON (p.id)",
            "CREATE INDEX location_id IF NOT EXISTS FOR (l:Location) ON (l.id)",
            "CREATE INDEX policy_id IF NOT EXISTS FOR (p:Policy) ON (p.id)",
            "CREATE INDEX insurer_id IF NOT EXISTS FOR (i:Insurer) ON (i.id)",
        ]
        with self.driver.session() as session:
            for idx in indexes:
                try:
                    session.run(idx)
                except Exception:
                    pass  # Index may already exist
    
    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================
    
    def generate_name(self):
        """Generate a realistic name."""
        first = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", 
                 "Michael", "Linda", "David", "Sarah", "William", "Elizabeth",
                 "Richard", "Barbara", "Joseph", "Susan", "Thomas", "Jessica",
                 "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
                 "Anthony", "Margaret", "Mark", "Betty", "Donald", "Sandra"]
        last = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", 
                "Miller", "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor",
                "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson",
                "White", "Lopez", "Lee", "Gonzalez", "Harris", "Clark", "Lewis"]
        return f"{random.choice(first)} {random.choice(last)}"
    
    def generate_date(self, days_ago_start=365, days_ago_end=30):
        """Generate a random date within a range."""
        days = random.randint(days_ago_end, days_ago_start)
        return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    def generate_phone(self):
        """Generate a phone number."""
        return f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    def generate_address(self):
        """Generate a street address."""
        streets = ['Oak', 'Main', 'Pine', 'Cedar', 'Maple', 'Elm', 'Park', 
                   'Lake', 'Hill', 'River', 'Forest', 'Valley']
        types = ['St', 'Ave', 'Rd', 'Blvd', 'Dr', 'Ln', 'Way', 'Ct']
        return f"{random.randint(100, 9999)} {random.choice(streets)} {random.choice(types)}"
    
    def _generate_vehicle_data(self):
        """Generate random vehicle properties."""
        makes_models = [
            ("Toyota", "Camry"), ("Honda", "Civic"), ("Ford", "F-150"),
            ("Chevrolet", "Malibu"), ("Nissan", "Altima"), ("Hyundai", "Sonata"),
            ("Kia", "Optima"), ("Subaru", "Outback"), ("Mazda", "CX-5"),
            ("Volkswagen", "Jetta"), ("Toyota", "RAV4"), ("Honda", "CR-V"),
            ("Ford", "Escape"), ("Chevrolet", "Equinox"), ("Jeep", "Cherokee"),
        ]
        make, model = random.choice(makes_models)
        colors = ["White", "Black", "Silver", "Gray", "Blue", "Red", "Green"]
        year = random.randint(2015, 2024)
        value = random.randint(8000, 45000)
        return make, model, year, random.choice(colors), value
    
    # =========================================================================
    # INFRASTRUCTURE POOLS
    # =========================================================================
    
    def create_infrastructure_pools(self):
        """Create shared infrastructure: insurer, adjusters, locations, providers, attorneys."""
        print("🏗️ Creating infrastructure...")
        
        # 0. Insurer (carrier node)
        self._run_query(
            "CREATE (:Insurer {id: $id, name: $name})",
            id=self.insurer_id, name='Peach State Mutual Insurance'
        )
        
        # 1. Adjusters (10) — single :Person label with role property
        for i in range(10):
            adj_id = self._get_id("ADJ")
            self.adjuster_pool.append(adj_id)
            self._run_query(
                "CREATE (:Person {id: $id, name: $name, role: 'Adjuster'})",
                id=adj_id, name=self.generate_name()
            )
        
        # 2. Accident Locations (8)
        locations = [
            ("Main St & 1st Ave", "Urban Intersection", "Downtown"),
            ("I-85 Exit 40", "Highway", "Metro Area"),
            ("Oak Ave & Elm St", "Suburban", "Residential"),
            ("Highway 400 N", "Highway", "North Corridor"),
            ("Downtown Connector", "Urban Highway", "City Center"),
            ("Mall Parking Lot", "Parking Lot", "Commercial"),
            ("Industrial Blvd", "Industrial", "Business Park"),
            ("School Zone - Pine St", "School Zone", "Residential")
        ]
        for name, loc_type, area in locations:
            loc_id = self._get_id("LOC")
            self.background_locations.append(loc_id)
            self._run_query(
                "CREATE (:Location {id: $id, name: $name, type: $type, area: $area})",
                id=loc_id, name=name, type=loc_type, area=area
            )
        
        # 3. Background Providers (12) - legitimate clinics
        provider_names = [
            ("City General Hospital", "Hospital", "Emergency"),
            ("Northside Medical Center", "Medical Center", "General"),
            ("Valley Health Clinic", "Clinic", "Family Practice"),
            ("Regional Orthopedics", "Specialist", "Orthopedics"),
            ("Metro Emergency Care", "Urgent Care", "Emergency"),
            ("Suburban Family Practice", "Clinic", "Family Practice"),
            ("Downtown Urgent Care", "Urgent Care", "Walk-in"),
            ("Eastside Physical Therapy", "Rehab", "Physical Therapy"),
            ("Westview Imaging", "Diagnostic", "Radiology"),
            ("Central Spine Institute", "Specialist", "Spine"),
            ("Lakeside Medical Group", "Medical Center", "Multi-specialty"),
            ("Hillcrest Diagnostics", "Diagnostic", "Laboratory")
        ]
        for name, prov_type, specialty in provider_names:
            prov_id = self._get_id("PROV_BG")
            self.background_providers.append(prov_id)
            self._run_query(
                """CREATE (:Provider {
                    id: $id, name: $name, type: $type, 
                    specialty: $specialty, status: 'Active',
                    npi: $npi
                })""",
                id=prov_id, name=name, type=prov_type, specialty=specialty,
                npi=self._generate_npi()
            )
        
        # 4. Background Attorneys (8) - legitimate firms
        for i in range(8):
            att_id = self._get_id("ATT_BG")
            self.background_attorneys.append(att_id)
            name = self.generate_name()
            self._run_query(
                """CREATE (:Attorney {
                    id: $id, name: $name, 
                    firm_type: 'Independent', status: 'Active',
                    bar_number: $bar
                })""",
                id=att_id, name=f"Law Office of {name}",
                bar=self._generate_bar_number()
            )
        
        print(f"   Created: 1 insurer, {len(self.adjuster_pool)} adjusters, {len(self.background_locations)} locations")
        print(f"   Created: {len(self.background_providers)} providers, {len(self.background_attorneys)} attorneys")
    
    # =========================================================================
    # BACKGROUND DATA (THE HAYSTACK)
    # =========================================================================
    
    def create_background_data(self, count=200):
        """Generate legitimate background claims with full connection chains."""
        print(f"📋 Generating {count} background claims...")
        
        for i in range(count):
            clm_id = self._get_id("CLM_BG")
            p_id = self._get_id("P_BG")
            veh_id = self._get_id("VEH_BG")
            pol_id = self._get_id("POL_BG")
            
            prov = random.choice(self.background_providers)
            adj = random.choice(self.adjuster_pool)
            loc = random.choice(self.background_locations)
            
            # Determine if bodily injury (30%) or property damage only (70%)
            is_injury = random.random() < 0.30
            
            # Right-skewed claim amounts
            if is_injury:
                # Injury claims: $5,000 - $25,000, skewed right
                amount = int(random.lognormvariate(9.2, 0.4))
                amount = max(5000, min(25000, amount))
                claim_type = 'Bodily Injury'
            else:
                # Property damage only: $1,000 - $8,000, skewed right
                amount = int(random.lognormvariate(7.8, 0.5))
                amount = max(1000, min(8000, amount))
                claim_type = 'Property Damage Only'
            
            incident_types = [
                'Standard Collision', 'Rear-End', 'Parking Lot Incident',
                'Single Vehicle', 'Weather-Related', 'Minor Impact'
            ]
            
            # Generate vehicle data
            make, model, year, color, value = self._generate_vehicle_data()
            
            # Generate dates
            claim_date = self.generate_date()
            bind_days_before = random.randint(60, 730)
            bind_date = (datetime.strptime(claim_date, "%Y-%m-%d") - timedelta(days=bind_days_before)).strftime("%Y-%m-%d")
            
            query = """
                CREATE (c:Claim {
                    id: $cid, 
                    claim_amount: $amt, 
                    claim_date: $date, 
                    incident_type: $incident, 
                    status: 'Closed',
                    claim_type: $claim_type
                })
                CREATE (p:Person {id: $pid, name: $pname, role: 'Claimant'})
                CREATE (ph:Phone {id: 'PH_' + $pid, number: $phone, type: 'Mobile'})
                CREATE (addr:Address {id: 'ADDR_' + $pid, street: $street, city: 'Atlanta', state: 'GA', zip: $zip})
                CREATE (v:Vehicle {id: $vid, vin: $vin, make: $make, model: $model, year: $year, color: $color, value: $vvalue})
                CREATE (pol:Policy {id: $polid, policy_number: $polnum, bind_date: $bind_date, premium: $premium, coverage_type: 'Auto'})
                
                CREATE (c)-[:FILED_BY]->(p)
                CREATE (p)-[:HAS_PHONE]->(ph)
                CREATE (p)-[:LIVES_AT]->(addr)
                CREATE (p)-[:HAS_POLICY]->(pol)
                CREATE (pol)-[:COVERS]->(v)
                CREATE (c)-[:INVOLVES_VEHICLE]->(v)
                CREATE (c)-[:UNDER_POLICY]->(pol)
                
                WITH c, pol
                MATCH (ins:Insurer {id: $ins_id})
                CREATE (pol)-[:INSURED_BY]->(ins)
                
                WITH c
                MATCH (ad:Person {id: $adj}) 
                CREATE (c)-[:HANDLED_BY]->(ad)
                
                WITH c
                MATCH (lo:Location {id: $loc}) 
                CREATE (c)-[:OCCURRED_AT]->(lo)
            """
            
            # Injury claims get provider
            if is_injury:
                query += f"""
                    WITH c
                    MATCH (pr:Provider {{id: '{prov}'}}) 
                    CREATE (c)-[:TREATED_AT]->(pr)
                """
            
            # 15% attorney representation (normal rate)
            if random.random() < 0.15:
                att = random.choice(self.background_attorneys)
                query += f"""
                    WITH c 
                    MATCH (at:Attorney {{id: '{att}'}}) 
                    CREATE (c)-[:REPRESENTED_BY {{hours_to_retain: {random.randint(48, 168)}}}]->(at)
                """
            
            self._run_query(
                query,
                cid=clm_id,
                pid=p_id,
                vid=veh_id,
                polid=pol_id,
                polnum=self._generate_policy_number(),
                amt=amount,
                date=claim_date,
                bind_date=bind_date,
                premium=random.randint(800, 3200),
                incident=random.choice(incident_types),
                claim_type=claim_type,
                pname=self.generate_name(),
                phone=self.generate_phone(),
                street=self.generate_address(),
                zip=f"3{random.randint(0, 9)}{random.randint(100, 999)}",
                vin=self._generate_vin(),
                make=make,
                model=model,
                year=year,
                color=color,
                vvalue=value,
                ins_id=self.insurer_id,
                adj=adj,
                loc=loc
            )
        
        print(f"   ✓ Created {count} legitimate background claims (with vehicles, policies, insurer)")
    
    # =========================================================================
    # SCENARIO 1: SPIDER WEB (Provider-Attorney Collusion)
    # =========================================================================
    
    def create_spider_web(self):
        """
        Provider-Attorney Collusion via Shared Fax/Device
        
        - 45 claims through one suspicious provider
        - 100% attorney representation (vs normal 10-15%)
        - All funneled through 3 "independent" attorneys
        - Hidden link: All 3 attorneys share the same fax number (Phone node)
        - Total exposure: $162,000
        """
        print("🕸️ Creating Scenario 1: Spider Web (Provider-Attorney Collusion)...")
        
        # The suspicious provider
        prov_id = "PROV_S1_MAIN"
        self._run_query("""
            CREATE (:Provider {
                id: $id, 
                name: 'Metro Care Clinic', 
                specialty: 'Pain Management',
                type: 'Clinic',
                status: 'Active',
                npi: $npi
            })
        """, id=prov_id, npi=self._generate_npi())
        
        # The shared fax number — Phone node with type 'Fax'
        fax_id = "FAX_S1_SHARED"
        self._run_query("""
            CREATE (:Phone {
                id: $id, 
                number: '(555) 019-9999', 
                type: 'Fax'
            })
        """, id=fax_id)
        
        # Three "independent" attorneys (actually sharing fax)
        attorneys = [
            ("ATT_S1_A", "Smith & Associates", "Personal Injury"),
            ("ATT_S1_B", "Doe Legal Group", "Auto Accidents"),
            ("ATT_S1_C", "Rapid Legal Services", "Insurance Claims")
        ]
        
        for att_id, name, specialty in attorneys:
            self._run_query("""
                MATCH (fax:Phone {id: $fid})
                CREATE (a:Attorney {
                    id: $id, 
                    name: $name, 
                    specialty: $specialty,
                    status: 'Active',
                    bar_number: $bar
                })
                CREATE (a)-[:HAS_PHONE]->(fax)
            """, fid=fax_id, id=att_id, name=name, specialty=specialty,
                bar=self._generate_bar_number())
        
        # Generate 45 claims (all represented, rotating through 3 attorneys)
        for i in range(45):
            claim_id = f"CLM_S1_{i:03d}"
            person_id = f"P_S1_{i:03d}"
            att_id = attorneys[i % 3][0]
            
            # Claims cluster around $3,600 (20% above $3k peer avg)
            amount = random.randint(3200, 4000)
            
            self._run_query("""
                MATCH (prov:Provider {id: $pid}), (att:Attorney {id: $aid})
                
                CREATE (c:Claim {
                    id: $cid,
                    claim_amount: $amount,
                    claim_date: $date,
                    incident_type: 'Soft Tissue / Whiplash',
                    status: 'Open',
                    claim_type: 'Bodily Injury'
                })
                
                CREATE (person:Person {
                    id: $perid, 
                    name: $pname,
                    role: 'Claimant'
                })
                
                CREATE (c)-[:FILED_BY]->(person)
                CREATE (c)-[:TREATED_AT]->(prov)
                CREATE (c)-[:REPRESENTED_BY {
                    hours_to_retain: $hours
                }]->(att)
            """, 
                pid=prov_id, 
                aid=att_id, 
                cid=claim_id, 
                perid=person_id,
                pname=self.generate_name(),
                amount=amount,
                date=self.generate_date(180, 7),
                hours=random.randint(1, 4)
            )
        
        print("   ✓ Created: 1 provider, 3 attorneys, 1 shared fax (Phone), 45 claims")
        print("   ✓ Total exposure: ~$162,000")
    
    # =========================================================================
    # SCENARIO 2: ROLE CHAMELEON (Staged Accident Ring)
    # =========================================================================
    
    def create_role_chameleon(self):
        """
        Crash-for-Cash Ring with Role Rotation
        
        - 4 individuals rotate through Driver/Passenger/Witness roles
        - 4 claims at the same intersection
        - Connected by "ghost address" from 2+ years ago
        - Total exposure: $120,000
        """
        print("🎭 Creating Scenario 2: Role Chameleon (Staged Accident Ring)...")
        
        # Ghost Address - historical connection point
        ghost_addr_id = "ADDR_S2_GHOST"
        self._run_query("""
            CREATE (:Address {
                id: $id, 
                street: '778 Elm Street, Apt 3B',
                city: 'Atlanta',
                state: 'GA',
                zip: '30301',
                type: 'Residential'
            })
        """, id=ghost_addr_id)
        
        # The 4 ring members
        members = [
            ("P_S2_A", "Darius Thorne", "ADDR_S2_A_CURR", "123 Oak Ave"),
            ("P_S2_B", "Sarah Jenkins", "ADDR_S2_B_CURR", "456 Pine St"),
            ("P_S2_C", "Mike Ross", "ADDR_S2_C_CURR", "789 Cedar Rd"),
            ("P_S2_D", "Lisa Chen", "ADDR_S2_D_CURR", "321 Maple Dr")
        ]
        
        for pid, name, curr_addr_id, curr_street in members:
            self._run_query("""
                CREATE (p:Person {
                    id: $pid, 
                    name: $name
                })
                CREATE (curr_addr:Address {
                    id: $curr_addr_id,
                    street: $curr_street,
                    city: 'Atlanta',
                    state: 'GA'
                })
                CREATE (p)-[:LIVES_AT {status: 'Current'}]->(curr_addr)
                
                WITH p
                MATCH (ghost:Address {id: $ghost_id})
                CREATE (p)-[:LIVES_AT {
                    status: 'Former',
                    date_start: '2022-01-15',
                    date_end: '2022-08-30'
                }]->(ghost)
            """, 
                pid=pid, 
                name=name, 
                curr_addr_id=curr_addr_id,
                curr_street=curr_street,
                ghost_id=ghost_addr_id
            )
        
        # Accident location
        self._run_query("""
            CREATE (:Location {
                id: 'LOC_S2_INTERSECTION',
                name: 'Peachtree & 10th Street',
                type: 'Urban Intersection'
            })
        """)
        
        # CLAIM 1: Darius (Driver) hits Sarah (Passenger), Mike witnesses
        self._run_query("""
            MATCH (darius:Person {id: 'P_S2_A'})
            MATCH (sarah:Person {id: 'P_S2_B'})
            MATCH (mike:Person {id: 'P_S2_C'})
            MATCH (loc:Location {id: 'LOC_S2_INTERSECTION'})
            
            CREATE (c:Claim {
                id: 'CLM_S2_001',
                claim_amount: 28000,
                claim_date: '2024-03-15',
                incident_type: 'Intersection Collision',
                status: 'Paid',
                claim_type: 'Bodily Injury'
            })
            
            CREATE (c)-[:FILED_BY {role: 'Driver'}]->(darius)
            CREATE (c)-[:INVOLVED {role: 'Passenger'}]->(sarah)
            CREATE (c)-[:WITNESSED_BY]->(mike)
            CREATE (c)-[:OCCURRED_AT]->(loc)
        """)
        
        # CLAIM 2: Sarah (Driver) with Lisa (Passenger), Darius witnesses
        self._run_query("""
            MATCH (sarah:Person {id: 'P_S2_B'})
            MATCH (lisa:Person {id: 'P_S2_D'})
            MATCH (darius:Person {id: 'P_S2_A'})
            MATCH (loc:Location {id: 'LOC_S2_INTERSECTION'})
            
            CREATE (c:Claim {
                id: 'CLM_S2_002',
                claim_amount: 32000,
                claim_date: '2024-06-22',
                incident_type: 'Rear-End Collision',
                status: 'Paid',
                claim_type: 'Bodily Injury'
            })
            
            CREATE (c)-[:FILED_BY {role: 'Driver'}]->(sarah)
            CREATE (c)-[:INVOLVED {role: 'Passenger'}]->(lisa)
            CREATE (c)-[:WITNESSED_BY]->(darius)
            CREATE (c)-[:OCCURRED_AT]->(loc)
        """)
        
        # CLAIM 3: Mike (Driver), Darius (Passenger), Lisa witnesses
        self._run_query("""
            MATCH (mike:Person {id: 'P_S2_C'})
            MATCH (darius:Person {id: 'P_S2_A'})
            MATCH (lisa:Person {id: 'P_S2_D'})
            MATCH (loc:Location {id: 'LOC_S2_INTERSECTION'})
            
            CREATE (c:Claim {
                id: 'CLM_S2_003',
                claim_amount: 25000,
                claim_date: '2024-09-10',
                incident_type: 'Side-Impact Collision',
                status: 'Open',
                claim_type: 'Bodily Injury'
            })
            
            CREATE (c)-[:FILED_BY {role: 'Driver'}]->(mike)
            CREATE (c)-[:INVOLVED {role: 'Passenger'}]->(darius)
            CREATE (c)-[:WITNESSED_BY]->(lisa)
            CREATE (c)-[:OCCURRED_AT]->(loc)
        """)
        
        # CLAIM 4: Lisa (Driver), Mike (Passenger), Sarah & Darius witness
        self._run_query("""
            MATCH (lisa:Person {id: 'P_S2_D'})
            MATCH (mike:Person {id: 'P_S2_C'})
            MATCH (sarah:Person {id: 'P_S2_B'})
            MATCH (darius:Person {id: 'P_S2_A'})
            MATCH (loc:Location {id: 'LOC_S2_INTERSECTION'})
            
            CREATE (c:Claim {
                id: 'CLM_S2_004',
                claim_amount: 35000,
                claim_date: '2025-01-05',
                incident_type: 'Intersection Collision',
                status: 'Open',
                claim_type: 'Bodily Injury'
            })
            
            CREATE (c)-[:FILED_BY {role: 'Driver'}]->(lisa)
            CREATE (c)-[:INVOLVED {role: 'Passenger'}]->(mike)
            CREATE (c)-[:WITNESSED_BY]->(sarah)
            CREATE (c)-[:WITNESSED_BY]->(darius)
            CREATE (c)-[:OCCURRED_AT]->(loc)
        """)
        
        print("   ✓ Created: 4 ring members, 1 ghost address, 4 claims")
        print("   ✓ Total exposure: ~$120,000")
    
    # =========================================================================
    # SCENARIO 3: IMMORTAL ASSET (Vehicle Recycling)
    # =========================================================================
    
    def create_immortal_asset(self):
        """
        Vehicle Recycling & Policy Hopping
        
        - BMW X5 "totaled" 3 times in 18 months
        - 3 different "owners" (connected by device fingerprint)
        - Short policy tenure (<60 days) before each loss
        - Total exposure: $185,000
        """
        print("🚗 Creating Scenario 3: Immortal Asset (Vehicle Recycling)...")
        
        # The recycled vehicle — no total_loss_count (computed via traversal)
        veh_id = "VEH_S3_MAIN"
        self._run_query("""
            CREATE (:Vehicle {
                id: $id, 
                vin: '1GKEV33K89J123456',
                make: 'BMW',
                model: 'X5',
                year: 2023,
                color: 'Black',
                value: 65000
            })
        """, id=veh_id)
        
        # Shared device fingerprint (the hidden link)
        device_id = "DEVICE_S3_SHARED"
        self._run_query("""
            CREATE (:Phone {
                id: $id,
                number: 'Device ID: A7X-9K2-M4P',
                type: 'Mobile Device Fingerprint'
            })
        """, id=device_id)
        
        # Three "different" owners
        owners = [
            {
                "id": "P_S3_OWNER1",
                "name": "Marcus Webb",
                "policy_id": "POL_S3_001",
                "claim_id": "CLM_S3_001",
                "bind_date": "2023-08-01",
                "crash_date": "2023-09-15",
                "payout": 58000,
                "incident": "Hit and Run - Parking Lot"
            },
            {
                "id": "P_S3_OWNER2", 
                "name": "Keisha Brown",
                "policy_id": "POL_S3_002",
                "claim_id": "CLM_S3_002",
                "bind_date": "2024-02-10",
                "crash_date": "2024-03-25",
                "payout": 62000,
                "incident": "Theft - Vehicle Recovered Damaged"
            },
            {
                "id": "P_S3_OWNER3",
                "name": "Alice Vane",
                "policy_id": "POL_S3_003", 
                "claim_id": "CLM_S3_003",
                "bind_date": "2024-12-01",
                "crash_date": "2025-01-20",
                "payout": 65000,
                "incident": "Hit and Run - Street Parking",
                "is_current": True
            }
        ]
        
        for owner in owners:
            status = "Open" if owner.get("is_current") else "Paid"
            
            self._run_query("""
                MATCH (v:Vehicle {id: $vid})
                MATCH (device:Phone {id: $device_id})
                MATCH (ins:Insurer {id: $ins_id})
                
                CREATE (p:Person {
                    id: $pid,
                    name: $pname,
                    role: 'Policyholder'
                })
                
                CREATE (pol:Policy {
                    id: $polid,
                    policy_number: $polnum,
                    bind_date: $bind_date,
                    premium: 2400,
                    coverage_type: 'Comprehensive'
                })
                
                CREATE (c:Claim {
                    id: $cid,
                    claim_amount: $payout,
                    claim_date: $crash_date,
                    incident_type: $incident,
                    status: $status,
                    claim_type: 'Property Damage Only'
                })
                
                CREATE (p)-[:HAS_POLICY]->(pol)
                CREATE (pol)-[:COVERS]->(v)
                CREATE (pol)-[:INSURED_BY]->(ins)
                CREATE (c)-[:INVOLVES_VEHICLE]->(v)
                CREATE (c)-[:FILED_BY]->(p)
                CREATE (c)-[:UNDER_POLICY]->(pol)
                CREATE (p)-[:HAS_PHONE]->(device)
            """,
                vid=veh_id,
                device_id=device_id,
                ins_id=self.insurer_id,
                pid=owner["id"],
                pname=owner["name"],
                polid=owner["policy_id"],
                polnum=self._generate_policy_number(),
                bind_date=owner["bind_date"],
                cid=owner["claim_id"],
                payout=owner["payout"],
                crash_date=owner["crash_date"],
                incident=owner["incident"],
                status=status
            )
        
        print("   ✓ Created: 1 vehicle, 3 owners, 3 policies, 3 claims, 1 shared device")
        print("   ✓ Total exposure: ~$185,000")
    
    # =========================================================================
    # SCENARIO 4: NETWORK MIGRATION (Post-Prosecution Evolution)
    # =========================================================================
    
    def create_network_migration(self):
        """
        Post-Prosecution Network Evolution
        
        - Dr. Bernard's was shut down (15 claims prosecuted)
        - Attorney Michael Chen was never sanctioned
        - New provider (Rapid Recovery) opened by Bernard's former employee
        - Chen funnels 82% of new clients to Rapid Recovery
        - Total exposure: $280,000+ in active claims
        """
        print("🔄 Creating Scenario 4: Network Migration...")
        
        # The shut-down provider — no fraud_confirmed or claims_denied
        old_prov_id = "PROV_S4_BERNARD"
        self._run_query("""
            CREATE (:Provider {
                id: $id,
                name: "Dr. Bernard's Auto Injury Center",
                status: 'License Revoked',
                revocation_date: '2024-06-15',
                npi: $npi
            })
        """, id=old_prov_id, npi=self._generate_npi())
        
        # The unsanctioned attorney
        att_id = "ATT_S4_CHEN"
        self._run_query("""
            CREATE (:Attorney {
                id: $id,
                name: 'Michael Chen, Esq.',
                firm: 'Chen Legal Associates',
                status: 'Active',
                bar_number: 'GA-2015-78432'
            })
        """, id=att_id)
        
        # The new provider (phoenix operation)
        new_prov_id = "PROV_S4_RAPID"
        self._run_query("""
            CREATE (:Provider {
                id: $id,
                name: 'Rapid Recovery Medical',
                status: 'Active',
                opened_date: '2024-08-20',
                specialty: 'Auto Injury Rehabilitation',
                npi: $npi
            })
        """, id=new_prov_id, npi=self._generate_npi())
        
        # The ownership/employment link
        self._run_query("""
            MATCH (old:Provider {id: $old_id})
            MATCH (new:Provider {id: $new_id})
            
            CREATE (owner:Person {
                id: 'P_S4_SIMMONS',
                name: 'Dr. Patricia Simmons',
                role: 'Owner / Medical Director',
                license: 'MD-2018-55421'
            })
            
            CREATE (new)-[:OWNED_BY]->(owner)
            CREATE (owner)-[:FORMER_EMPLOYEE_OF {
                role: 'Associate Physician',
                dates: '2021-2024',
                end_reason: 'Clinic Closure'
            }]->(old)
        """, old_id=old_prov_id, new_id=new_prov_id)
        
        # OLD CLAIMS: 15 prosecuted claims
        for i in range(15):
            claimant_id = f"P_S4_OLD_{i:03d}"
            claim_id = f"CLM_S4_OLD_{i:03d}"
            has_chen = i < 12  # 80% represented by Chen
            amount = 4300 + (i % 3) * 100
            
            self._run_query("""
                MATCH (prov:Provider {id: $prov_id})
                
                CREATE (p:Person {
                    id: $pid,
                    name: $pname,
                    role: 'Claimant'
                })
                
                CREATE (c:Claim {
                    id: $cid,
                    claim_amount: $amount,
                    claim_date: $date,
                    incident_type: 'Soft Tissue',
                    status: 'Denied - Fraud',
                    claim_type: 'Bodily Injury'
                })
                
                CREATE (c)-[:FILED_BY]->(p)
                CREATE (c)-[:TREATED_AT]->(prov)
            """,
                prov_id=old_prov_id,
                pid=claimant_id,
                pname=self.generate_name(),
                cid=claim_id,
                amount=amount,
                date=self.generate_date(400, 200)
            )
            
            if has_chen:
                self._run_query("""
                    MATCH (c:Claim {id: $cid})
                    MATCH (a:Attorney {id: $aid})
                    CREATE (c)-[:REPRESENTED_BY]->(a)
                """, cid=claim_id, aid=att_id)
        
        # NEW CLAIMS: 34 active claims at Rapid Recovery
        for i in range(34):
            claimant_id = f"P_S4_NEW_{i:03d}"
            claim_id = f"CLM_S4_NEW_{i:03d}"
            at_rapid = i < 28  # 82% at Rapid Recovery
            prov_id = new_prov_id if at_rapid else random.choice(self.background_providers)
            
            self._run_query("""
                MATCH (prov:Provider {id: $prov_id})
                MATCH (att:Attorney {id: $att_id})
                
                CREATE (p:Person {
                    id: $pid,
                    name: $pname,
                    role: 'Claimant'
                })
                
                CREATE (c:Claim {
                    id: $cid,
                    claim_amount: $amount,
                    claim_date: $date,
                    incident_type: 'Soft Tissue / Whiplash',
                    status: 'Open',
                    claim_type: 'Bodily Injury'
                })
                
                CREATE (c)-[:FILED_BY]->(p)
                CREATE (c)-[:TREATED_AT]->(prov)
                CREATE (c)-[:REPRESENTED_BY]->(att)
            """,
                prov_id=prov_id,
                att_id=att_id,
                pid=claimant_id,
                pname=self.generate_name(),
                cid=claim_id,
                amount=random.randint(6000, 12000),
                date=self.generate_date(90, 7)
            )
        
        print("   ✓ Created: 2 providers (1 revoked, 1 new), 1 attorney, ownership link")
        print("   ✓ Created: 15 old claims (denied), 34 new claims (open)")
        print("   ✓ Total exposure: ~$280,000+")
    
    # =========================================================================
    # MAIN GENERATION FUNCTION
    # =========================================================================
    
    def generate_all_demo_data(self):
        """Generate complete demo dataset with all scenarios."""
        start_time = time.time()
        
        print("\n" + "="*60)
        print("INSURANCE FRAUD GRAPH DEMO - DATA GENERATION")
        print("="*60 + "\n")
        
        try:
            self.clear_database()
            self.create_indexes()
            self.create_infrastructure_pools()
            self.create_background_data(200)
            self.create_spider_web()
            self.create_role_chameleon()
            self.create_immortal_asset()
            self.create_network_migration()
            
            elapsed = round(time.time() - start_time, 2)
            
            print("\n" + "="*60)
            print("✅ DATA GENERATION COMPLETE")
            print("="*60)
            print(f"⏱️  Time: {elapsed} seconds")
            print("\n📊 Summary:")
            print(f"   • Background claims: 200 (legitimate haystack)")
            print(f"   • Spider Web: 45 claims, $162K exposure")
            print(f"   • Role Chameleon: 4 claims, $120K exposure")
            print(f"   • Immortal Asset: 3 claims, $185K exposure")
            print(f"   • Network Migration: 49 claims, $280K+ exposure")
            print(f"\n   TOTAL: 301 claims, ~$747K+ fraud exposure")
            print("="*60 + "\n")
            
            return {
                "status": "success",
                "time_seconds": elapsed,
                "scenarios": {
                    "background": {"claims": 200, "description": "Legitimate haystack"},
                    "spider_web": {"claims": 45, "exposure": "$162,000"},
                    "role_chameleon": {"claims": 4, "exposure": "$120,000"},
                    "immortal_asset": {"claims": 3, "exposure": "$185,000"},
                    "network_migration": {"claims": 49, "exposure": "$280,000+"}
                },
                "total_claims": 301,
                "total_fraud_exposure": "$747,000+"
            }
            
        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            return {"status": "error", "message": str(e)}


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate fraud detection demo data")
    parser.add_argument("--uri", help="Neo4j URI")
    parser.add_argument("--user", help="Neo4j username")
    parser.add_argument("--password", help="Neo4j password")
    
    args = parser.parse_args()
    
    generator = ScenarioDataGenerator(
        uri=args.uri,
        user=args.user,
        password=args.password
    )
    
    result = generator.generate_all_demo_data()
    generator.close()
    
    if result["status"] == "success":
        print("\n🎉 Ready to explore fraud networks!")
        print("Launch the Streamlit app: streamlit run fraud_graph_chat.py")