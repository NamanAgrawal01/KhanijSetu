"""
KhanijSetu Fallback AI — Rule-based demo intelligence.

Provides realistic, explainable AI responses without requiring an external API.
All responses include reasoning and supporting data.
"""
import re
import random
from datetime import datetime, date


class FallbackAI:

    def analyze_document(self, text: str, filename: str = "", mine_name: str = "") -> dict:
        """Rule-based document analysis with issue detection."""
        text_lower = text.lower() if text else ""
        filename_lower = filename.lower() if filename else ""

        # Detect document type
        doc_type = "General Document"
        if any(w in filename_lower or w in text_lower for w in ["inspection", "inspect"]):
            doc_type = "Inspection Report"
        elif any(w in filename_lower or w in text_lower for w in ["safety", "fire"]):
            doc_type = "Safety Certificate"
        elif any(w in filename_lower or w in text_lower for w in ["environment", "pollution", "emission"]):
            doc_type = "Environmental Clearance"
        elif any(w in filename_lower or w in text_lower for w in ["compliance", "statutory"]):
            doc_type = "Compliance Report"
        elif any(w in filename_lower or w in text_lower for w in ["production", "output"]):
            doc_type = "Production Report"

        issues = []
        recommendations = []

        # Check for overdue / expiry keywords
        if any(w in text_lower for w in ["overdue", "expired", "lapsed", "not compliant"]):
            issues.append({
                "severity": "high",
                "description": "Document indicates overdue or expired compliance items",
                "regulation": "Mines Act, 1952 - Section 22"
            })
            recommendations.append("Schedule immediate review and renewal of expired certifications")

        if any(w in text_lower for w in ["fire safety", "fire extinguisher", "fire drill"]):
            issues.append({
                "severity": "high",
                "description": "Fire safety inspection findings require immediate attention",
                "regulation": "Coal Mines Regulations, 2017 - Regulation 186"
            })
            recommendations.append("Schedule immediate fire safety inspection and update compliance evidence")

        if any(w in text_lower for w in ["ppe", "personal protective", "helmet", "safety gear"]):
            issues.append({
                "severity": "medium",
                "description": "PPE compliance observations detected in document",
                "regulation": "Mines Rules, 1955 - Rule 29"
            })
            recommendations.append("Conduct PPE audit and ensure all workers have current safety equipment")

        if any(w in text_lower for w in ["missing", "incomplete", "not found", "absent"]):
            issues.append({
                "severity": "medium",
                "description": "Missing documentation or evidence identified",
                "regulation": "DGMS Circular - Documentation Requirements"
            })
            recommendations.append("Complete missing documentation and submit to compliance officer")

        if any(w in text_lower for w in ["emission", "pollution", "dust", "discharge"]):
            issues.append({
                "severity": "medium",
                "description": "Environmental compliance concerns identified",
                "regulation": "Environment Protection Act, 1986"
            })
            recommendations.append("Review environmental monitoring data and submit updated readings")

        # If no specific issues found, add demo issues
        if not issues:
            issues = [
                {"severity": "high", "description": "Fire safety certificate requires renewal - expires within 30 days", "regulation": "Coal Mines Regulations, 2017"},
                {"severity": "medium", "description": "Missing evidence for quarterly safety inspection", "regulation": "Mines Act, 1952"},
                {"severity": "low", "description": "Document formatting does not follow standard template", "regulation": "Internal Policy"}
            ]
            recommendations = [
                "Schedule immediate fire safety inspection and certificate renewal",
                "Upload quarterly safety inspection evidence within 7 days",
                "Update document to follow the standardized compliance template"
            ]

        key_findings = [
            "Document processed and analyzed successfully",
            f"Document type identified as: {doc_type}",
            f"Total issues detected: {len(issues)}",
            f"High severity issues: {sum(1 for i in issues if i['severity'] == 'high')}",
        ]

        return {
            "summary": f"Analysis of '{filename or 'uploaded document'}' reveals {len(issues)} compliance-related findings. "
                       f"The document has been classified as a {doc_type}. "
                       f"{sum(1 for i in issues if i['severity'] == 'high')} high-severity issues require immediate attention.",
            "document_category": doc_type,
            "extracted_mine": mine_name or "Not specified in document",
            "extracted_date": datetime.now().strftime("%d %b %Y"),
            "extracted_inspector": "Auto-detected from document",
            "extracted_expiry": "Review required",
            "key_findings": key_findings,
            "issues_high": sum(1 for i in issues if i["severity"] == "high"),
            "issues_medium": sum(1 for i in issues if i["severity"] == "medium"),
            "issues_low": sum(1 for i in issues if i["severity"] == "low"),
            "issues_details": issues,
            "recommendations": recommendations,
            "compliance_status": "requires_review" if any(i["severity"] == "high" for i in issues) else "acceptable",
            "risk_indicators": ["overdue_compliance", "documentation_gap"] if issues else [],
            "confidence_score": 0.82
        }

    def explain_risk(self, mine_data: dict) -> dict:
        """Generate explainable risk scoring with factor breakdown."""
        risk_score = mine_data.get("risk_score", 50)
        name = mine_data.get("name", "Mine")
        compliance = mine_data.get("compliance_score", 75)
        violations = mine_data.get("open_violations", 0)
        safety = mine_data.get("safety_score", 70)

        if risk_score >= 75:
            level = "HIGH"
        elif risk_score >= 50:
            level = "MEDIUM"
        elif risk_score >= 25:
            level = "LOW"
        else:
            level = "MINIMAL"

        factors = []
        total_weight = 0

        if violations > 5:
            w = 30
            factors.append({"factor": "Safety Violations", "weight": w, "detail": f"{violations} open violations pending resolution"})
            total_weight += w
        elif violations > 0:
            w = 15
            factors.append({"factor": "Safety Violations", "weight": w, "detail": f"{violations} open violations"})
            total_weight += w

        if compliance < 70:
            w = 25
            factors.append({"factor": "Overdue Compliance", "weight": w, "detail": f"Compliance score at {compliance}%, below acceptable threshold of 70%"})
            total_weight += w
        elif compliance < 85:
            w = 10
            factors.append({"factor": "Compliance Gap", "weight": w, "detail": f"Compliance score at {compliance}%"})
            total_weight += w

        if safety < 65:
            w = 20
            factors.append({"factor": "Safety Deficiency", "weight": w, "detail": f"Safety score at {safety}%, indicating systemic safety issues"})
            total_weight += w

        remaining = 100 - total_weight
        if remaining > 0:
            factors.append({"factor": "Environmental Factors", "weight": min(remaining, 20), "detail": "Environmental monitoring within acceptable range"})
            remaining -= min(remaining, 20)
        if remaining > 0:
            factors.append({"factor": "Historical Incidents", "weight": remaining, "detail": "Historical incident record factored into assessment"})

        explanation_parts = [f"{name} is classified as {level} RISK (Score: {risk_score}/100)."]
        if level in ["HIGH", "MEDIUM"]:
            explanation_parts.append("Primary contributing factors include:")
            for f in factors[:3]:
                explanation_parts.append(f"• {f['detail']}")

        recommendations = []
        if violations > 5:
            recommendations.append("Prioritize resolution of open safety violations within 14 days")
        if compliance < 70:
            recommendations.append("Conduct comprehensive compliance audit and address overdue requirements")
        if safety < 65:
            recommendations.append("Implement targeted safety improvement program with weekly monitoring")
        recommendations.append("Schedule follow-up risk assessment within 30 days")

        return {
            "risk_score": risk_score,
            "risk_level": level,
            "factors": factors,
            "explanation": " ".join(explanation_parts),
            "recommendations": recommendations,
            "trend": [
                {"month": "Apr", "score": max(30, risk_score - 15)},
                {"month": "May", "score": max(30, risk_score - 10)},
                {"month": "Jun", "score": max(30, risk_score - 5)},
                {"month": "Jul", "score": risk_score - 3},
                {"month": "Aug", "score": risk_score + 2},
                {"month": "Sep", "score": risk_score},
            ]
        }

    def detect_anomalies(self, data: dict) -> dict:
        """Detect operational anomalies using statistical deviation."""
        anomalies = []
        target = data.get("target", 1000)
        actual = data.get("actual", 730)
        deviation = ((target - actual) / target) * 100 if target > 0 else 0

        if deviation > 20:
            anomalies.append({
                "type": "production_deviation",
                "severity": "high",
                "title": "OPERATIONAL ANOMALY DETECTED",
                "description": f"Production is {deviation:.0f}% below the recent baseline.",
                "possible_factors": [
                    "Equipment downtime exceeding normal maintenance window",
                    "Workforce shortage due to seasonal attendance patterns",
                    "Geological conditions affecting extraction rate"
                ]
            })

        return {
            "anomalies_detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def answer_query(self, query: str, context: dict = None) -> dict:
        """Intent-based query answering using keyword matching with database context."""
        query_lower = query.lower()
        context = context or {}

        # Extract database context
        mines_data = context.get("mines", [])
        total_mines = context.get("total_mines", len(mines_data))
        open_violations = context.get("open_violations", 0)
        critical_alerts = context.get("critical_alerts", 0)
        overdue_compliance = context.get("overdue_compliance", 0)
        pending_actions = context.get("pending_actions", 0)
        high_risk_names = context.get("high_risk_mines", [])

        # Sort mines by risk
        high_risk_mines = sorted([m for m in mines_data if m.get("risk_score", 0) >= 70], key=lambda x: x.get("risk_score", 0), reverse=True)
        avg_compliance = sum(m.get("compliance_score", 75) for m in mines_data) / max(len(mines_data), 1)

        # Intent: High-risk mines
        if any(w in query_lower for w in ["attention", "high risk", "critical", "urgent", "immediate"]):
            mine_details = ""
            entities = []
            for i, m in enumerate(high_risk_mines[:5], 1):
                mine_details += f"\n{i}. **{m['name']}** — Risk Score: {m['risk_score']}/100\n   • {m.get('open_violations', 0)} open violations\n   • Compliance: {m.get('compliance_score', 0)}%\n   • Status: {m.get('status', 'operational')}\n"
                entities.append({"name": m["name"], "risk_score": m["risk_score"], "type": "mine"})

            if not mine_details:
                mine_details = "\nNo mines currently classified as high risk. All mines operating within acceptable parameters.\n"

            return {
                "answer": f"Based on current risk assessments, **{len(high_risk_mines)}** mines require immediate attention:\n{mine_details}\n"
                          f"**Recommended Actions:**\n"
                          f"• Schedule immediate safety inspections at all high-risk mines\n"
                          f"• Assign dedicated compliance officers\n"
                          f"• Escalate overdue items to regional management",
                "data": {"high_risk_count": len(high_risk_mines), "total_mines": total_mines},
                "entities": entities,
                "recommendations": [
                    "Schedule immediate safety inspections at high-risk mines",
                    "Assign dedicated compliance officers to address overdue items",
                    "Escalate unresolved corrective actions to regional management",
                    "Review contractor safety performance at affected mines"
                ],
                "confidence": 0.88
            }

        # Intent: Specific mine risk
        if any(w in query_lower for w in ["why", "reason", "explain"]) and any(w in query_lower for w in ["risk", "high", "score"]):
            target_mine = high_risk_mines[0] if high_risk_mines else (mines_data[0] if mines_data else {"name": "Mine", "risk_score": 50, "compliance_score": 75, "open_violations": 0})
            return {
                "answer": f"**Risk Analysis — {target_mine['name']}**\n\n"
                          f"Current Risk Score: **{target_mine['risk_score']}/100**\n\n"
                          f"The elevated risk is primarily due to:\n\n"
                          f"• **{target_mine.get('open_violations', 0)} open violations** pending resolution\n"
                          f"• **Compliance score at {target_mine.get('compliance_score', 0)}%** — below acceptable threshold\n"
                          f"• **Status: {target_mine.get('status', 'operational')}**\n\n"
                          f"The risk score factors in safety violations, overdue compliance requirements, "
                          f"and historical inspection findings.",
                "data": {"risk_score": target_mine["risk_score"], "compliance": target_mine.get("compliance_score", 75)},
                "entities": [{"name": target_mine["name"], "risk_score": target_mine["risk_score"], "type": "mine"}],
                "recommendations": [
                    f"Address the {target_mine.get('open_violations', 0)} open violations within 7 days",
                    "Implement targeted safety improvement program",
                    "Resolve pending corrective actions immediately",
                    "Schedule follow-up risk assessment within 30 days"
                ],
                "confidence": 0.90
            }

        # Intent: Recurring violations
        if any(w in query_lower for w in ["recurring", "repeated", "pattern", "violation"]):
            return {
                "answer": f"**Recurring Violation Analysis**\n\n"
                          f"Currently tracking **{open_violations} open violations** across {total_mines} mines.\n\n"
                          f"Common recurring patterns include:\n\n"
                          f"1. **PPE Non-Compliance** — observed across multiple inspections at high-risk mines\n"
                          f"2. **Equipment Maintenance Delays** — overdue certifications at several mines\n"
                          f"3. **Environmental Reporting Gaps** — late submissions for quarterly reports\n\n"
                          f"**AI Insight:** Repeated violations indicate persistent compliance weaknesses. "
                          f"Recommend targeted training programs and increased inspection frequency.",
                "data": {"open_violations": open_violations, "high_risk_mines": len(high_risk_mines)},
                "entities": [{"name": m["name"], "risk_score": m["risk_score"], "type": "mine"} for m in high_risk_mines[:3]],
                "recommendations": [
                    "Implement mandatory PPE training program across affected mines",
                    "Establish automated equipment maintenance scheduling",
                    "Set up automated reminders for environmental reporting deadlines"
                ],
                "confidence": 0.85
            }

        # Intent: Contractor performance
        if any(w in query_lower for w in ["contractor", "vendor", "performance"]):
            return {
                "answer": "**Contractor Safety Performance Summary**\n\n"
                          "Contractors with poor safety performance:\n\n"
                          "1. **Bharat Mining Services** — Safety Score: 52/100\n"
                          "   • 5 safety violations in last quarter\n"
                          "   • 2 workers found without PPE\n\n"
                          "2. **Eastern Excavators Pvt Ltd** — Safety Score: 61/100\n"
                          "   • 3 equipment-related incidents\n"
                          "   • Training compliance at 68%\n\n"
                          "All other contractors are within acceptable safety thresholds (>70/100).",
                "data": {"total_contractors": 10, "non_compliant": 2},
                "entities": [
                    {"name": "Bharat Mining Services", "safety_score": 52, "type": "contractor"},
                    {"name": "Eastern Excavators Pvt Ltd", "safety_score": 61, "type": "contractor"},
                ],
                "recommendations": [
                    "Issue safety improvement notice to Bharat Mining Services",
                    "Mandate additional safety training for Eastern Excavators workforce",
                    "Consider contract review for persistently non-compliant contractors"
                ],
                "confidence": 0.83
            }

        # Intent: Compliance due
        if any(w in query_lower for w in ["due", "week", "upcoming", "pending", "deadline"]):
            return {
                "answer": f"**Compliance Actions Due**\n\n"
                          f"**{overdue_compliance}** compliance items currently overdue\n"
                          f"**{pending_actions}** corrective actions pending\n\n"
                          f"Priority items include:\n\n"
                          f"• Fire safety certificate renewals at mines with expiring certificates\n"
                          f"• Environmental monitoring reports for the current quarter\n"
                          f"• Equipment safety certifications approaching expiry\n\n"
                          f"**Priority:** Address overdue items immediately to avoid regulatory penalties.",
                "data": {"overdue": overdue_compliance, "pending_actions": pending_actions},
                "entities": [{"name": m["name"], "type": "mine"} for m in high_risk_mines[:3]],
                "recommendations": [
                    "Process overdue compliance items immediately",
                    "Assign inspectors for pending monthly inspections",
                    "Send automated reminders to responsible officers"
                ],
                "confidence": 0.87
            }

        # Intent: Governance summary
        if any(w in query_lower for w in ["summarize", "summary", "overview", "governance", "situation", "status"]):
            return {
                "answer": f"**Governance Situation Summary**\n\n"
                          f"**Overall Status:** {'Critical attention needed' if len(high_risk_mines) > 3 else 'Moderate with areas requiring attention'}\n\n"
                          f"📊 **Key Metrics:**\n"
                          f"• Total mines monitored: {total_mines}\n"
                          f"• Overall compliance: {avg_compliance:.1f}%\n"
                          f"• High-risk mines: {len(high_risk_mines)}\n"
                          f"• Open violations: {open_violations}\n"
                          f"• Critical alerts: {critical_alerts}\n"
                          f"• Pending corrective actions: {pending_actions}\n\n"
                          f"⚠️ **Areas of Concern:**\n"
                          f"• {len(high_risk_mines)} mines classified as high risk\n"
                          f"• {overdue_compliance} compliance requirements overdue\n"
                          f"• {critical_alerts} critical alerts active",
                "data": {"compliance": round(avg_compliance, 1), "high_risk": len(high_risk_mines), "violations": open_violations},
                "entities": [{"name": m["name"], "risk_score": m["risk_score"], "type": "mine"} for m in high_risk_mines[:5]],
                "recommendations": [
                    f"Focus immediate attention on the {len(high_risk_mines)} high-risk mines",
                    "Address recurring violations through training programs",
                    f"Resolve {critical_alerts} critical alerts within 7 days",
                    "Improve compliance across all subsidiaries"
                ],
                "confidence": 0.86
            }

        # Default response
        return {
            "answer": f"I've analyzed your query about '{query}'. Based on current mining governance data:\n\n"
                      f"The platform is monitoring **{total_mines} mines** across {len(set(m.get('status','') for m in mines_data))} operational states. "
                      f"Overall compliance stands at **{avg_compliance:.1f}%** with {len(high_risk_mines)} mines requiring elevated attention.\n\n"
                      f"Current status: {open_violations} open violations, {critical_alerts} critical alerts, "
                      f"{pending_actions} pending corrective actions.\n\n"
                      f"For more specific insights, try asking:\n"
                      f"• \"Which mines require immediate attention?\"\n"
                      f"• \"Show recurring violations\"\n"
                      f"• \"What compliance actions are due this week?\"\n"
                      f"• \"Summarize the governance situation\"",
            "data": None,
            "entities": [],
            "recommendations": [
                "Review high-risk mine profiles for detailed analysis",
                "Check the compliance dashboard for overdue items",
                "Review recent field reports for operational insights"
            ],
            "confidence": 0.70
        }

        # Intent: High-risk mines
        if any(w in query_lower for w in ["attention", "high risk", "critical", "urgent", "immediate"]):
            return {
                "answer": "Based on current risk assessments, the following mines require immediate attention:\n\n"
                          "1. **Rajmahal Coal Mine** — Risk Score: 82/100 (HIGH)\n"
                          "   • 4 overdue safety requirements\n"
                          "   • 3 recurring PPE violations\n"
                          "   • 2 unresolved corrective actions\n\n"
                          "2. **Godda East Mine** — Risk Score: 76/100 (HIGH)\n"
                          "   • Environmental compliance overdue by 15 days\n"
                          "   • Fire safety certificate expiring\n\n"
                          "3. **Kathara Deep Mine** — Risk Score: 71/100 (HIGH)\n"
                          "   • 3 open safety violations\n"
                          "   • Equipment maintenance backlog\n\n"
                          "**Recommended Actions:**\n"
                          "• Schedule immediate safety inspections at all three mines\n"
                          "• Assign dedicated compliance officers\n"
                          "• Escalate overdue items to regional management",
                "data": {"high_risk_count": 3, "total_mines": 48},
                "entities": [
                    {"name": "Rajmahal Coal Mine", "risk_score": 82, "type": "mine"},
                    {"name": "Godda East Mine", "risk_score": 76, "type": "mine"},
                    {"name": "Kathara Deep Mine", "risk_score": 71, "type": "mine"},
                ],
                "recommendations": [
                    "Schedule immediate safety inspections at high-risk mines",
                    "Assign dedicated compliance officers to address overdue items",
                    "Escalate unresolved corrective actions to regional management",
                    "Review contractor safety performance at affected mines"
                ],
                "confidence": 0.88
            }

        # Intent: Specific mine risk
        if any(w in query_lower for w in ["why", "reason", "explain"]) and any(w in query_lower for w in ["risk", "high", "score"]):
            return {
                "answer": "**Risk Analysis — Rajmahal Coal Mine**\n\n"
                          "Current Risk Score: **82/100 (HIGH)**\n\n"
                          "The elevated risk is primarily due to:\n\n"
                          "• **4 overdue safety requirements** — Including fire safety inspection (overdue 23 days) "
                          "and emergency evacuation drill (overdue 11 days)\n"
                          "• **3 recurring PPE violations** — PPE non-compliance observed in 4 consecutive inspections, "
                          "indicating a persistent systemic issue\n"
                          "• **2 unresolved corrective actions** — Both past their deadlines by more than 14 days\n"
                          "• **Environmental compliance** — Dust monitoring report pending for current quarter\n\n"
                          "The risk score has increased from 64 to 82 over the past 3 months, "
                          "primarily driven by accumulating unresolved violations.",
                "data": {"risk_score": 82, "previous_score": 64, "trend": "increasing"},
                "entities": [{"name": "Rajmahal Coal Mine", "risk_score": 82, "type": "mine"}],
                "recommendations": [
                    "Address the 4 overdue safety requirements within 7 days",
                    "Implement mandatory PPE training program",
                    "Resolve pending corrective actions immediately",
                    "Submit environmental monitoring reports"
                ],
                "confidence": 0.90
            }

        # Intent: Recurring violations
        if any(w in query_lower for w in ["recurring", "repeated", "pattern", "violation"]):
            return {
                "answer": "**Recurring Violation Analysis (Last 6 Months)**\n\n"
                          "The following violation patterns have been detected:\n\n"
                          "1. **PPE Non-Compliance** — 4 consecutive inspections\n"
                          "   Mines: Rajmahal, Godda East, Kathara Deep\n"
                          "   Pattern: Workers found without proper PPE in active zones\n\n"
                          "2. **Equipment Maintenance Delays** — 3 occurrences\n"
                          "   Mines: Kathara Deep, Bokaro Central\n"
                          "   Pattern: Heavy machinery maintenance logs overdue\n\n"
                          "3. **Environmental Reporting Gaps** — 2 occurrences\n"
                          "   Mines: Godda East\n"
                          "   Pattern: Quarterly emission reports submitted late\n\n"
                          "**AI Insight:** Repeated PPE-related observations indicate persistent compliance weakness. "
                          "Recommend targeted safety training program and increased inspection frequency.",
                "data": {"recurring_types": 3, "total_occurrences": 9},
                "entities": [
                    {"name": "PPE Non-Compliance", "count": 4, "type": "violation"},
                    {"name": "Equipment Maintenance", "count": 3, "type": "violation"},
                ],
                "recommendations": [
                    "Implement mandatory PPE training program across affected mines",
                    "Establish automated equipment maintenance scheduling",
                    "Set up automated reminders for environmental reporting deadlines"
                ],
                "confidence": 0.85
            }

        # Intent: Contractor performance
        if any(w in query_lower for w in ["contractor", "vendor", "performance"]):
            return {
                "answer": "**Contractor Safety Performance Summary**\n\n"
                          "Contractors with poor safety performance:\n\n"
                          "1. **Bharat Mining Services** — Safety Score: 52/100\n"
                          "   • 5 safety violations in last quarter\n"
                          "   • 2 workers found without PPE\n\n"
                          "2. **Eastern Excavators Pvt Ltd** — Safety Score: 61/100\n"
                          "   • 3 equipment-related incidents\n"
                          "   • Training compliance at 68%\n\n"
                          "All other contractors are within acceptable safety thresholds (>70/100).",
                "data": {"total_contractors": 8, "non_compliant": 2},
                "entities": [
                    {"name": "Bharat Mining Services", "safety_score": 52, "type": "contractor"},
                    {"name": "Eastern Excavators Pvt Ltd", "safety_score": 61, "type": "contractor"},
                ],
                "recommendations": [
                    "Issue safety improvement notice to Bharat Mining Services",
                    "Mandate additional safety training for Eastern Excavators workforce",
                    "Consider contract review for persistently non-compliant contractors"
                ],
                "confidence": 0.83
            }

        # Intent: Compliance due
        if any(w in query_lower for w in ["due", "week", "upcoming", "pending", "deadline"]):
            return {
                "answer": "**Compliance Actions Due This Week**\n\n"
                          "5 compliance actions require attention:\n\n"
                          "1. Fire Safety Certificate renewal — Rajmahal Mine (Due: Tomorrow)\n"
                          "2. Monthly Safety Inspection — Godda East Mine (Due: 2 days)\n"
                          "3. Environmental Monitoring Report — Kathara Deep Mine (Due: 3 days)\n"
                          "4. Equipment Maintenance Log — Bokaro Central Mine (Due: 4 days)\n"
                          "5. Worker Training Verification — Jharia West Mine (Due: 5 days)\n\n"
                          "**Priority:** Items 1 and 2 are high-priority and should be addressed immediately.",
                "data": {"due_this_week": 5, "overdue": 2},
                "entities": [
                    {"name": "Rajmahal Coal Mine", "due_date": "Tomorrow", "type": "mine"},
                    {"name": "Godda East Mine", "due_date": "2 days", "type": "mine"},
                ],
                "recommendations": [
                    "Process fire safety certificate renewal immediately",
                    "Assign inspector for Godda East monthly inspection",
                    "Send automated reminders to responsible officers"
                ],
                "confidence": 0.87
            }

        # Intent: Governance summary
        if any(w in query_lower for w in ["summarize", "summary", "overview", "governance", "situation", "status"]):
            return {
                "answer": "**Governance Situation Summary**\n\n"
                          "**Overall Status:** Moderate with areas requiring attention\n\n"
                          "📊 **Key Metrics:**\n"
                          "• Total mines monitored: 48\n"
                          "• Overall compliance: 78% (↑ 4.2% vs last month)\n"
                          "• High-risk mines: 9 (18.7%)\n"
                          "• Open violations: 37\n"
                          "• Pending corrective actions: 12\n\n"
                          "📈 **Positive Trends:**\n"
                          "• Overall compliance improved by 4.2%\n"
                          "• 15 violations resolved in the last 30 days\n"
                          "• Inspector report submission rate improved to 94%\n\n"
                          "⚠️ **Areas of Concern:**\n"
                          "• 9 mines classified as high risk (up from 7 last month)\n"
                          "• PPE violations recurring across 3 mines\n"
                          "• 7 critical issues awaiting resolution\n"
                          "• Fire safety compliance at 65% across subsidiary ECL",
                "data": {"compliance": 78, "high_risk": 9, "violations": 37},
                "entities": [],
                "recommendations": [
                    "Focus immediate attention on the 9 high-risk mines",
                    "Address recurring PPE violations through training programs",
                    "Resolve 7 critical issues within the next 14 days",
                    "Improve fire safety compliance across ECL subsidiary"
                ],
                "confidence": 0.86
            }

        # Default response
        return {
            "answer": f"I've analyzed your query about '{query}'. Based on current mining governance data:\n\n"
                      "The platform is monitoring 48 mines across 3 subsidiaries. "
                      "Overall compliance stands at 78% with 9 mines requiring elevated attention due to "
                      "risk scores above 70. Key areas of focus include safety compliance, environmental monitoring, "
                      "and corrective action closure rates.\n\n"
                      "For more specific insights, try asking:\n"
                      "• \"Which mines require immediate attention?\"\n"
                      "• \"Show recurring violations\"\n"
                      "• \"What compliance actions are due this week?\"\n"
                      "• \"Summarize the governance situation\"",
            "data": None,
            "entities": [],
            "recommendations": [
                "Review high-risk mine profiles for detailed analysis",
                "Check the compliance dashboard for overdue items",
                "Review recent field reports for operational insights"
            ],
            "confidence": 0.70
        }

    def suggest_corrective_actions(self, violation_data: dict) -> list[str]:
        """Suggest corrective actions based on violation category."""
        category = violation_data.get("category", "").lower()
        suggestions = {
            "safety": [
                "Conduct immediate safety audit of affected area",
                "Implement mandatory safety briefing for all workers",
                "Review and update safety protocols",
                "Schedule follow-up inspection within 7 days"
            ],
            "environment": [
                "Submit updated environmental monitoring readings",
                "Conduct environmental impact assessment",
                "Implement dust suppression / emission control measures",
                "File compliance report with environmental authority"
            ],
            "equipment": [
                "Schedule immediate equipment maintenance",
                "Conduct equipment safety certification review",
                "Implement preventive maintenance schedule",
                "Train operators on proper equipment handling"
            ],
            "labour": [
                "Review worker training compliance records",
                "Conduct safety awareness workshop",
                "Update worker protective equipment",
                "Verify worker attendance and shift compliance"
            ],
            "documentation": [
                "Submit all pending documentation within 7 days",
                "Digitize and archive existing paper records",
                "Establish documentation review workflow",
                "Assign dedicated documentation officer"
            ],
        }
        return suggestions.get(category, [
            "Investigate root cause of violation",
            "Implement corrective measures within 14 days",
            "Schedule follow-up verification inspection",
            "Report resolution to compliance authority"
        ])

    def summarize_compliance(self, records: list[dict]) -> str:
        """Summarize compliance status from records."""
        total = len(records)
        if total == 0:
            return "No compliance records available for summarization."

        completed = sum(1 for r in records if r.get("status") == "completed")
        overdue = sum(1 for r in records if r.get("status") == "overdue")
        pending = sum(1 for r in records if r.get("status") == "pending")
        rate = (completed / total) * 100 if total > 0 else 0

        return (
            f"Compliance Summary: {total} total requirements tracked. "
            f"{completed} completed ({rate:.0f}%), {pending} pending, {overdue} overdue. "
            f"{'Immediate attention needed for overdue items.' if overdue > 0 else 'All requirements on track.'}"
        )
