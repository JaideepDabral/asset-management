# ITSM Platform Master Documentation

## 1. Project Overview & Proposal

The ITSM (IT Service Management) Platform is a comprehensive solution designed to manage the full lifecycle of IT assets, support tickets, and employee transitions.

### Key Capabilities

- **Role-Based Security:** 6 distinct roles (System Admin, IT, Inventory, Finance, Manager, Employee).
- **Asset Command Center:** Real-time inventory tracking and automated lifecycle management.
- **Intelligent Procurement:** 5-stage approval pipeline (Employee -> Manager -> IT -> Finance -> Delivery).
- **IT Support & Helpdesk:** Linked incident ticketing with mandatory diagnostics.
- **Secure Offboarding:** Snapshot-based asset reclamation and account locking.
- **Strategic Analytics:** Executive dashboards and operational reports.

## 2. Feature Implementation Matrix

Current Status: **~68% Complete** (15/22 Features Active)

| Module              | Feature                               | Status     |
| :------------------ | :------------------------------------ | :--------- |
| **Access Control**  | RBAC, User Onboarding                 | ✅ ACTIVE  |
| **Asset Mgmt**      | Hardware Tracking, Inventory, History | ✅ ACTIVE  |
| **Procurement**     | PR Workflow, Delivery Verification    | ✅ ACTIVE  |
| **IT Support**      | Incident Ticketing, Checklists, BYOD  | ✅ ACTIVE  |
| **HR Operations**   | Exit Workflow, Asset Reclamation      | ✅ ACTIVE  |
| **Employee Portal** | "My Assets", Service Catalog          | ✅ ACTIVE  |
| **Analytics**       | Executive Dashboards, Stock Alerts    | ✅ ACTIVE  |
| **Roadmap**         | SSO, Software Mgmt, Barcode Scanning  | ❌ Roadmap |

## 3. Technical Infrastructure & Setup

### Database Configuration (PostgreSQL)

The backend uses PostgreSQL with the `asset` schema.

- **Connectivity:** Controlled via `.env` variables (`DATABASE_URL` or individual host/port settings).
- **Setup:** Run `python setup_database.py` to initialize schemas and tables.
- **Mock Data:** Use `python populate_mock_data.py` for testing.

### Backend Workflow Engine

A standardized state machine manages transitions:
`SUBMITTED` -> `MANAGER_APPROVED` -> `IT_APPROVED` -> `PROCUREMENT_REQUESTED` -> `QC_PENDING` -> `USER_ACCEPTANCE_PENDING` -> `IN_USE` -> `CLOSED`.

### Integration Summary

- **Frontend-Backend:** Fully integrated via `apiClient.js` and `AssetContext.jsx`.
- **API Base:** `http://localhost:8000`
- **Authentication:** JWT-based persistent sessions.

## 4. Operational Workflows

### Asset Request & Procurement

1. **Employee** submits request.
2. **Manager** approves.
3. **IT** verifies technical specs.
4. **Finance** reviews budget and approves PO (if out of stock).
5. **Procurement** confirms delivery.
6. **Inventory Manager** performs QC and allocates asset.
7. **Employee** accepts/rejects delivery.

### IT Support (Ticketing)

- Tickets are auto-linked to assets.
- Technicians must complete diagnostic checklists before resolution notes can be submitted.

### Employee Exit (Offboarding)

1. **Admin** initiates exit.
2. **System** freezes asset/BYOD snapshot.
3. **Inventory Manager** reclaims physical assets.
4. **IT** wipes/unenrolls BYOD devices.
5. **Admin** finalizes and disables account.

## 5. System Status & Verification

- **Internal Docs:** Interactive API documentation available at `/docs`.
- **Audit Logs:** All significant actions are recorded in `system.audit_logs`.
- **Data Collection:** The `/api/v1/collect` endpoint allows external systems to auto-register assets via serial number detection.
