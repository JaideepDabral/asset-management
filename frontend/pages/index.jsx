import { useRole } from '@/contexts/RoleContext'
import SystemAdminDashboard from '@/components/dashboards/SystemAdminDashboard'
import AssetInventoryDashboard from '@/components/dashboards/AssetInventoryDashboard'
import FinanceAuditDashboard from '@/components/dashboards/FinanceAuditDashboard'
import ITSupportDashboard from '@/components/dashboards/ITSupportDashboard'
import EndUserDashboard from '@/components/dashboards/EndUserDashboard'

export default function Dashboard() {
    const { currentRole } = useRole();

    // 1. System Admin
    if (currentRole.label === 'System Admin') return <SystemAdminDashboard />

    // 2. Asset & Inventory Manager (Combined)
    if (currentRole.label === 'Asset & Inventory Manager') return <AssetInventoryDashboard />

    // 3. Procurement & Finance (Combined)
    if (currentRole.label === 'Procurement & Finance') return <FinanceAuditDashboard />

    // 4. IT Management
    if (currentRole.label === 'IT Management') return <ITSupportDashboard />

    // 5. End User
    if (currentRole.label === 'End User') return <EndUserDashboard />

    // Fallback
    return <SystemAdminDashboard />
}
