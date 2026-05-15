"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BlacklistEntry {
  id: string;
  entity_name: string;
  entity_type: string;
  registration_number: string;
  country: string;
  reason: string;
  reason_category: string;
  severity: string;
  related_project_ids: string[];
  evidence_refs: string[];
  incident_date: string | null;
  added_by: string;
  approved_by: string | null;
  is_active: boolean;
  review_date: string | null;
  internal_notes: string;
  created_at: string;
  updated_at: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  warning: "bg-amber-100 text-amber-800",
  restricted: "bg-orange-100 text-orange-800",
  banned: "bg-red-100 text-red-800",
};

const CATEGORY_LABELS: Record<string, string> = {
  performance: "Performance",
  safety_violation: "Safety Violation",
  fraud: "Fraud",
  payment_default: "Payment Default",
  legal: "Legal",
  other: "Other",
};

const ENTITY_TYPE_LABELS: Record<string, string> = {
  contractor: "Contractor",
  supplier: "Supplier",
  engineer: "Engineer",
  subconsultant: "Subconsultant",
  client: "Client",
};

export default function BlacklistPage() {
  const [entries, setEntries] = useState<BlacklistEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterEntityType, setFilterEntityType] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [search, setSearch] = useState("");
  const [showInactive, setShowInactive] = useState(false);

  // New entry form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEntry, setNewEntry] = useState({
    entity_name: "",
    entity_type: "contractor",
    registration_number: "",
    country: "",
    reason: "",
    reason_category: "performance",
    severity: "warning",
    added_by: "admin_001",
    internal_notes: "",
  });

  // Selected entry for detail
  const [selectedEntry, setSelectedEntry] = useState<BlacklistEntry | null>(null);

  // Check blacklist
  const [checkName, setCheckName] = useState("");
  const [checkResult, setCheckResult] = useState<{ is_blacklisted: boolean; matches: BlacklistEntry[] } | null>(null);

  const fetchBlacklist = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterEntityType) params.set("entity_type", filterEntityType);
      if (filterSeverity) params.set("severity", filterSeverity);
      if (filterCategory) params.set("reason_category", filterCategory);
      if (search) params.set("search", search);
      params.set("is_active", showInactive ? "false" : "true");
      const res = await fetch(`${API_BASE}/api/moderation/blacklist?${params}`);
      const data = await res.json();
      setEntries(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBlacklist();
  }, [filterEntityType, filterSeverity, filterCategory, showInactive]);

  const handleSearch = () => {
    fetchBlacklist();
  };

  const addEntry = async () => {
    try {
      await fetch(`${API_BASE}/api/moderation/blacklist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newEntry),
      });
      setNewEntry({
        entity_name: "",
        entity_type: "contractor",
        registration_number: "",
        country: "",
        reason: "",
        reason_category: "performance",
        severity: "warning",
        added_by: "admin_001",
        internal_notes: "",
      });
      setShowAddForm(false);
      fetchBlacklist();
    } catch (err) {
      console.error(err);
    }
  };

  const approveEntry = async (entryId: string) => {
    try {
      await fetch(`${API_BASE}/api/moderation/blacklist/${entryId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved_by: "admin_001" }),
      });
      fetchBlacklist();
      if (selectedEntry?.id === entryId) {
        const res = await fetch(`${API_BASE}/api/moderation/blacklist/${entryId}`);
        setSelectedEntry(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const deactivateEntry = async (entryId: string) => {
    try {
      await fetch(`${API_BASE}/api/moderation/blacklist/${entryId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: false }),
      });
      fetchBlacklist();
      setSelectedEntry(null);
    } catch (err) {
      console.error(err);
    }
  };

  const checkBlacklist = async () => {
    if (!checkName.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/moderation/blacklist/check?entity_name=${encodeURIComponent(checkName)}`);
      setCheckResult(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString();

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Blacklist Management</h1>
          <p className="text-slate-500 mt-1">Manage blacklisted contractors, suppliers, and engineers</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
        >
          {showAddForm ? "Cancel" : "Add to Blacklist"}
        </button>
      </div>

      {/* Check Blacklist */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
        <p className="text-sm font-medium text-slate-700 mb-2">Quick Check — Is an entity blacklisted?</p>
        <div className="flex gap-2">
          <input
            type="text"
            value={checkName}
            onChange={(e) => setCheckName(e.target.value)}
            placeholder="Enter entity name..."
            className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            onKeyDown={(e) => e.key === "Enter" && checkBlacklist()}
          />
          <button
            onClick={checkBlacklist}
            className="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm font-medium hover:bg-slate-900"
          >
            Check
          </button>
        </div>
        {checkResult && (
          <div className={`mt-3 p-3 rounded-lg text-sm ${checkResult.is_blacklisted ? "bg-red-50 text-red-800" : "bg-green-50 text-green-800"}`}>
            {checkResult.is_blacklisted ? (
              <div>
                <p className="font-medium">BLACKLISTED — {checkResult.matches.length} match(es) found</p>
                {checkResult.matches.map((m) => (
                  <p key={m.id} className="mt-1">
                    {m.entity_name} — {m.severity} ({m.reason_category})
                  </p>
                ))}
              </div>
            ) : (
              <p className="font-medium">No blacklist entries found for &quot;{checkName}&quot;</p>
            )}
          </div>
        )}
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="bg-white rounded-xl border border-red-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Add to Blacklist</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Entity Name *</label>
              <input
                type="text"
                value={newEntry.entity_name}
                onChange={(e) => setNewEntry({ ...newEntry, entity_name: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500"
                placeholder="Company or individual name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Entity Type</label>
              <select
                value={newEntry.entity_type}
                onChange={(e) => setNewEntry({ ...newEntry, entity_type: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white"
              >
                <option value="contractor">Contractor</option>
                <option value="supplier">Supplier</option>
                <option value="engineer">Engineer</option>
                <option value="subconsultant">Subconsultant</option>
                <option value="client">Client</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Registration Number</label>
              <input
                type="text"
                value={newEntry.registration_number}
                onChange={(e) => setNewEntry({ ...newEntry, registration_number: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Country</label>
              <input
                type="text"
                value={newEntry.country}
                onChange={(e) => setNewEntry({ ...newEntry, country: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Reason *</label>
              <textarea
                value={newEntry.reason}
                onChange={(e) => setNewEntry({ ...newEntry, reason: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                placeholder="Describe why this entity is being blacklisted..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
              <select
                value={newEntry.reason_category}
                onChange={(e) => setNewEntry({ ...newEntry, reason_category: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white"
              >
                <option value="performance">Performance</option>
                <option value="safety_violation">Safety Violation</option>
                <option value="fraud">Fraud</option>
                <option value="payment_default">Payment Default</option>
                <option value="legal">Legal</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Severity</label>
              <select
                value={newEntry.severity}
                onChange={(e) => setNewEntry({ ...newEntry, severity: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white"
              >
                <option value="warning">Warning</option>
                <option value="restricted">Restricted</option>
                <option value="banned">Banned</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Internal Notes</label>
              <textarea
                value={newEntry.internal_notes}
                onChange={(e) => setNewEntry({ ...newEntry, internal_notes: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                placeholder="Admin-only notes (not visible to the entity)..."
              />
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-4">
            <button
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              onClick={addEntry}
              disabled={!newEntry.entity_name || !newEntry.reason}
              className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add to Blacklist
            </button>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={filterEntityType}
          onChange={(e) => setFilterEntityType(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white"
        >
          <option value="">All Entity Types</option>
          <option value="contractor">Contractor</option>
          <option value="supplier">Supplier</option>
          <option value="engineer">Engineer</option>
          <option value="subconsultant">Subconsultant</option>
          <option value="client">Client</option>
        </select>

        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white"
        >
          <option value="">All Severities</option>
          <option value="warning">Warning</option>
          <option value="restricted">Restricted</option>
          <option value="banned">Banned</option>
        </select>

        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white"
        >
          <option value="">All Categories</option>
          <option value="performance">Performance</option>
          <option value="safety_violation">Safety Violation</option>
          <option value="fraud">Fraud</option>
          <option value="payment_default">Payment Default</option>
          <option value="legal">Legal</option>
          <option value="other">Other</option>
        </select>

        <div className="flex gap-2">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search name or reg. no..."
            className="px-3 py-2 text-sm border border-slate-300 rounded-lg"
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch} className="px-3 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm hover:bg-slate-200">
            Search
          </button>
        </div>

        <label className="flex items-center gap-1.5 text-xs text-slate-600 self-center ml-auto">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="rounded border-slate-300"
          />
          Show inactive
        </label>

        <span className="self-center text-sm text-slate-400">{total} entries</span>
      </div>

      {/* Blacklist Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading blacklist...</div>
        ) : entries.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            No blacklist entries found. Use &quot;Add to Blacklist&quot; to create one.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Entity</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Type</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Category</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Severity</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Approved</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Added</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {entries.map((entry) => (
                <tr
                  key={entry.id}
                  onClick={() => setSelectedEntry(selectedEntry?.id === entry.id ? null : entry)}
                  className={`cursor-pointer hover:bg-slate-50 ${selectedEntry?.id === entry.id ? "bg-red-50" : ""}`}
                >
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-900">{entry.entity_name}</p>
                    {entry.registration_number && (
                      <p className="text-xs text-slate-400">Reg: {entry.registration_number}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{ENTITY_TYPE_LABELS[entry.entity_type] || entry.entity_type}</td>
                  <td className="px-4 py-3 text-slate-600">{CATEGORY_LABELS[entry.reason_category] || entry.reason_category}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLORS[entry.severity] || ""}`}>
                      {entry.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {entry.approved_by ? (
                      <span className="text-green-600 text-xs">Yes</span>
                    ) : (
                      <span className="text-amber-600 text-xs">Pending</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{formatDate(entry.created_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                      {!entry.approved_by && entry.is_active && (
                        <button
                          onClick={() => approveEntry(entry.id)}
                          className="text-xs text-green-600 hover:text-green-800 font-medium"
                        >
                          Approve
                        </button>
                      )}
                      {entry.is_active && (
                        <button
                          onClick={() => deactivateEntry(entry.id)}
                          className="text-xs text-red-600 hover:text-red-800 font-medium"
                        >
                          Deactivate
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Detail panel */}
      {selectedEntry && (
        <div className="fixed right-6 top-20 w-96 bg-white rounded-xl border border-slate-200 shadow-xl p-6 z-50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Entry Detail</h2>
            <button onClick={() => setSelectedEntry(null)} className="text-slate-400 hover:text-slate-600">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-slate-500">Entity:</span>
              <span className="ml-2 font-medium text-slate-900">{selectedEntry.entity_name}</span>
            </div>
            <div>
              <span className="text-slate-500">Type:</span>
              <span className="ml-2 text-slate-900">{ENTITY_TYPE_LABELS[selectedEntry.entity_type]}</span>
            </div>
            {selectedEntry.country && (
              <div>
                <span className="text-slate-500">Country:</span>
                <span className="ml-2 text-slate-900">{selectedEntry.country}</span>
              </div>
            )}
            <div>
              <span className="text-slate-500 block mb-1">Reason:</span>
              <p className="text-slate-700 bg-slate-50 rounded-lg p-3">{selectedEntry.reason}</p>
            </div>
            {selectedEntry.internal_notes && (
              <div>
                <span className="text-slate-500 block mb-1">Internal Notes:</span>
                <p className="text-slate-700 bg-amber-50 border border-amber-200 rounded-lg p-3">{selectedEntry.internal_notes}</p>
              </div>
            )}
            {selectedEntry.review_date && (
              <div>
                <span className="text-slate-500">Review Date:</span>
                <span className="ml-2 text-amber-600 font-medium">{selectedEntry.review_date}</span>
              </div>
            )}
            <div className="pt-2 border-t border-slate-200">
              <p className="text-xs text-slate-400">
                Added by {selectedEntry.added_by} on {formatDate(selectedEntry.created_at)}
                {selectedEntry.approved_by && ` | Approved by ${selectedEntry.approved_by}`}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
