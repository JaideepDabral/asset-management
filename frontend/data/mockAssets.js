// Mock asset data used as fallback for AI Assistant
export const initialMockAssets = [
    {
      id: 1,
      type: "Laptop",
      segment: "IT",
      cost: 75000,
      warranty_expiry: "2025-12-31",
      assigned_to: "John Doe",
      status: "Active",
    },
    {
      id: 2,
      type: "Desktop",
      segment: "IT",
      cost: 55000,
      warranty_expiry: "2024-06-15",
      assigned_to: "Unassigned",
      status: "Active",
    },
    {
      id: 3,
      type: "Chair",
      segment: "NON-IT",
      cost: 5000,
      warranty_expiry: null,
      assigned_to: "Jane Smith",
      status: "Active",
    },
    {
      id: 4,
      type: "Monitor",
      segment: "IT",
      cost: 12000,
      warranty_expiry: "2026-01-20",
      assigned_to: "Unassigned",
      status: "Repair",
    },
];
