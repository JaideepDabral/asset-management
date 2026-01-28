import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, ShoppingCart, Check, Truck, Package, FileText, CheckCircle, AlertCircle, X, DollarSign, Calendar, Building, ShieldCheck } from 'lucide-react'

// --- Helper: Action Modal ---
const ActionModal = ({ isOpen, onClose, title, data, onConfirm, actionLabel, stepType }) => {
    if (!isOpen || !data) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity" onClick={onClose} />
            <div className="relative bg-[#0f172a] border border-white/10 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="px-6 py-4 border-b border-white/10 bg-slate-900/50 flex justify-between items-center">
                    <h3 className="text-lg font-bold text-white">{title}</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors"><X size={20} /></button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Asset Summary */}
                    <div className="bg-slate-800/50 rounded-xl p-4 border border-white/5 flex gap-4">
                        <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400">
                            <Package size={24} />
                        </div>
                        <div>
                            <h4 className="text-white font-medium text-lg">{data.name}</h4>
                            <p className="text-slate-400 text-sm">{data.type} • {data.specs}</p>
                        </div>
                    </div>

                    {/* Details Grid */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <p className="text-xs text-slate-500 uppercase font-semibold">Requested By</p>
                            <p className="text-slate-200 text-sm flex items-center gap-2">
                                <span className="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-xs text-white mobile-hidden">{data.assigned_to?.charAt(0)}</span>
                                {data.assigned_to}
                            </p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-xs text-slate-500 uppercase font-semibold">Estimated Cost</p>
                            <p className="text-slate-200 text-sm font-mono flex items-center gap-1">
                                <DollarSign size={12} className="text-emerald-500" /> {data.cost}
                            </p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-xs text-slate-500 uppercase font-semibold">Vendor</p>
                            <p className="text-slate-200 text-sm flex items-center gap-1">
                                <Building size={12} className="text-blue-400" /> {data.vendor || 'Pending Selection'}
                            </p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-xs text-slate-500 uppercase font-semibold">Justification</p>
                            <p className="text-slate-200 text-sm truncate" title={data.justification}>{data.justification}</p>
                        </div>
                    </div>

                    {/* Compliance / Checklist Section */}
                    <div className="border-t border-white/5 pt-4">
                        <h5 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                            <ShieldCheck size={16} className="text-emerald-400" />
                            {stepType === 'approve' ? 'Pre-Approval Checklist' :
                                stepType === 'order' ? 'Procurement Checklist' :
                                    stepType === 'receive' ? 'Onboarding Checklist' : 'Status'}
                        </h5>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm text-slate-300">
                                <CheckCircle size={14} className="text-emerald-500" />
                                <span>Budget allocated and confirmed</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-slate-300">
                                <CheckCircle size={14} className="text-emerald-500" />
                                <span>Hardware standards compliance verified</span>
                            </div>
                            {stepType === 'receive' && (
                                <div className="flex items-center gap-2 text-sm text-slate-300">
                                    <CheckCircle size={14} className="text-blue-500" />
                                    <span>Asset tagging & serialization ready</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-slate-900/50 border-t border-white/10 flex justify-end gap-3">
                    <button onClick={onClose} className="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors">Cancel</button>
                    <button
                        onClick={() => onConfirm(data.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium text-white shadow-lg transition-all flex items-center gap-2
                            ${stepType === 'approve' ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-500/20' :
                                stepType === 'order' ? 'bg-blue-600 hover:bg-blue-500 shadow-blue-500/20' :
                                    stepType === 'receive' ? 'bg-purple-600 hover:bg-purple-500 shadow-purple-500/20' : 'bg-slate-700'}
                        `}
                    >
                        {actionLabel}
                    </button>
                </div>
            </div>
        </div>
    );
};


export default function Procurement() {
    const [loading, setLoading] = useState(true)

    // Detailed Mock Data (Enterprise)
    const [requests, setRequests] = useState([
        {
            id: 101,
            name: 'Dell Precision 5570',
            type: 'Workstation',
            specs: 'i9, 32GB RAM, 1TB SSD, RTX A2000',
            vendor: 'Dell Enterprise',
            cost: '1,85,000',
            procurement_status: 'Requested',
            assigned_to: 'Design Team',
            justification: 'New hire in Creative department needs rendering power.',
            compliance: 'Standard'
        },
        {
            id: 102,
            name: 'MacBook Pro 16"',
            type: 'Laptop',
            specs: 'M3 Pro, 18GB, 512GB',
            vendor: 'Imagine Store',
            cost: '2,40,000',
            procurement_status: 'Approved',
            assigned_to: 'Sarah Lee (Dev)',
            justification: 'Replacement for aged device (Asset #4002).',
            compliance: 'Exception Approved'
        },
        {
            id: 103,
            name: 'HP LaserJet Pro MFP',
            type: 'Printer',
            specs: 'Network M428fdw',
            vendor: 'Office Supplies Co.',
            cost: '45,000',
            procurement_status: 'Ordered',
            assigned_to: 'HR Dept',
            justification: 'Additional capacity for payroll processing.',
            compliance: 'Standard'
        },
        {
            id: 104,
            name: 'Cisco Meraki MR44',
            type: 'Network',
            specs: 'Wi-Fi 6 Access Point',
            vendor: 'Network Solutions',
            cost: '62,000',
            procurement_status: 'Received',
            assigned_to: 'IT Infra',
            justification: 'Expansion of 3rd floor coverage.',
            compliance: 'Critical Infra'
        },
    ])

    // Modal State
    const [modalConfig, setModalConfig] = useState(null) // { isOpen, data, type, ... }

    useEffect(() => {
        // Simulate initial data fetch
        setTimeout(() => setLoading(false), 500)
    }, [])

    // --- Logic ---

    const openActionModal = (request) => {
        let config = { isOpen: true, data: request };

        switch (request.procurement_status) {
            case 'Requested':
                config.title = "Approve Procurement Request";
                config.actionLabel = "Approve Request";
                config.stepType = 'approve';
                config.onConfirm = handleApprove;
                break;
            case 'Approved':
                config.title = "Place Start Order";
                config.actionLabel = "Confirm Order Placement";
                config.stepType = 'order';
                config.onConfirm = handleOrder;
                break;
            case 'Ordered':
                config.title = "Receive Shipment & Verify";
                config.actionLabel = "Receive & Stock";
                config.stepType = 'receive';
                config.onConfirm = handleReceive;
                break;
            case 'Received':
                config.title = "Finalize Asset Registration";
                config.actionLabel = "Register to Inventory";
                config.stepType = 'receive';
                config.onConfirm = handleStock;
                break;
            default:
                return;
        }
        setModalConfig(config);
    }

    const updateStatus = (id, newStatus) => {
        setRequests(prev => prev.map(r => r.id === id ? { ...r, procurement_status: newStatus } : r));
        setModalConfig(null);
    }

    const handleApprove = (id) => updateStatus(id, 'Approved');
    const handleOrder = (id) => updateStatus(id, 'Ordered');
    const handleReceive = (id) => updateStatus(id, 'Received');

    const handleStock = (id) => {
        // 1. Find Data
        const request = requests.find(r => r.id === id);
        if (!request) return;

        // 2. Add to LocalStorage (Inventory Handoff)
        const savedAssets = localStorage.getItem('assets');
        const currentAssets = savedAssets ? JSON.parse(savedAssets) : [];

        const newAsset = {
            id: Date.now(), // Generate new Asset ID
            name: request.name,
            type: request.type,
            status: 'In Stock', // Initial inventory status
            assigned_to: null, // Initially unassigned in inventory until deployed
            location: 'Main Store',
            cost: parseInt(request.cost.replace(/,/g, '')),
            vendor: request.vendor,
            purchase_date: new Date().toISOString().split('T')[0]
        };

        const updatedAssets = [...currentAssets, newAsset];
        localStorage.setItem('assets', JSON.stringify(updatedAssets));

        // 3. Update Request Status
        updateStatus(id, 'Stocked');

        // Optional: Notify user
        // alert("Asset moved to inventory!"); 
    }

    const getStatusStep = (status) => {
        const steps = ['Requested', 'Approved', 'Ordered', 'Received', 'Stocked']
        const currentIdx = steps.indexOf(status)

        return (
            <div className="flex flex-col gap-1">
                <div className="flex items-center space-x-1">
                    {steps.slice(0, 5).map((step, idx) => (
                        <div
                            key={step}
                            title={step}
                            className={`h-1.5 w-8 rounded-full transition-colors duration-300 ${idx <= currentIdx
                                    ? status === 'Stocked' ? 'bg-emerald-500' : 'bg-blue-500'
                                    : 'bg-slate-700'
                                }`}
                        />
                    ))}
                </div>
                <span className={`text-[10px] font-medium uppercase tracking-wider ${status === 'Stocked' ? 'text-emerald-400' : 'text-slate-400'
                    }`}>
                    {status}
                </span>
            </div>
        )
    }

    if (loading) return <div className="p-8 text-white">Loading Enterprise Procurement Module...</div>

    return (
        <div className="space-y-8 pb-20">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-white tracking-tight">Procurement & Onboarding</h2>
                    <p className="text-slate-400 mt-1">Enterprise Asset Acquisition Pipeline</p>
                </div>
                <Link href="/" className="btn btn-secondary flex items-center bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-colors">
                    <ArrowLeft size={16} className="mr-2" /> Dashboard
                </Link>
            </div>

            <div className="glass-panel overflow-hidden border border-white/5 bg-slate-900/50 backdrop-blur rounded-2xl">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/10 bg-white/5">
                            <th className="p-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Request Details</th>
                            <th className="p-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Business Context</th>
                            <th className="p-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Pipeline Status</th>
                            <th className="p-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Next Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {requests.length === 0 ? <tr><td colSpan="4" className="p-8 text-center text-slate-500">No active procurement orders.</td></tr> :
                            requests.map(req => {
                                const isStocked = req.procurement_status === 'Stocked';
                                return (
                                    <tr key={req.id} className={`transition-colors ${isStocked ? 'bg-emerald-900/5 hover:bg-emerald-900/10' : 'hover:bg-white/5'}`}>
                                        <td className="p-4">
                                            <div className="flex items-start gap-3">
                                                <div className="mt-1 p-2 rounded bg-slate-800 text-slate-400">
                                                    {req.type === 'Laptop' || req.type === 'Workstation' ? <Package size={16} /> : <FileText size={16} />}
                                                </div>
                                                <div>
                                                    <div className="font-medium text-white">{req.name}</div>
                                                    <div className="text-xs text-slate-500 mt-0.5">{req.specs}</div>
                                                    <div className="text-[10px] text-slate-600 uppercase mt-1">{req.vendor}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <div className="text-slate-300 text-sm">{req.assigned_to}</div>
                                            <div className="text-xs text-slate-500 mt-0.5 line-clamp-1">{req.justification}</div>
                                        </td>
                                        <td className="p-4">
                                            {getStatusStep(req.procurement_status)}
                                        </td>
                                        <td className="p-4">
                                            {isStocked ? (
                                                <span className="flex items-center text-emerald-500 text-sm font-medium">
                                                    <CheckCircle size={16} className="mr-2" /> Completed
                                                </span>
                                            ) : (
                                                <button
                                                    onClick={() => openActionModal(req)}
                                                    className={`text-xs py-1.5 px-3 rounded flex items-center shadow-lg transition-all font-medium
                                                        ${req.procurement_status === 'Requested' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20' :
                                                            req.procurement_status === 'Approved' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500/20' :
                                                                req.procurement_status === 'Ordered' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20 hover:bg-purple-500/20' :
                                                                    'bg-slate-700 text-slate-300 hover:bg-slate-600'}
                                                    `}
                                                >
                                                    {req.procurement_status === 'Requested' && <>Authorize</>}
                                                    {req.procurement_status === 'Approved' && <><ShoppingCart size={14} className="mr-2" />Order</>}
                                                    {req.procurement_status === 'Ordered' && <><Truck size={14} className="mr-2" />Receive</>}
                                                    {req.procurement_status === 'Received' && <><Package size={14} className="mr-2" />Stock</>}
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                    </tbody>
                </table>
            </div>

            {/* Action Modal */}
            <ActionModal
                isOpen={modalConfig?.isOpen}
                onClose={() => setModalConfig(null)}
                {...modalConfig}
            />
        </div>
    )
}
