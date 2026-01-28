import React from 'react';
import { AlertCircle, Clock, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const MOCK_ALERTS = [
    {
        id: 1,
        type: 'critical',
        title: 'Warranty Expiring Soon',
        message: 'MacBook Pro M1 (AST-003) warranty expires in 5 days.',
        time: '2 hours ago',
        icon: AlertCircle,
        color: 'text-rose-400',
        bg: 'bg-rose-500/10',
        border: 'border-rose-500/20',
        link: '/assets?risk=warranty'
    },
    {
        id: 2,
        type: 'warning',
        title: 'New Renewal Request',
        message: 'Sarah Jenkins requested renewal for Dell XPS 15.',
        time: '5 hours ago',
        icon: Clock,
        color: 'text-orange-400',
        bg: 'bg-orange-500/10',
        border: 'border-orange-500/20',
        link: '/renewals'
    },
    {
        id: 3,
        type: 'success',
        title: 'Procurement Approved',
        message: 'PO-2024-001 for 5 monitors has been approved.',
        time: '1 day ago',
        icon: CheckCircle2,
        color: 'text-emerald-400',
        bg: 'bg-emerald-500/10',
        border: 'border-emerald-500/20',
        link: '/procurement'
    },
    {
        id: 4,
        type: 'info',
        title: 'Asset Assigned',
        message: 'iPhone 13 assigned to New Hire (Mike Ross).',
        time: '1 day ago',
        icon: AlertTriangle, // Placeholder icon or Info icon
        color: 'text-blue-400',
        bg: 'bg-blue-500/10',
        border: 'border-blue-500/20',
        link: '/assets'
    },
    {
        id: 5,
        type: 'critical',
        title: 'Maintenance Overdue',
        message: 'Server Rack A-04 monthly maintenance missed.',
        time: '2 days ago',
        icon: AlertCircle,
        color: 'text-rose-400',
        bg: 'bg-rose-500/10',
        border: 'border-rose-500/20',
        link: '/assets?status=Repair'
    }
];

export default function AlertsFeed() {
    const [alerts, setAlerts] = React.useState(MOCK_ALERTS);

    React.useEffect(() => {
        const savedSettings = localStorage.getItem('appSettings');
        if (savedSettings) {
            try {
                const { notifications } = JSON.parse(savedSettings);
                // Filter logic
                const filtered = MOCK_ALERTS.filter(alert => {
                    if (alert.title.includes('Warranty') && !notifications.expiry) return false;
                    if (alert.title.includes('Renewal') && !notifications.approvals) return false;
                    if (alert.title.includes('Approved') && !notifications.approvals) return false;
                    return true;
                });
                setAlerts(filtered);
            } catch (e) {
                console.error("Failed to load settings for alerts", e);
            }
        }
    }, []);

    if (alerts.length === 0) return (
        <div className="p-8 text-center border border-white/5 rounded-xl bg-white/5">
            <p className="text-slate-400 text-sm">No active alerts</p>
        </div>
    );

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-bold text-white flex items-center">
                    <span className="relative flex h-3 w-3 mr-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                    </span>
                    Live Alerts
                </h3>
                <button className="text-slate-400 hover:text-white text-xs font-medium transition-colors">
                    Clear All
                </button>
            </div>

            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                {alerts.map((alert) => {
                    const Icon = alert.icon;
                    return (
                        <div
                            key={alert.id}
                            className={`p-4 rounded-xl border ${alert.border} ${alert.bg} flex gap-4 transition-all hover:scale-[1.02] cursor-pointer`}
                        >
                            <div className={`mt-1 p-2 rounded-full ${alert.bg} border ${alert.border}`}>
                                <Icon size={16} className={alert.color} />
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start">
                                    <h4 className={`text-sm font-semibold ${alert.color}`}>{alert.title}</h4>
                                    <span className="text-[10px] text-slate-400 font-medium">{alert.time}</span>
                                </div>
                                <p className="text-slate-300 text-xs mt-1 leading-relaxed">
                                    {alert.message}
                                </p>
                                <Link href={alert.link}>
                                    <div className="mt-3 flex items-center text-[10px] font-medium text-slate-400 hover:text-white transition-colors group">
                                        View Details
                                        <ArrowRight size={12} className="ml-1 transition-transform group-hover:translate-x-1" />
                                    </div>
                                </Link>
                            </div>
                        </div>
                    );
                })}
            </div>

            <Link href="/notifications" className="block w-full py-3 text-center text-xs text-slate-400 hover:text-white font-medium border-t border-white/5 hover:bg-white/5 transition-colors">
                View All Notifications
            </Link>
        </div>
    );
}
