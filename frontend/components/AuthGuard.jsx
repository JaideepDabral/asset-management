import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useRole } from '@/contexts/RoleContext';

const ROLE_DASHBOARD_MAP = {
    'System Admin': '/dashboard/system-admin',
    'Asset & Inventory Manager': '/dashboard/asset-inventory-manager',
    'Procurement & Finance': '/dashboard/procurement-finance',
    'IT Management': '/dashboard/it-management',
    'End User': '/dashboard/end-user'
};

export default function AuthGuard({ children }) {
    const { isAuthenticated, currentRole, ROLES, isLoading } = useRole();
    const router = useRouter();
    const [authorized, setAuthorized] = useState(false);

    useEffect(() => {
        if (isLoading) {
            console.log("AuthGuard: [WAITING] Context is still loading...");
            return;
        }

        const checkAuth = () => {
            const currentPath = router.asPath.split('?')[0];
            const isLoginPage = currentPath === '/login';

            console.log("AuthGuard: [CHECKING]", { 
                isAuthenticated, 
                role: currentRole?.label, 
                path: currentPath,
                isReady: router.isReady 
            });

            if (!isAuthenticated) {
                if (!isLoginPage) {
                    console.warn("AuthGuard: [UNAUTHORIZED] No session found. Redirecting to login.");
                    router.push('/login');
                } else {
                    console.log("AuthGuard: [ALLOWED] At login page, unauthorized is fine.");
                    setAuthorized(true);
                }
            } else {
                if (!currentRole) {
                    console.warn("AuthGuard: [INCOMPLETE] Authenticated but no role. This shouldn't happen.");
                    setAuthorized(true);
                    return;
                }

                if (currentPath === '/') {
                    const targetPath = ROLE_DASHBOARD_MAP[currentRole.label] || '/dashboard/end-user';
                    console.log("AuthGuard: [REDIRECTING] Sending authenticated user to dashboard:", targetPath);
                    router.push(targetPath);
                } else {
                    console.log("AuthGuard: [AUTHORIZED] Access granted for", currentRole.label);
                    setAuthorized(true);
                }
            }
        };

        if (router.isReady) {
            checkAuth();
        }

    }, [isAuthenticated, currentRole, router.asPath, isLoading, router.isReady]);

    if (isLoading || (!authorized && router.pathname !== '/login')) {
        return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500 text-sm">Loading Identity...</div>;
    }

    return children;
}
