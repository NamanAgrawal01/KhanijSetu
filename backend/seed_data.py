"""
KhanijSetu Seed Data Script

Creates users, subsidiaries, mines, compliance records, violations,
corrective actions, inspections, contractors, workers, production records,
field reports, alerts, audit logs, and notifications.

DATA CLASSIFICATION: SYNTHETIC / ILLUSTRATIVE
All mine data is based on publicly known Coal India Limited subsidiary structures
and Indian coal mining regulations. This is NOT official government data.
Sources: Coal India Limited (public information), DGMS regulations, Mines Act 1952.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta, timezone
from app.database import engine, SessionLocal, Base
from app.models.user import User, Subsidiary, Notification
from app.models.mine import Mine
from app.models.compliance import ComplianceRequirement, ComplianceRecord
from app.models.inspection import Inspection, InspectionItem
from app.models.violation import Violation
from app.models.corrective_action import CorrectiveAction
from app.models.document import Document, DocumentAnalysis
from app.models.contractor import Contractor, Worker, Attendance
from app.models.production import ProductionRecord
from app.models.field_report import FieldReport
from app.models.alert import Alert
from app.models.audit import AuditLog
from app.auth.jwt_handler import get_password_hash

import random

def seed():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")
        today = date.today()
        now = datetime.now(timezone.utc)

        # ===== SUBSIDIARIES (4) =====
        subsidiaries = [
            Subsidiary(id=1, name="Eastern Coalfields Limited (ECL)", code="ECL", region="Eastern Region", head_name="Shri R.N. Chakraborty", head_email="rn.chakraborty@ecl.gov.in", address="Sanctoria, Asansol, West Bengal"),
            Subsidiary(id=2, name="Central Coalfields Limited (CCL)", code="CCL", region="Central Region", head_name="Shri P.M. Prasad", head_email="pm.prasad@ccl.gov.in", address="Darbhanga House, Ranchi, Jharkhand"),
            Subsidiary(id=3, name="Bharat Coking Coal Limited (BCCL)", code="BCCL", region="Northern Region", head_name="Shri A.K. Jha", head_email="ak.jha@bccl.gov.in", address="Koyla Bhawan, Dhanbad, Jharkhand"),
            Subsidiary(id=4, name="Mahanadi Coalfields Limited (MCL)", code="MCL", region="Southern Region", head_name="Shri O.P. Singh", head_email="op.singh@mcl.gov.in", address="Jagriti Vihar, Burla, Odisha"),
        ]
        db.add_all(subsidiaries)
        db.flush()

        # ===== USERS (10) — inserted WITHOUT mine_id first to avoid circular FK ===
        demo_password = get_password_hash("demo123")
        users = [
            User(id=1, email="admin@khanijsetu.gov.in", password_hash=demo_password, name="Dr. Arun Kumar Verma", role="admin", designation="Platform Administrator", phone="+91-9876543210", subsidiary_id=None, mine_id=None),
            User(id=2, email="operator@khanijsetu.gov.in", password_hash=demo_password, name="Shri Amit Kumar Singh", role="mine_operator", designation="Mine Operator", phone="+91-9876543211", subsidiary_id=1, mine_id=None),
            User(id=3, email="inspector@khanijsetu.gov.in", password_hash=demo_password, name="Shri Rajesh Kumar Sharma", role="inspector", designation="Inspector of Mines, DGMS", phone="+91-9876543212", subsidiary_id=None, mine_id=None),
            User(id=4, email="analyst@khanijsetu.gov.in", password_hash=demo_password, name="Smt. Priya Mehta", role="analyst", designation="General Manager (Compliance)", phone="+91-9876543213", subsidiary_id=1, mine_id=None),
            User(id=5, email="viewer@khanijsetu.gov.in", password_hash=demo_password, name="Shri Vinod Prasad", role="viewer", designation="Director, DGMS", phone="+91-9876543214", subsidiary_id=None, mine_id=None),
            User(id=6, email="inspector2@khanijsetu.gov.in", password_hash=demo_password, name="Shri Pankaj Verma", role="inspector", designation="Assistant Inspector of Mines", phone="+91-9876543215", subsidiary_id=None, mine_id=None),
            User(id=7, email="operator2@khanijsetu.gov.in", password_hash=demo_password, name="Shri Deepak Pandey", role="mine_operator", designation="Mine Operator", phone="+91-9876543216", subsidiary_id=2, mine_id=None),
            User(id=8, email="operator3@khanijsetu.gov.in", password_hash=demo_password, name="Shri Suresh Yadav", role="mine_operator", designation="Mine Operator", phone="+91-9876543217", subsidiary_id=1, mine_id=None),
            User(id=9, email="analyst2@khanijsetu.gov.in", password_hash=demo_password, name="Shri Ramesh Agarwal", role="analyst", designation="Chief Safety Officer", phone="+91-9876543218", subsidiary_id=2, mine_id=None),
            User(id=10, email="operator4@khanijsetu.gov.in", password_hash=demo_password, name="Smt. Kavita Devi", role="mine_operator", designation="Mine Operator", phone="+91-9876543219", subsidiary_id=4, mine_id=None),
        ]
        db.add_all(users)
        db.flush()

        # ===== MINES (12) =====
        mines = [
            Mine(id=1, name="Rajmahal Coal Mine", code="MINE-001", subsidiary_id=1, location="Rajmahal, Godda", district="Godda", state="Jharkhand", latitude=24.7914, longitude=87.8346, mine_type="Opencast", manager_id=2, manager_name="Shri Amit Kumar Singh", capacity_mtpa=2.5, num_workers=245, status="operational", compliance_score=61.0, risk_score=82, safety_score=58.0, environment_score=67.0, labour_score=84.0, production_score=73.0, open_violations=8, last_inspection_date=datetime(2026, 9, 10)),
            Mine(id=2, name="Godda East Mine", code="MINE-002", subsidiary_id=1, location="Godda East, Godda", district="Godda", state="Jharkhand", latitude=24.8301, longitude=87.2161, mine_type="Underground", manager_id=8, manager_name="Shri Suresh Yadav", capacity_mtpa=1.8, num_workers=180, status="operational", compliance_score=68.0, risk_score=76, safety_score=65.0, environment_score=62.0, labour_score=78.0, production_score=70.0, open_violations=5, last_inspection_date=datetime(2026, 8, 28)),
            Mine(id=3, name="Kathara Deep Mine", code="MINE-003", subsidiary_id=2, location="Kathara, Bokaro", district="Bokaro", state="Jharkhand", latitude=23.6693, longitude=85.9558, mine_type="Underground", manager_id=7, manager_name="Shri Deepak Pandey", capacity_mtpa=1.5, num_workers=210, status="operational", compliance_score=72.0, risk_score=71, safety_score=68.0, environment_score=73.0, labour_score=76.0, production_score=69.0, open_violations=6, last_inspection_date=datetime(2026, 9, 5)),
            Mine(id=4, name="Bokaro Central Mine", code="MINE-004", subsidiary_id=2, location="Bokaro Steel City", district="Bokaro", state="Jharkhand", latitude=23.7957, longitude=86.1520, mine_type="Opencast", manager_name="Shri Manoj Kumar", capacity_mtpa=3.0, num_workers=320, status="operational", compliance_score=81.0, risk_score=45, safety_score=78.0, environment_score=80.0, labour_score=86.0, production_score=82.0, open_violations=3, last_inspection_date=datetime(2026, 9, 8)),
            Mine(id=5, name="Jharia West Mine", code="MINE-005", subsidiary_id=3, location="Jharia, Dhanbad", district="Dhanbad", state="Jharkhand", latitude=23.7473, longitude=86.4304, mine_type="Underground", manager_name="Shri Rakesh Sharma", capacity_mtpa=2.0, num_workers=195, status="operational", compliance_score=85.0, risk_score=38, safety_score=82.0, environment_score=84.0, labour_score=88.0, production_score=80.0, open_violations=2, last_inspection_date=datetime(2026, 9, 11)),
            Mine(id=6, name="Mugma Colliery", code="MINE-006", subsidiary_id=3, location="Mugma, Dhanbad", district="Dhanbad", state="Jharkhand", latitude=23.7600, longitude=86.4200, mine_type="Opencast", manager_name="Shri Naveen Gupta", capacity_mtpa=2.2, num_workers=175, status="operational", compliance_score=79.0, risk_score=48, safety_score=76.0, environment_score=78.0, labour_score=82.0, production_score=77.0, open_violations=4, last_inspection_date=datetime(2026, 9, 3)),
            Mine(id=7, name="Sonepur Bazari Mine", code="MINE-007", subsidiary_id=1, location="Sonepur Bazari, Raniganj", district="Burdwan", state="West Bengal", latitude=23.6200, longitude=87.1300, mine_type="Opencast", manager_name="Shri Bikash Roy", capacity_mtpa=4.0, num_workers=410, status="operational", compliance_score=88.0, risk_score=32, safety_score=85.0, environment_score=86.0, labour_score=90.0, production_score=88.0, open_violations=1, last_inspection_date=datetime(2026, 9, 9)),
            Mine(id=8, name="Dhanbad North Mine", code="MINE-008", subsidiary_id=3, location="Dhanbad North", district="Dhanbad", state="Jharkhand", latitude=23.8000, longitude=86.4500, mine_type="Underground", manager_name="Shri Alok Mishra", capacity_mtpa=1.2, num_workers=150, status="operational", compliance_score=74.0, risk_score=56, safety_score=71.0, environment_score=72.0, labour_score=80.0, production_score=68.0, open_violations=5, last_inspection_date=datetime(2026, 8, 25)),
            Mine(id=9, name="Korba West OCP", code="MINE-009", subsidiary_id=2, location="Korba, Chhattisgarh", district="Korba", state="Chhattisgarh", latitude=22.3500, longitude=82.7000, mine_type="Opencast", manager_name="Shri Vijay Tiwari", capacity_mtpa=5.0, num_workers=480, status="operational", compliance_score=91.0, risk_score=22, safety_score=90.0, environment_score=88.0, labour_score=92.0, production_score=93.0, open_violations=1, last_inspection_date=datetime(2026, 9, 12)),
            Mine(id=10, name="Talcher Coalfield", code="MINE-010", subsidiary_id=4, location="Talcher, Angul", district="Angul", state="Odisha", latitude=20.9500, longitude=85.2100, mine_type="Opencast", manager_id=10, manager_name="Smt. Kavita Devi", capacity_mtpa=6.0, num_workers=520, status="operational", compliance_score=87.0, risk_score=28, safety_score=84.0, environment_score=85.0, labour_score=90.0, production_score=89.0, open_violations=2, last_inspection_date=datetime(2026, 9, 7)),
            Mine(id=11, name="Raniganj Area Mine", code="MINE-011", subsidiary_id=1, location="Raniganj, Burdwan", district="Burdwan", state="West Bengal", latitude=23.6100, longitude=87.1500, mine_type="Underground", manager_name="Shri Partha Das", capacity_mtpa=1.4, num_workers=165, status="operational", compliance_score=70.0, risk_score=62, safety_score=66.0, environment_score=69.0, labour_score=75.0, production_score=72.0, open_violations=4, last_inspection_date=datetime(2026, 8, 20)),
            Mine(id=12, name="Hazaribagh South Mine", code="MINE-012", subsidiary_id=2, location="Hazaribagh, Jharkhand", district="Hazaribagh", state="Jharkhand", latitude=23.9500, longitude=85.3600, mine_type="Underground", manager_name="Shri Sandeep Kumar", capacity_mtpa=1.0, num_workers=130, status="suspended", compliance_score=52.0, risk_score=88, safety_score=48.0, environment_score=55.0, labour_score=62.0, production_score=45.0, open_violations=9, last_inspection_date=datetime(2026, 7, 15)),
        ]
        db.add_all(mines)
        db.flush()

        # Now update users with their mine_ids (after mines exist)
        db.query(User).filter(User.id == 2).update({"mine_id": 1})
        db.query(User).filter(User.id == 7).update({"mine_id": 3})
        db.query(User).filter(User.id == 8).update({"mine_id": 2})
        db.query(User).filter(User.id == 10).update({"mine_id": 10})
        db.flush()


        # ===== COMPLIANCE REQUIREMENTS (12) =====
        requirements = [
            ComplianceRequirement(id=1, title="Monthly Safety Inspection", category="safety", description="Mandatory monthly safety inspection as per Mines Act", frequency="monthly", authority="DGMS", regulation_ref="Mines Act, 1952 - Section 22"),
            ComplianceRequirement(id=2, title="Fire Safety Certificate", category="safety", description="Valid fire safety certificate and equipment inspection", frequency="annual", authority="DGMS", regulation_ref="Coal Mines Regulations, 2017 - Regulation 186"),
            ComplianceRequirement(id=3, title="Emergency Evacuation Drill", category="safety", description="Quarterly emergency evacuation drill", frequency="quarterly", authority="DGMS", regulation_ref="Mines Rules, 1955"),
            ComplianceRequirement(id=4, title="Environmental Monitoring Report", category="environment", description="Quarterly air and water quality monitoring", frequency="quarterly", authority="MoEFCC", regulation_ref="Environment Protection Act, 1986"),
            ComplianceRequirement(id=5, title="Dust Suppression System Check", category="environment", description="Monthly dust suppression system functionality check", frequency="monthly", authority="SPCB", regulation_ref="Air Act, 1981"),
            ComplianceRequirement(id=6, title="Worker Safety Training", category="labour", description="Bi-annual worker safety training and certification", frequency="biannual", authority="DGMS", regulation_ref="Mines Vocational Training Rules, 1966"),
            ComplianceRequirement(id=7, title="Equipment Safety Certification", category="equipment", description="Annual equipment safety certification for heavy machinery", frequency="annual", authority="DGMS", regulation_ref="Coal Mines Regulations, 2017"),
            ComplianceRequirement(id=8, title="Production Reporting", category="production", description="Monthly production and output reporting", frequency="monthly", authority="CIL", regulation_ref="Coal India Guidelines"),
            ComplianceRequirement(id=9, title="PPE Compliance Audit", category="safety", description="Monthly PPE compliance audit for all workers", frequency="monthly", authority="DGMS", regulation_ref="Mines Rules, 1955 - Rule 29"),
            ComplianceRequirement(id=10, title="Ventilation System Check", category="safety", description="Weekly ventilation and gas monitoring for underground mines", frequency="weekly", authority="DGMS", regulation_ref="Coal Mines Regulations, 2017 - Regulation 153"),
            ComplianceRequirement(id=11, title="Mine Plan Compliance", category="documentation", description="Quarterly mine plan compliance verification", frequency="quarterly", authority="DGMS", regulation_ref="Mines Act, 1952"),
            ComplianceRequirement(id=12, title="Contractor Compliance Review", category="documentation", description="Monthly contractor safety and compliance review", frequency="monthly", authority="Internal", regulation_ref="CIL Contractor Policy"),
        ]
        db.add_all(requirements)
        db.flush()

        # ===== COMPLIANCE RECORDS (72 — 6 requirements × 12 mines) =====
        statuses = ["completed", "completed", "pending", "due_soon", "overdue"]
        risk_levels = ["low", "low", "medium", "high", "critical"]
        records = []
        officers = ["Shri Amit Kumar Singh", "Shri Suresh Yadav", "Shri Deepak Pandey", "Shri Manoj Kumar", "Shri Rakesh Sharma", "Shri Naveen Gupta", "Shri Bikash Roy", "Shri Alok Mishra", "Shri Vijay Tiwari", "Smt. Kavita Devi", "Shri Partha Das", "Shri Sandeep Kumar"]
        for mine_id in range(1, 13):
            for req_id in [1, 2, 3, 4, 5, 9]:
                s_idx = random.randint(0, 4)
                # Make mine 1 (Rajmahal) have more overdue items
                if mine_id == 1 and req_id in [2, 3, 9]:
                    s_idx = 4  # overdue
                # Mine 12 (suspended) mostly overdue
                if mine_id == 12:
                    s_idx = random.choice([3, 4, 4, 4])
                # Mine 7, 9, 10 (high compliance) mostly completed
                if mine_id in [7, 9, 10]:
                    s_idx = random.choice([0, 0, 0, 1])
                status = statuses[s_idx]
                risk = risk_levels[s_idx]
                due = today - timedelta(days=random.randint(-30, 30))
                completed = due - timedelta(days=random.randint(1, 5)) if status == "completed" else None
                records.append(ComplianceRecord(
                    requirement_id=req_id, mine_id=mine_id,
                    status=status, due_date=due, completed_date=completed,
                    responsible_officer=officers[(mine_id - 1) % len(officers)],
                    risk_level=risk,
                ))
        db.add_all(records)
        db.flush()

        # ===== VIOLATIONS (25) =====
        violations = [
            Violation(violation_code="VIO-2026-0001", mine_id=1, category="safety", severity="high", title="PPE Non-Compliance in Active Mining Zone", description="12 out of 45 workers observed without proper PPE in active mining zone during routine inspection", reported_by=3, reported_by_name="Inspector R.K. Sharma", assigned_to_name="Shri Amit Kumar Singh", detected_date=today - timedelta(days=15), deadline=today + timedelta(days=5), status="assigned", is_recurring=1, recurrence_count=4),
            Violation(violation_code="VIO-2026-0002", mine_id=1, category="safety", severity="critical", title="Fire Safety Equipment Expired", description="Fire extinguishers in Section B found expired. Last serviced January 2026.", reported_by=3, reported_by_name="Inspector R.K. Sharma", assigned_to_name="Shri Amit Kumar Singh", detected_date=today - timedelta(days=10), deadline=today + timedelta(days=2), status="detected", is_recurring=0),
            Violation(violation_code="VIO-2026-0003", mine_id=1, category="safety", severity="high", title="Emergency Exit Signage Not Illuminated", description="Emergency exit signage in Shaft 3 not illuminated, posing safety risk during power failure", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=10), status="assigned", is_recurring=0),
            Violation(violation_code="VIO-2026-0004", mine_id=1, category="environment", severity="medium", title="Dust Suppression System Malfunction", description="Dust suppression system in Section A not functioning properly", reported_by=6, reported_by_name="Inspector P. Verma", detected_date=today - timedelta(days=20), status="in_progress", is_recurring=0),
            Violation(violation_code="VIO-2026-0005", mine_id=1, category="safety", severity="high", title="Roof Support Deficiency in Gallery 7", description="Roof support in Gallery 7 needs immediate reinforcement per geotechnical assessment", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=8), status="detected", is_recurring=0),
            Violation(violation_code="VIO-2026-0006", mine_id=2, category="environment", severity="high", title="Environmental Compliance Overdue", description="Environmental monitoring report overdue by 15 days. PM2.5 and TSS levels need verification.", reported_by=6, reported_by_name="Inspector P. Verma", detected_date=today - timedelta(days=15), deadline=today - timedelta(days=5), status="assigned", is_recurring=0),
            Violation(violation_code="VIO-2026-0007", mine_id=3, category="equipment", severity="medium", title="Equipment Maintenance Delay", description="Heavy machinery maintenance logs overdue for 3 pieces of equipment", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=12), status="in_progress", is_recurring=1, recurrence_count=3),
            Violation(violation_code="VIO-2026-0008", mine_id=2, category="safety", severity="high", title="Fire Safety Certificate Expiring", description="Fire safety certificate expires within 5 days. Renewal not initiated.", reported_by=6, reported_by_name="Inspector P. Verma", detected_date=today - timedelta(days=5), deadline=today + timedelta(days=5), status="detected", is_recurring=0),
            Violation(violation_code="VIO-2026-0009", mine_id=3, category="safety", severity="medium", title="Incomplete First Aid Kits", description="First aid kits in underground sections found incomplete during inspection", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=7), status="assigned", is_recurring=0),
            Violation(violation_code="VIO-2026-0010", mine_id=1, category="documentation", severity="low", title="Safety Register Update Pending", description="Safety register not updated for last 2 weeks", reported_by=6, reported_by_name="Inspector P. Verma", detected_date=today - timedelta(days=14), status="in_progress", is_recurring=0),
            Violation(violation_code="VIO-2026-0011", mine_id=2, category="environment", severity="medium", title="Environmental Reporting Gap", description="Quarterly emission reports submitted late for second consecutive quarter", reported_by=6, reported_by_name="Inspector P. Verma", detected_date=today - timedelta(days=20), status="detected", is_recurring=1, recurrence_count=2),
            Violation(violation_code="VIO-2026-0012", mine_id=4, category="safety", severity="low", title="Minor Ventilation Irregularity", description="Slight ventilation flow reduction in Section C, within tolerance but needs monitoring", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=3), status="assigned", is_recurring=0),
            Violation(violation_code="VIO-2026-0013", mine_id=6, category="equipment", severity="medium", title="Conveyor Belt Wear", description="Conveyor belt showing excessive wear, replacement needed within 30 days", detected_date=today - timedelta(days=6), status="in_progress", is_recurring=0),
            Violation(violation_code="VIO-2026-0014", mine_id=8, category="safety", severity="high", title="Water Seepage in Access Tunnel", description="Water seepage observed in lower level access tunnel, structural assessment required", detected_date=today - timedelta(days=4), status="detected", is_recurring=0),
            Violation(violation_code="VIO-2026-0015", mine_id=8, category="labour", severity="medium", title="Worker Training Compliance Gap", description="15 workers overdue for mandatory safety training renewal", detected_date=today - timedelta(days=11), status="assigned", is_recurring=0),
            Violation(violation_code="VIO-2026-0016", mine_id=1, category="safety", severity="high", title="PPE Violation - Respiratory Protection", description="Workers in dusty Section C not using respiratory protection", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=3), status="detected", is_recurring=1, recurrence_count=4),
            Violation(violation_code="VIO-2026-0017", mine_id=1, category="safety", severity="medium", title="Damaged Safety Helmets", description="3 safety helmets found damaged and not replaced", detected_date=today - timedelta(days=2), status="detected", is_recurring=0),
            Violation(violation_code="VIO-2026-0018", mine_id=3, category="equipment", severity="high", title="Equipment Safety Certification Lapsed", description="Annual safety certification for 2 excavators has lapsed", detected_date=today - timedelta(days=9), status="assigned", is_recurring=1, recurrence_count=2),
            Violation(violation_code="VIO-2026-0019", mine_id=11, category="safety", severity="high", title="Ventilation Failure in Level 3", description="Primary ventilation fan in Level 3 non-functional for 48 hours. Backup operating at reduced capacity.", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=2), deadline=today + timedelta(days=1), status="detected", is_recurring=0),
            Violation(violation_code="VIO-2026-0020", mine_id=12, category="safety", severity="critical", title="Methane Levels Exceeding Safe Limit", description="Methane sensor readings at 2.1% in Section D, exceeding the 1.5% permissible limit under CMR 2017", reported_by=3, reported_by_name="Inspector R.K. Sharma", detected_date=today - timedelta(days=1), deadline=today, status="detected", is_recurring=1, recurrence_count=3),
            Violation(violation_code="VIO-2026-0021", mine_id=12, category="environment", severity="high", title="Mine Water Discharge pH Non-Compliant", description="Mine water discharge pH recorded at 4.2, well below the 6.0-8.5 permissible range", detected_date=today - timedelta(days=5), status="assigned", is_recurring=0),
            Violation(violation_code="VIO-2026-0022", mine_id=11, category="labour", severity="medium", title="Overtime Violations", description="23 workers exceeded maximum permissible overtime hours under Mines Act, Section 36", detected_date=today - timedelta(days=8), status="in_progress", is_recurring=0),
            Violation(violation_code="VIO-2026-0023", mine_id=9, category="documentation", severity="low", title="Mine Closure Plan Not Updated", description="Annual mine closure plan update pending for 2026-27 cycle", detected_date=today - timedelta(days=18), status="assigned", is_recurring=0),
            Violation(violation_code="VIO-2026-0024", mine_id=12, category="equipment", severity="critical", title="Hoist Rope Deterioration", description="Wire rope on main winding engine shows 12% reduction in diameter, exceeding the 10% discard threshold", detected_date=today - timedelta(days=3), deadline=today, status="detected", is_recurring=0),
            Violation(violation_code="VIO-2026-0025", mine_id=10, category="environment", severity="medium", title="Noise Level Exceedance", description="Daytime noise levels at 82 dB at mine boundary, exceeding the 75 dB limit", detected_date=today - timedelta(days=7), status="in_progress", is_recurring=0),
        ]
        db.add_all(violations)
        db.flush()

        # ===== CORRECTIVE ACTIONS (15) =====
        corrective_actions = [
            CorrectiveAction(action_code="CA-2026-0001", violation_id=1, mine_id=1, title="Conduct PPE compliance training for all workers", description="Mandatory PPE training session for all 245 workers with certification", assigned_to_name="Shri Amit Kumar Singh", deadline=today + timedelta(days=7), priority="high", status="in_progress"),
            CorrectiveAction(action_code="CA-2026-0002", violation_id=2, mine_id=1, title="Replace expired fire extinguishers in Section B", description="Procure and install new fire extinguishers; service existing units", assigned_to_name="Shri Amit Kumar Singh", deadline=today + timedelta(days=3), priority="critical", status="pending"),
            CorrectiveAction(action_code="CA-2026-0003", violation_id=3, mine_id=1, title="Repair emergency exit signage illumination", description="Repair/replace illuminated signage in Shaft 3", assigned_to_name="Shri Amit Kumar Singh", deadline=today + timedelta(days=5), priority="high", status="pending"),
            CorrectiveAction(action_code="CA-2026-0004", violation_id=4, mine_id=1, title="Repair dust suppression system", description="Repair malfunctioning dust suppression system in Section A", assigned_to_name="Shri Amit Kumar Singh", deadline=today + timedelta(days=10), priority="medium", status="in_progress"),
            CorrectiveAction(action_code="CA-2026-0005", violation_id=6, mine_id=2, title="Submit overdue environmental monitoring report", description="Complete and submit environmental monitoring report for Q2 2026", assigned_to_name="Shri Suresh Yadav", deadline=today + timedelta(days=5), priority="high", status="overdue"),
            CorrectiveAction(action_code="CA-2026-0006", violation_id=7, mine_id=3, title="Complete equipment maintenance backlog", description="Service and certify 3 pieces of heavy machinery", assigned_to_name="Shri Deepak Pandey", deadline=today + timedelta(days=14), priority="medium", status="in_progress"),
            CorrectiveAction(action_code="CA-2026-0007", violation_id=9, mine_id=3, title="Replenish first aid kits", description="Audit and replenish all underground first aid kits", assigned_to_name="Shri Deepak Pandey", deadline=today + timedelta(days=3), priority="high", status="submitted", evidence_url="/uploads/evidence_firstaid.jpg", evidence_notes="All kits replenished and documented"),
            CorrectiveAction(action_code="CA-2026-0008", violation_id=12, mine_id=4, title="Monitor ventilation flow", description="Install additional monitoring sensors in Section C", assigned_to_name="Shri Manoj Kumar", deadline=today + timedelta(days=7), priority="low", status="verified", verified_by_name="Inspector R.K. Sharma", verified_date=today - timedelta(days=1)),
            CorrectiveAction(action_code="CA-2026-0009", violation_id=13, mine_id=6, title="Replace worn conveyor belt", description="Procure and replace conveyor belt section", assigned_to_name="Shri Naveen Gupta", deadline=today + timedelta(days=20), priority="medium", status="in_progress"),
            CorrectiveAction(action_code="CA-2026-0010", violation_id=15, mine_id=8, title="Schedule worker safety training", description="Arrange mandatory safety training for 15 workers", assigned_to_name="Shri Alok Mishra", deadline=today + timedelta(days=14), priority="medium", status="pending"),
            CorrectiveAction(action_code="CA-2026-0011", violation_id=19, mine_id=11, title="Repair primary ventilation fan in Level 3", description="Emergency repair of ventilation fan motor and impeller assembly", assigned_to_name="Shri Partha Das", deadline=today + timedelta(days=2), priority="critical", status="in_progress"),
            CorrectiveAction(action_code="CA-2026-0012", violation_id=20, mine_id=12, title="Evacuate Section D and install methane drainage", description="Evacuate workers from Section D, install methane drainage boreholes, and calibrate monitoring sensors", assigned_to_name="Shri Sandeep Kumar", deadline=today, priority="critical", status="in_progress"),
            CorrectiveAction(action_code="CA-2026-0013", violation_id=21, mine_id=12, title="Install water treatment plant for mine discharge", description="Commission portable water treatment unit for pH adjustment before discharge", assigned_to_name="Shri Sandeep Kumar", deadline=today + timedelta(days=10), priority="high", status="pending"),
            CorrectiveAction(action_code="CA-2026-0014", violation_id=24, mine_id=12, title="Replace deteriorated hoist rope", description="Replace main winding rope and conduct statutory rope test as per Regulation 162", assigned_to_name="Shri Sandeep Kumar", deadline=today + timedelta(days=1), priority="critical", status="pending"),
            CorrectiveAction(action_code="CA-2026-0015", violation_id=25, mine_id=10, title="Install noise barriers at mine boundary", description="Install acoustic barriers and schedule blasting operations during daytime only", assigned_to_name="Smt. Kavita Devi", deadline=today + timedelta(days=21), priority="medium", status="in_progress"),
        ]
        db.add_all(corrective_actions)
        db.flush()

        # ===== INSPECTIONS (25) =====
        inspection_types = ["routine", "safety", "environmental", "special", "follow_up"]
        ratings = ["satisfactory", "needs_improvement", "unsatisfactory", "satisfactory"]
        for i in range(1, 26):
            mine_id = ((i - 1) % 12) + 1
            insp = Inspection(
                mine_id=mine_id,
                inspector_id=3 if i % 2 == 0 else 6,
                inspection_type=inspection_types[i % 5],
                scheduled_date=today - timedelta(days=i * 4),
                completed_date=today - timedelta(days=i * 4 + 1) if i > 3 else None,
                status="completed" if i > 3 else ("scheduled" if i == 1 else "in_progress"),
                priority=["normal", "high", "urgent", "normal"][i % 4],
                overall_rating=ratings[i % 4] if i > 3 else None,
                findings_summary=f"Inspection findings for mine {mine_id}: {'Several safety observations requiring attention' if mine_id in [1,2,3,12] else 'Mine operations generally satisfactory with minor observations'}" if i > 3 else None,
                gps_latitude=23.7 + random.uniform(0, 0.3),
                gps_longitude=86.4 + random.uniform(0, 0.3),
            )
            db.add(insp)
        db.flush()

        # Add checklist items for first 8 inspections
        checklist = [
            ("PPE", "Personal Protective Equipment compliance"),
            ("PPE", "Safety helmets condition"),
            ("Emergency", "Emergency exit accessibility"),
            ("Emergency", "Fire extinguisher status"),
            ("Emergency", "Emergency evacuation plan display"),
            ("Equipment", "Equipment maintenance logs"),
            ("Equipment", "Heavy machinery safety certification"),
            ("Safety", "Worker safety briefing records"),
            ("Safety", "First aid kit availability"),
            ("Environment", "Dust suppression systems"),
            ("Environment", "Ventilation systems"),
            ("Documentation", "Safety register updated"),
            ("Documentation", "Compliance certificates current"),
        ]
        for insp_id in range(1, 9):
            for cat, name in checklist:
                item_status = random.choice(["pass", "pass", "pass", "fail", "na"])
                db.add(InspectionItem(
                    inspection_id=insp_id, category=cat, item_name=name,
                    status=item_status,
                    severity="high" if item_status == "fail" else None,
                    notes="Requires attention" if item_status == "fail" else None,
                ))
        db.flush()

        # ===== CONTRACTORS (10) =====
        contractors = [
            Contractor(name="Shri Rajan Enterprises", company="Rajan Mining Services", mine_id=1, contract_type="Mining Operations", contract_start=date(2026, 1, 1), contract_end=date(2026, 12, 31), num_workers=45, safety_score=72.0, violation_count=3, compliance_status="compliant", performance_rating="good"),
            Contractor(name="Bharat Mining Services", company="Bharat Mining Pvt Ltd", mine_id=1, contract_type="Equipment Operation", contract_start=date(2026, 3, 1), contract_end=date(2026, 9, 30), num_workers=28, safety_score=52.0, violation_count=5, compliance_status="non_compliant", performance_rating="poor"),
            Contractor(name="Eastern Excavators", company="Eastern Excavators Pvt Ltd", mine_id=2, contract_type="Excavation", contract_start=date(2026, 1, 15), contract_end=date(2027, 1, 14), num_workers=35, safety_score=61.0, violation_count=3, compliance_status="compliant", performance_rating="average"),
            Contractor(name="Singh Transport Co", company="Singh Transport & Logistics", mine_id=3, contract_type="Transportation", contract_start=date(2026, 4, 1), contract_end=date(2026, 10, 15), num_workers=22, safety_score=85.0, violation_count=0, compliance_status="compliant", performance_rating="excellent"),
            Contractor(name="National Construction Ltd", company="National Construction & Mining", mine_id=4, contract_type="Civil Works", contract_start=date(2026, 2, 1), contract_end=date(2026, 11, 30), num_workers=40, safety_score=78.0, violation_count=1, compliance_status="compliant", performance_rating="good"),
            Contractor(name="Jharkhand Earth Movers", company="JEM Mining Solutions", mine_id=5, contract_type="Earth Moving", contract_start=date(2026, 1, 1), contract_end=date(2026, 12, 31), num_workers=30, safety_score=88.0, violation_count=0, compliance_status="compliant", performance_rating="excellent"),
            Contractor(name="Coalfield Services India", company="CSI Pvt Ltd", mine_id=6, contract_type="Support Services", contract_start=date(2026, 5, 1), contract_end=date(2026, 10, 31), num_workers=18, safety_score=74.0, violation_count=2, compliance_status="expiring", performance_rating="good"),
            Contractor(name="Mineral Tech Solutions", company="MTS Mining", mine_id=7, contract_type="Technical Services", contract_start=date(2026, 1, 1), contract_end=date(2027, 3, 31), num_workers=25, safety_score=82.0, violation_count=1, compliance_status="compliant", performance_rating="good"),
            Contractor(name="Odisha Earth Movers", company="OEM Pvt Ltd", mine_id=10, contract_type="Overburden Removal", contract_start=date(2026, 2, 1), contract_end=date(2027, 1, 31), num_workers=55, safety_score=86.0, violation_count=0, compliance_status="compliant", performance_rating="excellent"),
            Contractor(name="Korba Mining Support", company="KMS Infrastructure", mine_id=9, contract_type="Drilling & Blasting", contract_start=date(2026, 3, 1), contract_end=date(2026, 12, 31), num_workers=32, safety_score=80.0, violation_count=1, compliance_status="compliant", performance_rating="good"),
        ]
        db.add_all(contractors)
        db.flush()

        # ===== WORKERS (120) =====
        indian_names = [
            "Rajesh Kumar", "Sunil Sharma", "Anil Yadav", "Vijay Singh", "Manoj Tiwari",
            "Ravi Prasad", "Ashok Verma", "Deepak Mishra", "Sanjay Gupta", "Pankaj Das",
            "Ramesh Patel", "Suresh Mehta", "Govind Thakur", "Dinesh Chauhan", "Bikash Roy",
            "Ajay Dubey", "Prakash Rai", "Santosh Pandey", "Mukesh Sahu", "Rakesh Mahto",
            "Umesh Oraon", "Kamlesh Munda", "Ganesh Tudu", "Birsa Hembrom", "Lakhan Murmu",
            "Pappu Ram", "Chhotu Singh", "Babu Lal", "Phool Chand", "Mangal Yadav",
            "Shyam Sundar", "Ram Dayal", "Jagdish Prasad", "Nand Kishor", "Hari Om",
            "Gopal Yadav", "Mohan Lal", "Kailash Nath", "Dev Narayan", "Brij Mohan",
            "Sukhdev Singh", "Harbans Lal", "Jagtar Singh", "Balwant Rai", "Gurdas Mann",
            "Satish Kumar", "Vinod Soni", "Anand Prakash", "Brijesh Tiwari", "Arvind Saxena",
            "Navin Jha", "Amit Ranjan", "Sonu Tirkey", "Laxman Oraon", "Sahib Gond",
            "Vishnu Yadav", "Shankar Lal", "Trilok Nath", "Pradeep Rawat", "Kishore Kumar",
            "Yogesh Bharti", "Dharam Pal", "Chunni Lal", "Fakir Chand", "Kishan Sah",
            "Nagendra Yadav", "Basant Kumar", "Girish Yadav", "Harish Chandra", "Inder Mohan",
            "Jitendra Yadav", "Kedar Nath", "Lalji Yadav", "Madan Mohan", "Narendra Singh",
            "Om Prakash", "Prem Narayan", "Qumar Ali", "Ram Swaroop", "Shiv Kumar",
            "Tek Narayan", "Umakant Mishra", "Vikram Singh", "Wakil Ahmad", "Xalxo Peter",
            "Yashwant Rao", "Zahir Khan", "Amar Nath", "Bhola Nath", "Chandra Mohan",
            "Devi Dayal", "Eklavya Yadav", "Fateh Singh", "Ganga Ram", "Hanuman Prasad",
            "Ishwar Dayal", "Jagannath Sahu", "Kabir Das", "Laxmi Narayan", "Munna Lal",
            "Narayan Das", "Onkar Singh", "Parshuram Yadav", "Qadir Hussain", "Raghu Nath",
            "Saryu Prasad", "Tulsi Ram", "Udai Shankar", "Veer Bahadur", "Wali Mohammad",
            "Xerxes Gond", "Yogeshwar Yadav", "Zafar Iqbal", "Aditya Oraon", "Bharat Ram",
            "Chandrabhan Singh", "Durga Prasad", "Eknath Yadav", "Firoz Khan", "Govardhan Das",
        ]
        worker_roles = ["Miner", "Machine Operator", "Electrician", "Safety Officer", "Supervisor", "Helper", "Driver", "Blaster", "Fitter", "Surveyor"]
        departments = ["Mining", "Mechanical", "Electrical", "Safety", "Transport", "Administration"]
        training_statuses = ["current", "current", "current", "due_soon", "overdue"]
        for i in range(1, 121):
            mine_id = ((i - 1) % 12) + 1
            is_contract = 1 if i > 80 else 0
            contractor_id = ((i - 81) % 10) + 1 if is_contract else None
            db.add(Worker(
                employee_id=f"EMP-{i:04d}",
                name=indian_names[(i - 1) % len(indian_names)],
                contractor_id=contractor_id,
                mine_id=mine_id,
                role=worker_roles[i % len(worker_roles)],
                department=departments[i % len(departments)],
                is_contract=is_contract,
                training_status=training_statuses[i % len(training_statuses)],
            ))
        db.flush()

        # ===== ATTENDANCE (14 days × 120 workers = ~1680 records, cap at 7 days) =====
        for day_offset in range(7):
            d = today - timedelta(days=day_offset)
            for worker_id in range(1, 121):
                mine_id = ((worker_id - 1) % 12) + 1
                status = random.choice(["present", "present", "present", "present", "absent", "leave"])
                check_in_hour = random.randint(6, 8)
                check_in_min = random.randint(0, 59)
                db.add(Attendance(
                    worker_id=worker_id, mine_id=mine_id,
                    date=d, status=status,
                    method=random.choice(["manual", "qr", "biometric"]),
                    check_in=datetime(2026, 9, d.day, check_in_hour, check_in_min) if status == "present" else None,
                ))
        db.flush()

        # ===== PRODUCTION RECORDS (180 — 12 mines × 15 days) =====
        for mine_id in range(1, 13):
            base_target = [1200, 800, 700, 1500, 900, 1000, 2000, 600, 2500, 3000, 650, 500][mine_id - 1]
            for day_offset in range(15):
                d = today - timedelta(days=day_offset)
                target = base_target + random.randint(-100, 100)
                if mine_id == 1:
                    actual = int(target * random.uniform(0.60, 0.80))
                elif mine_id == 12:
                    actual = int(target * random.uniform(0.30, 0.50))  # suspended mine
                elif mine_id in [7, 9, 10]:
                    actual = int(target * random.uniform(0.92, 1.05))  # high performers
                else:
                    actual = int(target * random.uniform(0.80, 1.02))
                downtime = random.uniform(0, 4) if mine_id in [1, 3, 12] else random.uniform(0, 1.5)
                incidents = 0
                if mine_id == 1 and day_offset < 3:
                    incidents = 1
                if mine_id == 12 and day_offset < 5:
                    incidents = random.randint(0, 2)
                db.add(ProductionRecord(
                    mine_id=mine_id, date=d,
                    target_tonnes=target, actual_tonnes=actual,
                    downtime_hours=round(downtime, 1),
                    downtime_reason="Equipment maintenance" if downtime > 2 else ("Shift change delay" if downtime > 1 else None),
                    safety_incidents=incidents,
                ))
        db.flush()

        # ===== FIELD REPORTS (10) =====
        field_reports = [
            FieldReport(report_code="FR-2026-0001", mine_id=1, reporter_id=3, reporter_name="Inspector R.K. Sharma", observation_type="safety", severity="high", title="Unsafe working conditions in Shaft 3", description="Workers observed working near unsupported roof section. Immediate reinforcement required.", latitude=24.7914, longitude=87.8346, location_label="Shaft 3, Rajmahal Mine"),
            FieldReport(report_code="FR-2026-0002", mine_id=1, reporter_id=3, reporter_name="Inspector R.K. Sharma", observation_type="safety", severity="medium", title="PPE compliance issue at Entry Gate", description="Several workers entering active zone without proper respiratory protection", latitude=24.7920, longitude=87.8350, location_label="Entry Gate, Rajmahal Mine"),
            FieldReport(report_code="FR-2026-0003", mine_id=2, reporter_id=6, reporter_name="Inspector P. Verma", observation_type="environment", severity="medium", title="Dust levels elevated in Section A", description="Visual observation of elevated dust levels. Suppression system needs inspection.", latitude=24.8301, longitude=87.2161, location_label="Section A, Godda East"),
            FieldReport(report_code="FR-2026-0004", mine_id=3, reporter_id=3, reporter_name="Inspector R.K. Sharma", observation_type="equipment", severity="high", title="Excavator hydraulic leak", description="Hydraulic fluid leak observed on Excavator EX-003. Machine should be taken out of service.", latitude=23.6693, longitude=85.9558, location_label="Pit Area, Kathara Deep"),
            FieldReport(report_code="FR-2026-0005", mine_id=4, reporter_id=6, reporter_name="Inspector P. Verma", observation_type="general", severity="low", title="Housekeeping observation", description="General housekeeping improvement needed near workshop area", latitude=23.7957, longitude=86.1520, location_label="Workshop, Bokaro Central"),
            FieldReport(report_code="FR-2026-0006", mine_id=12, reporter_id=3, reporter_name="Inspector R.K. Sharma", observation_type="safety", severity="critical", title="Methane alarm triggered in Section D", description="Continuous methane alarm sounding in Section D. Workers evacuated. Sensor readings confirmed at 2.1%.", latitude=23.9500, longitude=85.3600, location_label="Section D, Hazaribagh South"),
            FieldReport(report_code="FR-2026-0007", mine_id=11, reporter_id=6, reporter_name="Inspector P. Verma", observation_type="safety", severity="high", title="Ventilation system alarm in Level 3", description="Low airflow alarm triggered in Level 3. Primary fan appears to have mechanical failure.", latitude=23.6100, longitude=87.1500, location_label="Level 3, Raniganj Area"),
            FieldReport(report_code="FR-2026-0008", mine_id=9, reporter_id=6, reporter_name="Inspector P. Verma", observation_type="general", severity="low", title="Best practice observation", description="Excellent implementation of color-coded PPE system at Korba West. Recommend replicating across all mines.", latitude=22.3500, longitude=82.7000, location_label="Main Pit, Korba West"),
            FieldReport(report_code="FR-2026-0009", mine_id=10, reporter_id=3, reporter_name="Inspector R.K. Sharma", observation_type="environment", severity="medium", title="Noise level concern at boundary", description="Elevated noise levels observed at mine boundary. Measurements needed to confirm compliance.", latitude=20.9500, longitude=85.2100, location_label="Boundary, Talcher"),
            FieldReport(report_code="FR-2026-0010", mine_id=5, reporter_id=6, reporter_name="Inspector P. Verma", observation_type="safety", severity="low", title="Good safety practice observed", description="All workers observed with complete PPE including respiratory protection in dusty sections. Safety briefing records well maintained.", latitude=23.7473, longitude=86.4304, location_label="Active Zone, Jharia West"),
        ]
        db.add_all(field_reports)
        db.flush()

        # ===== ALERTS (20) =====
        alerts = [
            Alert(mine_id=1, mine_name="Rajmahal Coal Mine", type="compliance", severity="critical", title="Environmental compliance overdue — Rajmahal Mine", message="Environmental monitoring report has been overdue for 23 days. Immediate submission required to avoid regulatory penalty.", status="active", escalation_level=2, source="system"),
            Alert(mine_id=2, mine_name="Godda East Mine", type="safety", severity="critical", title="Fire safety certificate expires in 2 days", message="Fire safety certificate for Godda East Mine expires on September 14, 2026. Renewal must be completed immediately.", status="active", escalation_level=1, source="system"),
            Alert(mine_id=1, mine_name="Rajmahal Coal Mine", type="safety", severity="critical", title="Critical PPE violation — 4th consecutive occurrence", message="PPE non-compliance has been observed in 4 consecutive inspections at Rajmahal Mine. Systemic issue requiring management intervention.", status="active", escalation_level=3, source="ai"),
            Alert(mine_id=3, mine_name="Kathara Deep Mine", type="equipment", severity="high", title="Equipment maintenance overdue — 3 units", message="3 pieces of heavy machinery have overdue maintenance certifications at Kathara Deep Mine.", status="active", escalation_level=1, source="system"),
            Alert(mine_id=1, mine_name="Rajmahal Coal Mine", type="safety", severity="high", title="Roof support deficiency detected", message="Geotechnical assessment indicates roof support in Gallery 7 requires immediate reinforcement.", status="active", escalation_level=1, source="inspector"),
            Alert(mine_id=5, mine_name="Jharia West Mine", type="compliance", severity="warning", title="Safety inspection due in 5 days", message="Monthly safety inspection for Jharia West Mine is due on September 17, 2026.", status="active", source="system"),
            Alert(mine_id=8, mine_name="Dhanbad North Mine", type="safety", severity="high", title="Water seepage detected in tunnel", message="Water seepage observed in lower level access tunnel. Structural assessment required.", status="active", escalation_level=1, source="inspector"),
            Alert(mine_id=1, mine_name="Rajmahal Coal Mine", type="compliance", severity="warning", title="Production below target — 27% deviation", message="Production at Rajmahal Mine has been consistently 27% below target for the last 10 days.", status="active", source="ai"),
            Alert(mine_id=6, mine_name="Mugma Colliery", type="equipment", severity="warning", title="Conveyor belt wear detected", message="Conveyor belt showing excessive wear. Replacement should be scheduled within 30 days.", status="active", source="system"),
            Alert(mine_id=7, mine_name="Sonepur Bazari Mine", type="compliance", severity="info", title="Quarterly compliance report submitted", message="Q2 2026 compliance report for Sonepur Bazari Mine has been submitted and verified.", status="resolved", source="system"),
            Alert(mine_id=4, mine_name="Bokaro Central Mine", type="safety", severity="info", title="Ventilation monitoring installed", message="Additional ventilation monitoring sensors installed in Section C as per corrective action CA-2026-0008.", status="resolved", source="system"),
            Alert(mine_id=1, mine_name="Rajmahal Coal Mine", type="safety", severity="critical", title="Fire extinguisher expired in Section B", message="Fire extinguishers in Section B found expired. Immediate replacement required per Coal Mines Regulations, 2017.", status="active", escalation_level=2, source="inspector"),
            Alert(mine_id=2, mine_name="Godda East Mine", type="environment", severity="high", title="PM2.5 levels exceed limit", message="PM2.5 levels recorded at 68 µg/m³ against limit of 60 µg/m³. Corrective measures required.", status="active", source="system"),
            Alert(mine_id=12, mine_name="Hazaribagh South Mine", type="safety", severity="critical", title="Methane levels exceeding safe limit — EMERGENCY", message="Methane sensor readings at 2.1% in Section D. Workers evacuated. Mine operations suspended until further notice.", status="active", escalation_level=3, source="system"),
            Alert(mine_id=12, mine_name="Hazaribagh South Mine", type="equipment", severity="critical", title="Hoist rope deterioration — immediate replacement", message="Wire rope on main winding engine shows 12% diameter reduction exceeding the 10% discard threshold. Statutory replacement required.", status="active", escalation_level=2, source="inspector"),
            Alert(mine_id=11, mine_name="Raniganj Area Mine", type="safety", severity="high", title="Ventilation failure in Level 3", message="Primary ventilation fan non-functional. Backup system running at reduced capacity.", status="active", escalation_level=1, source="system"),
            Alert(mine_id=9, mine_name="Korba West OCP", type="compliance", severity="info", title="All compliance requirements up to date", message="Korba West OCP has met all compliance requirements for September 2026.", status="resolved", source="system"),
            Alert(mine_id=10, mine_name="Talcher Coalfield", type="environment", severity="warning", title="Noise levels approaching limit at boundary", message="Daytime noise levels at 72 dB approaching the 75 dB limit. Monitoring recommended.", status="active", source="system"),
            Alert(mine_id=12, mine_name="Hazaribagh South Mine", type="compliance", severity="critical", title="Mine operations suspended", message="Operations at Hazaribagh South Mine suspended due to multiple critical safety violations.", status="active", escalation_level=3, source="authority"),
            Alert(mine_id=3, mine_name="Kathara Deep Mine", type="labour", severity="warning", title="Contractor compliance review due", message="Monthly contractor compliance review for Singh Transport Co is due in 3 days.", status="active", source="system"),
        ]
        db.add_all(alerts)
        db.flush()

        # ===== AUDIT LOGS (120) =====
        actions = ["login", "created", "updated", "uploaded", "verified", "submitted", "viewed", "generated", "exported", "archived"]
        modules = ["auth", "mines", "compliance", "inspections", "violations", "corrective_actions", "documents", "reports", "field_reports", "contractors"]
        for i in range(1, 121):
            user_id = (i % len(users)) + 1
            user = users[user_id - 1]
            action = actions[i % len(actions)]
            module = modules[i % len(modules)]
            db.add(AuditLog(
                user_id=user.id, user_name=user.name, user_role=user.role,
                action=action, module=module,
                entity=module.rstrip("s"), entity_id=i,
                details=f"{user.name} {action} {module} record #{i}",
                status="success",
                created_at=now - timedelta(hours=i),
            ))
        db.flush()

        # ===== DOCUMENTS (8) =====
        docs = [
            Document(name="Safety_Inspection_Report_Rajmahal_Aug2026.pdf", document_type="inspection_report", mine_id=1, uploaded_by=2, uploaded_by_name="Shri Amit Kumar Singh", processing_status="completed"),
            Document(name="Environmental_Monitoring_Q2_Godda.pdf", document_type="environmental_clearance", mine_id=2, uploaded_by=8, uploaded_by_name="Shri Suresh Yadav", processing_status="completed"),
            Document(name="Fire_Safety_Certificate_Kathara.pdf", document_type="safety_certificate", mine_id=3, uploaded_by=7, uploaded_by_name="Shri Deepak Pandey", processing_status="completed"),
            Document(name="Mine_Closure_Plan_Korba_2026.pdf", document_type="mine_plan", mine_id=9, uploaded_by=1, uploaded_by_name="Dr. Arun Kumar Verma", processing_status="completed"),
            Document(name="Contractor_Compliance_Review_Sep2026.docx", document_type="compliance_report", mine_id=1, uploaded_by=2, uploaded_by_name="Shri Amit Kumar Singh", processing_status="completed"),
            Document(name="Methane_Monitoring_Report_Hazaribagh.pdf", document_type="safety_report", mine_id=12, uploaded_by=1, uploaded_by_name="Dr. Arun Kumar Verma", processing_status="completed"),
            Document(name="PPE_Audit_Report_Jharia_Sep2026.pdf", document_type="inspection_report", mine_id=5, uploaded_by=3, uploaded_by_name="Inspector R.K. Sharma", processing_status="completed"),
            Document(name="Production_Report_Talcher_Aug2026.xlsx", document_type="production_report", mine_id=10, uploaded_by=10, uploaded_by_name="Smt. Kavita Devi", processing_status="completed"),
        ]
        db.add_all(docs)
        db.flush()

        # ===== NOTIFICATIONS (for demo users) =====
        notification_data = [
            # Admin notifications
            (1, "New violation reported", "Critical violation VIO-2026-0020 (Methane levels exceeding safe limit) reported at Hazaribagh South Mine", "violation", "critical", "/app/violations"),
            (1, "Mine operations suspended", "Hazaribagh South Mine operations suspended due to critical safety violations", "alert", "critical", "/app/alerts"),
            (1, "Monthly compliance report ready", "September 2026 compliance report is ready for review", "report", "info", "/app/reports"),
            # Mine Manager (Rajmahal)
            (2, "Corrective action deadline approaching", "CA-2026-0002 (Replace fire extinguishers) deadline in 3 days", "corrective_action", "high", "/app/corrective-actions"),
            (2, "New inspection scheduled", "Safety inspection scheduled for September 15, 2026", "inspection", "info", "/app/inspections"),
            (2, "Production alert", "Production has been 27% below target for the last 10 days", "production", "warning", "/app/production"),
            (2, "Violation assigned to you", "VIO-2026-0016 (PPE Violation - Respiratory Protection) assigned for resolution", "violation", "high", "/app/violations"),
            # Inspector
            (3, "Inspection due", "Routine safety inspection at Jharia West Mine due on September 17, 2026", "inspection", "info", "/app/inspections"),
            (3, "Corrective action submitted for verification", "CA-2026-0007 (Replenish first aid kits) submitted with evidence", "corrective_action", "info", "/app/corrective-actions"),
            (3, "High-risk mine alert", "Hazaribagh South Mine risk score at 88 — requires immediate inspection", "risk", "critical", "/app/risk"),
            # Corporate
            (4, "Quarterly compliance report overdue", "ECL subsidiary quarterly compliance report is 5 days overdue", "compliance", "high", "/app/compliance"),
            (4, "Risk dashboard updated", "Risk scores recalculated for all mines. 3 mines in critical risk zone.", "risk", "warning", "/app/risk"),
            # Authority
            (5, "Mine suspension notice", "Hazaribagh South Mine suspended due to methane exceedance", "alert", "critical", "/app/alerts"),
            (5, "Recurring violation pattern detected", "AI analysis detected recurring PPE violations at Rajmahal Coal Mine (4 occurrences)", "violation", "high", "/app/violations"),
            (5, "New environmental non-compliance", "Godda East Mine PM2.5 levels exceed prescribed limits", "compliance", "high", "/app/compliance"),
        ]
        for user_id, title, message, ntype, severity, link in notification_data:
            db.add(Notification(
                user_id=user_id, title=title, message=message,
                type=ntype, severity=severity, link=link,
            ))
        db.flush()

        db.commit()
        print("[OK] Database seeded successfully!")
        print(f"   - {len(users)} users")
        print(f"   - {len(subsidiaries)} subsidiaries")
        print(f"   - {len(mines)} mines")
        print(f"   - {len(requirements)} compliance requirements")
        print(f"   - {len(records)} compliance records")
        print(f"   - {len(violations)} violations")
        print(f"   - {len(corrective_actions)} corrective actions")
        print(f"   - 25 inspections")
        print(f"   - {len(contractors)} contractors")
        print(f"   - 120 workers")
        print(f"   - ~840 attendance records")
        print(f"   - 180 production records")
        print(f"   - {len(field_reports)} field reports")
        print(f"   - {len(alerts)} alerts")
        print(f"   - 120 audit logs")
        print(f"   - {len(docs)} documents")
        print(f"   - {len(notification_data)} notifications")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
