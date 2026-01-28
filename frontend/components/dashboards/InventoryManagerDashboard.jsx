import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Archive, TrendingDown, AlertOctagon, CheckCircle, Package } from 'lucide-react';
import { useAssetContext } from '@/contexts/AssetContext';
import { useRole } from '@/contexts/RoleContext';

export default function InventoryManagerDashboard() {
    const { user } = useRole();
    const { requests, inventoryCheckAvailable, inventoryCheckNotAvailable, inventoryAllocateDelivered, assets, exitRequests, processExitAssets } = useAssetContext();

    // ENTERPRISE: Requests awaiting inventory check (exclude fulfilled/closed)
    const awaitingStockCheck = requests.filter(r => {
        const shouldShow = r.currentOwnerRole === 'ASSET_INVENTORY_MANAGER' && 
            r.status !== 'FULFILLED' && 
            r.status !== 'CLOSED' &&
            r.procurementStage !== 'DELIVERED';
        
        // Debug logging
        if (r.currentOwnerRole === 'ASSET_INVENTORY_MANAGER') {
            console.log(`[Inventory Filter] Request ${r.id}: status=${r.status}, shouldShow=${shouldShow}`);
        }
        
        return shouldShow;
    });

    // ENTERPRISE: Delivered items awaiting final allocation (exclude fulfilled/closed)
    const awaitingAllocation = requests.filter(r => 
        (r.currentOwnerRole === 'ASSET_INVENTORY_MANAGER' && r.procurementStage === 'DELIVERED') || 
        (r.status === 'QC_PENDING')
    ).filter(r => r.status !== 'FULFILLED' && r.status !== 'CLOSED');

    // REAL DATA: Calculate stock stats from context assets
    const stockStats = assets.reduce((acc, asset) => {
        const type = asset.type || 'Other';
        if (!acc[type]) acc[type] = { name: type, stock: 0, min: 5 }; // Mock min threshold
        if (asset.status === 'In Stock' || asset.status === 'Available') {
            acc[type].stock += 1;
        }
        return acc;
    }, {});

    const realStockData = Object.values(stockStats).sort((a, b) => b.stock - a.stock);
    const displayStockData = realStockData.length > 0 ? realStockData : [
        { name: 'Laptops', stock: 0, min: 5 },
        { name: 'Monitors', stock: 0, min: 5 }
    ];

    const totalSKUs = new Set(assets.map(a => a.type)).size;
    const criticalShortages = realStockData.filter(i => i.stock < i.min).length;

    return (
        <div className="space-y-6">
            <header>
                <h1 className="text-3xl font-bold text-white">Stock Control</h1>
                <p className="text-slate-400">Inventory levels and replenishment alerts</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6 border border-white/5 hover:border-blue-500/30 transition-all">
                    <div className="flex justify-between">
                        <div>
                            <p className="text-slate-400 text-xs uppercase font-bold tracking-wider">Total SKUs</p>
                            <h3 className="text-3xl font-bold text-white mt-1">{totalSKUs}</h3>
                        </div>
                        <div className="p-3 bg-blue-500/10 rounded-xl">
                            <Archive size={20} className="text-blue-500" />
                        </div>
                    </div>
                </div>
                <div className="glass-card p-6 border border-white/5 hover:border-rose-500/30 transition-all">
                    <div className="flex justify-between">
                        <div>
                            <p className="text-slate-400 text-xs uppercase font-bold tracking-wider">Critical Shortages</p>
                            <h3 className="text-3xl font-bold text-rose-500 mt-1">{criticalShortages}</h3>
                        </div>
                        <div className="p-3 bg-rose-500/10 rounded-xl">
                            <AlertOctagon size={20} className="text-rose-500" />
                        </div>
                    </div>
                </div>
                <div className="glass-card p-6 border border-white/5 hover:border-amber-500/30 transition-all">
                    <div className="flex justify-between">
                        <div>
                            <p className="text-slate-400 text-xs uppercase font-bold tracking-wider">To Reorder</p>
                            <h3 className="text-3xl font-bold text-amber-500 mt-1">{requests.filter(r => r.status === 'PROCUREMENT_REQUIRED').length}</h3>
                        </div>
                        <div className="p-3 bg-amber-500/10 rounded-xl">
                            <TrendingDown size={20} className="text-amber-500" />
                        </div>
                    </div>
                </div>
            </div>

            {/* FULFILLMENT QUEUE (NEW) */}
            <div className="glass-panel p-6">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Package className="text-emerald-400" />
                        Inventory Stock Check
                        <span className="bg-blue-500/10 text-blue-400 text-xs px-2 py-0.5 rounded-full border border-blue-500/20">{awaitingStockCheck.length}</span>
                    </h3>
                </div>

                {awaitingStockCheck.length === 0 ? (
                    <div className="p-8 text-center text-slate-500 bg-white/5 rounded-xl border border-dashed border-white/10">
                        No requests awaiting stock check.
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-white/5 text-slate-400 text-xs uppercase font-bold">
                                <tr>
                                    <th className="p-3 rounded-l-lg">Asset Request</th>
                                    <th className="p-3">Requested By</th>
                                    <th className="p-3">Approval</th>
                                    <th className="p-3 text-right rounded-r-lg">Stock Decision</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {awaitingStockCheck.map(req => (
                                    <tr key={req.id} className="hover:bg-white/5 transition-colors">
                                        <td className="p-3">
                                            <div className="text-white font-medium">{req.assetType}</div>
                                            <div className="text-xs text-slate-500">{req.id}</div>
                                            <div className="text-xs text-slate-400 mt-1">{req.justification}</div>
                                        </td>
                                        <td className="p-3">
                                            <div className="text-slate-300">{req.requestedBy.name}</div>
                                            <div className="text-xs text-slate-500">{req.requestedBy.role}</div>
                                        </td>
                                        <td className="p-3">
                                            <span className="text-xs px-2 py-1 rounded font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                                IT APPROVED
                                            </span>
                                        </td>
                                        <td className="p-3 text-right">
                                            <div className="flex justify-end gap-2">
                                                <button
                                                    onClick={async () => {
                                                        const assetId = prompt(`Enter available asset ID for ${req.assetType}:`, "AST-" + Math.floor(Math.random() * 1000));
                                                        if (assetId) await inventoryCheckAvailable(req.id, assetId, user.name || 'Inventory Manager');
                                                    }}
                                                    className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-4 py-2 rounded-lg font-medium shadow-lg shadow-emerald-500/10 transition-all flex items-center gap-2"
                                                >
                                                    <CheckCircle size={14} /> Asset Available
                                                </button>
                                                <button
                                                    onClick={async () => await inventoryCheckNotAvailable(req.id, user.name || 'Inventory Manager')}
                                                    className="bg-amber-600 hover:bg-amber-500 text-white text-xs px-4 py-2 rounded-lg font-medium shadow-lg shadow-amber-500/10 transition-all"
                                                >
                                                    Not Available → Procurement
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* SECTION 2: Allocate Delivered Items */}
            {awaitingAllocation.length > 0 && (
                <div className="glass-panel p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <CheckCircle className="text-green-400" />
                            Delivered Items - Final Allocation
                            <span className="bg-green-500/10 text-green-400 text-xs px-2 py-0.5 rounded-full border border-green-500/20">{awaitingAllocation.length}</span>
                        </h3>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-white/5 text-slate-400 text-xs uppercase font-bold">
                                <tr>
                                    <th className="p-3 rounded-l-lg">Asset Request</th>
                                    <th className="p-3">Requested By</th>
                                    <th className="p-3">Procurement</th>
                                    <th className="p-3 text-right rounded-r-lg">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {awaitingAllocation.map(req => (
                                    <tr key={req.id} className="hover:bg-white/5 transition-colors">
                                        <td className="p-3">
                                            <div className="text-white font-medium">{req.assetType}</div>
                                            <div className="text-xs text-slate-500">{req.id}</div>
                                        </td>
                                        <td className="p-3">
                                            <div className="text-slate-300">{req.requestedBy.name}</div>
                                            <div className="text-xs text-slate-500">{req.requestedBy.role}</div>
                                        </td>
                                        <td className="p-3">
                                            <span className="text-xs px-2 py-1 rounded font-bold bg-green-500/10 text-green-400 border border-green-500/20">
                                                ✓ DELIVERED
                                            </span>
                                        </td>
                                        <td className="p-3 text-right">
                                            <button
                                                onClick={async () => {
                                                    const assetId = prompt(`Enter asset ID to allocate for ${req.assetType}:`, req.assetId || ("AST-" + Math.floor(Math.random() * 1000)));
                                                    if (assetId) await inventoryAllocateDelivered(req.id, assetId, user.name || 'Inventory Manager');
                                                }}
                                                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-4 py-2 rounded-lg font-medium shadow-lg shadow-emerald-500/10 transition-all flex items-center gap-2 ml-auto"
                                            >
                                                <CheckCircle size={14} /> Allocate Asset → Complete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* SECTION 3: Exit Reclamations (NEW) */}
            {exitRequests.filter(r => r.status === 'OPEN' || r.status === 'BYOD_PROCESSED').length > 0 && (
                <div className="glass-panel p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                             <Archive className="text-orange-400" />
                             Asset Reclamation (Employee Exit)
                             <span className="bg-orange-500/10 text-orange-400 text-xs px-2 py-0.5 rounded-full border border-orange-500/20">
                                 {exitRequests.filter(r => r.status === 'OPEN' || r.status === 'BYOD_PROCESSED').length}
                             </span>
                        </h3>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-white/5 text-slate-400 text-xs uppercase font-bold">
                                <tr>
                                    <th className="p-3 rounded-l-lg">User</th>
                                    <th className="p-3">Assets to Reclaim</th>
                                    <th className="p-3">Status</th>
                                    <th className="p-3 text-right rounded-r-lg">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {exitRequests.filter(r => r.status === 'OPEN' || r.status === 'BYOD_PROCESSED').map(req => (
                                    <tr key={req.id} className="hover:bg-white/5 transition-colors">
                                        <td className="p-3">
                                            <div className="text-white font-medium">{req.user_id}</div>
                                            <div className="text-xs text-slate-500">Exit ID: {req.id}</div>
                                        </td>
                                        <td className="p-3">
                                            <div className="text-slate-300 text-sm">
                                                {req.assets_snapshot?.length || 0} Physical Assets
                                            </div>
                                            <div className="text-xs text-slate-500 font-mono">
                                                {req.assets_snapshot?.map(a => a.asset_id).join(', ')}
                                            </div>
                                        </td>
                                        <td className="p-3">
                                            <span className="text-[10px] px-2 py-1 rounded font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">
                                                {req.status}
                                            </span>
                                        </td>
                                        <td className="p-3 text-right">
                                            <button
                                                onClick={async () => {
                                                    if (confirm(`Confirm receipt and QC of all company assets for user ${req.user_id}?`)) {
                                                        await processExitAssets(req.id);
                                                    }
                                                }}
                                                className="bg-orange-600 hover:bg-orange-500 text-white text-xs px-4 py-2 rounded-lg font-medium shadow-lg shadow-orange-500/10 transition-all"
                                            >
                                                Process Asset Returns
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="glass-panel p-6 lg:col-span-2">
                    <h3 className="text-lg font-bold text-white mb-6">Stock Levels by Category</h3>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={displayStockData}>
                                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                />
                                <Bar dataKey="stock" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-panel p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Stock Alerts</h3>
                    <div className="space-y-4">
                        {displayStockData.filter(i => i.stock < i.min).map(item => (
                            <div key={item.name} className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-bold text-rose-400">{item.name}</span>
                                    <span className="text-xs bg-rose-500 text-white px-2 py-0.5 rounded-full">Below Min</span>
                                </div>
                                <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                                    <div className="bg-rose-500 h-full" style={{ width: `${Math.min(100, (item.stock / item.min) * 100)}%` }}></div>
                                </div>
                                <div className="flex justify-between mt-2 text-xs text-slate-400">
                                    <span>Current: {item.stock}</span>
                                    <span>Min: {item.min}</span>
                                </div>
                                <button className="mt-3 w-full py-1.5 text-xs font-semibold text-rose-950 bg-rose-400 rounded hover:bg-rose-300">
                                    Restock Now
                                </button>
                            </div>
                        ))}
                        <div className="p-4 bg-white/5 rounded-xl text-center cursor-pointer hover:bg-white/10">
                            <span className="text-sm text-slate-400">+ View Reconciliation Report</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
