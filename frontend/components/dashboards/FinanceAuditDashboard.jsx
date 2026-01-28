import { useState } from 'react';
import ProcurementManagerDashboard from './ProcurementManagerDashboard';
import FinanceDashboard from './FinanceDashboard';
import AuditOfficerDashboard from './AuditOfficerDashboard';
import { ShoppingCart, DollarSign, ClipboardCheck } from 'lucide-react';

export default function FinanceAuditDashboard() {
    const [activeTab, setActiveTab] = useState('procurement');

    const tabs = [
        { id: 'procurement', label: 'Procurement', icon: ShoppingCart, component: ProcurementManagerDashboard },
        { id: 'finance', label: 'Finance', icon: DollarSign, component: FinanceDashboard },
        { id: 'audit', label: 'Audit', icon: ClipboardCheck, component: AuditOfficerDashboard },
    ];

    const ActiveComponent = tabs.find(t => t.id === activeTab)?.component || ProcurementManagerDashboard;

    return (
        <div className="space-y-6">
            {/* Tab Navigation */}
            <div className="flex flex-wrap gap-2 bg-slate-900/50 p-1.5 rounded-xl border border-white/5 backdrop-blur-sm w-fit">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${activeTab === tab.id
                                ? 'bg-amber-600/90 text-white shadow-lg shadow-amber-500/25' // Using Amber/Gold theme for finance
                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <tab.icon size={16} />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <ActiveComponent />
            </div>
        </div>
    );
}
