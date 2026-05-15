"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DisputeComment {
  id: string;
  author_name: string;
  author_role: string;
  comment: string;
  is_internal: boolean;
  created_at: string;
}

interface Dispute {
  id: string;
  project_id: string;
  review_id: string | null;
  raised_by: string;
  raised_by_email: string;
  raised_by_role: string;
  title: string;
  description: string;
  dispute_type: string;
  severity: string;
  disputed_item: string;
  disputed_value: string;
  proposed_value: string;
  evidence_refs: string[];
  status: string;
  assigned_to: string | null;
  assignee_name: string | null;
  resolution_notes: string;
  resolution_outcome: string;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  comments: DisputeComment[];
}

const STATUS_COLORS: Record<string, string> = {
  open: "bg-amber-100 text-amber-800",
  investigating: "bg-blue-100 text-blue-800",
  mediated: "bg-purple-100 text-purple-800",
  resolved: "bg-green-100 text-green-800",
  dismissed: "bg-slate-100 text-slate-600",
  escalated: "bg-red-100 text-red-800",
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-800",
  high: "bg-orange-100 text-orange-800",
  medium: "bg-amber-100 text-amber-800",
  low: "bg-slate-100 text-slate-600",
};

const DISPUTE_TYPE_LABELS: Record<string, string> = {
  design_disagreement: "Design Disagreement",
  calculation_error: "Calculation Error",
  scope_dispute: "Scope Dispute",
  cost_dispute: "Cost Dispute",
  safety_concern: "Safety Concern",
};

export default function DisputesPage() {
  const searchParams = useSearchParams();
  const initialStatus = searchParams.get("status") || "";

  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState(initialStatus);
  const [filterSeverity, setFilterSeverity] = useState("");
  const [filterType, setFilterType] = useState("");
  const [selectedDispute, setSelectedDispute] = useState<Dispute | null>(null);
  const [newComment, setNewComment] = useState("");
  const [isInternal, setIsInternal] = useState(false);
  const [resolveOutcome, setResolveOutcome] = useState("");
  const [resolveNotes, setResolveNotes] = useState("");

  const fetchDisputes = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.set("status", filterStatus);
      if (filterSeverity) params.set("severity", filterSeverity);
      if (filterType) params.set("dispute_type", filterType);
      const res = await fetch(`${API_BASE}/api/moderation/disputes?${params}`);
      const data = await res.json();
      setDisputes(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDisputes();
  }, [filterStatus, filterSeverity, filterType]);

  const addComment = async () => {
    if (!selectedDispute || !newComment.trim()) return;
    try {
      await fetch(`${API_BASE}/api/moderation/disputes/${selectedDispute.id}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          comment: newComment,
          author_name: "Admin",
          author_role: "admin",
          is_internal: isInternal,
        }),
      });
      setNewComment("");
      fetchDisputes();
      // Refresh selected
      const res = await fetch(`${API_BASE}/api/moderation/disputes/${selectedDispute.id}`);
      setSelectedDispute(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const resolveDispute = async () => {
    if (!selectedDispute || !resolveOutcome) return;
    try {
      await fetch(`${API_BASE}/api/moderation/disputes/${selectedDispute.id}?admin_id=admin_001`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "resolved",
          resolution_outcome: resolveOutcome,
          resolution_notes: resolveNotes,
        }),
      });
      setResolveOutcome("");
      setResolveNotes("");
      fetchDisputes();
      const res = await fetch(`${API_BASE}/api/moderation/disputes/${selectedDispute.id}`);
      setSelectedDispute(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const assignDispute = async (adminId: string) => {
    if (!selectedDispute) return;
    try {
      await fetch(`${API_BASE}/api/moderation/disputes/${selectedDispute.id}?admin_id=admin_001`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "investigating", assigned_to: adminId }),
      });
      fetchDisputes();
      const res = await fetch(`${API_BASE}/api/moderation/disputes/${selectedDispute.id}`);
      setSelectedDispute(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString();

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Dispute Resolution</h1>
        <p className="text-slate-500 mt-1">Investigate, mediate, and resolve disputes raised by project parties</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="mediated">Mediated</option>
          <option value="resolved">Resolved</option>
          <option value="dismissed">Dismissed</option>
          <option value="escalated">Escalated</option>
        </select>

        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Types</option>
          <option value="design_disagreement">Design Disagreement</option>
          <option value="calculation_error">Calculation Error</option>
          <option value="scope_dispute">Scope Dispute</option>
          <option value="cost_dispute">Cost Dispute</option>
          <option value="safety_concern">Safety Concern</option>
        </select>

        <span className="self-center text-sm text-slate-400">{total} disputes</span>
      </div>

      <div className="flex gap-6">
        {/* Disputes List */}
        <div className="flex-1">
          {loading ? (
            <div className="text-center py-12 text-slate-400">Loading disputes...</div>
          ) : disputes.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400">
              No disputes found. When a party raises a dispute, it will appear here.
            </div>
          ) : (
            <div className="space-y-3">
              {disputes.map((dispute) => (
                <div
                  key={dispute.id}
                  onClick={() => setSelectedDispute(dispute)}
                  className={`bg-white rounded-xl border p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedDispute?.id === dispute.id ? "border-orange-400 ring-1 ring-orange-200" : "border-slate-200"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[dispute.status] || "bg-slate-100"}`}>
                          {dispute.status}
                        </span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLORS[dispute.severity] || ""}`}>
                          {dispute.severity}
                        </span>
                      </div>
                      <h3 className="font-semibold text-slate-900 truncate">{dispute.title}</h3>
                      <p className="text-sm text-slate-500 mt-0.5">
                        Raised by {dispute.raised_by} ({dispute.raised_by_role}) &middot; {formatDate(dispute.created_at)}
                      </p>
                      {dispute.disputed_item && (
                        <p className="text-xs text-slate-400 mt-1">
                          Disputed: {dispute.disputed_item}
                          {dispute.disputed_value ? ` — ${dispute.disputed_value}` : ""}
                          {dispute.proposed_value ? ` → Proposed: ${dispute.proposed_value}` : ""}
                        </p>
                      )}
                      {dispute.assignee_name && (
                        <p className="text-xs text-blue-500 mt-1">Assigned to: {dispute.assignee_name}</p>
                      )}
                    </div>
                    <svg className="w-5 h-5 text-slate-300 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Detail Panel */}
        {selectedDispute && (
          <div className="w-[440px] flex-shrink-0">
            <div className="bg-white rounded-xl border border-slate-200 p-6 sticky top-6 max-h-[85vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-slate-900">Dispute Detail</h2>
                <span className={`inline-flex items-center px-2.5 py-1 rounded text-xs font-medium ${STATUS_COLORS[selectedDispute.status] || ""}`}>
                  {selectedDispute.status}
                </span>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-slate-500">Title:</span>
                  <span className="ml-2 text-slate-900 font-medium">{selectedDispute.title}</span>
                </div>
                <div>
                  <span className="text-slate-500">Raised by:</span>
                  <span className="ml-2 text-slate-900">{selectedDispute.raised_by} ({selectedDispute.raised_by_role})</span>
                </div>
                <div>
                  <span className="text-slate-500">Type:</span>
                  <span className="ml-2 text-slate-900">{DISPUTE_TYPE_LABELS[selectedDispute.dispute_type] || selectedDispute.dispute_type}</span>
                </div>
                <div>
                  <span className="text-slate-500">Severity:</span>
                  <span className={`ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLORS[selectedDispute.severity] || ""}`}>
                    {selectedDispute.severity}
                  </span>
                </div>

                {selectedDispute.description && (
                  <div>
                    <span className="text-slate-500 block mb-1">Description:</span>
                    <p className="text-slate-700 bg-slate-50 rounded-lg p-3">{selectedDispute.description}</p>
                  </div>
                )}

                {/* Disputed Values */}
                {(selectedDispute.disputed_item || selectedDispute.disputed_value) && (
                  <div className="bg-orange-50 rounded-lg p-3">
                    <p className="font-medium text-orange-900 mb-1">Disputed Item</p>
                    {selectedDispute.disputed_item && <p>Item: <strong>{selectedDispute.disputed_item}</strong></p>}
                    {selectedDispute.disputed_value && <p>Current value: <strong>{selectedDispute.disputed_value}</strong></p>}
                    {selectedDispute.proposed_value && <p>Proposed value: <strong>{selectedDispute.proposed_value}</strong></p>}
                  </div>
                )}

                {selectedDispute.assignee_name && (
                  <div>
                    <span className="text-slate-500">Assigned to:</span>
                    <span className="ml-2 text-slate-900">{selectedDispute.assignee_name}</span>
                  </div>
                )}

                {selectedDispute.resolution_outcome && (
                  <div className="bg-green-50 rounded-lg p-3">
                    <p className="font-medium text-green-900 mb-1">Resolution</p>
                    <p>Outcome: <strong>{selectedDispute.resolution_outcome}</strong></p>
                    {selectedDispute.resolution_notes && <p className="mt-1">{selectedDispute.resolution_notes}</p>}
                  </div>
                )}
              </div>

              {/* Comment Thread */}
              <div className="mt-4 pt-4 border-t border-slate-200">
                <p className="text-sm font-medium text-slate-700 mb-2">
                  Comments ({selectedDispute.comments.length})
                </p>
                <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
                  {selectedDispute.comments.map((comment) => (
                    <div key={comment.id} className={`text-xs rounded-lg p-2 ${comment.is_internal ? "bg-amber-50 border border-amber-200" : "bg-slate-50"}`}>
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-slate-700">{comment.author_name} ({comment.author_role})</span>
                        <span className="text-slate-400">{formatDate(comment.created_at)}</span>
                      </div>
                      <p className="text-slate-600 mt-0.5">{comment.comment}</p>
                      {comment.is_internal && <p className="text-amber-600 mt-0.5 italic">Internal — not visible to parties</p>}
                    </div>
                  ))}
                  {selectedDispute.comments.length === 0 && (
                    <p className="text-slate-400 text-center py-2">No comments yet</p>
                  )}
                </div>

                {/* Add Comment */}
                <div className="space-y-2">
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Add a comment..."
                    rows={2}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="flex items-center gap-3">
                    <label className="flex items-center gap-1.5 text-xs text-slate-600">
                      <input
                        type="checkbox"
                        checked={isInternal}
                        onChange={(e) => setIsInternal(e.target.checked)}
                        className="rounded border-slate-300"
                      />
                      Internal only
                    </label>
                    <button
                      onClick={addComment}
                      disabled={!newComment.trim()}
                      className="ml-auto px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Comment
                    </button>
                  </div>
                </div>
              </div>

              {/* Resolve / Assign Actions */}
              {selectedDispute.status !== "resolved" && selectedDispute.status !== "dismissed" && (
                <div className="mt-4 pt-4 border-t border-slate-200">
                  <p className="text-sm font-medium text-slate-700 mb-2">Actions</p>

                  {/* Assign */}
                  {!selectedDispute.assigned_to && (
                    <div className="mb-3">
                      <p className="text-xs text-slate-500 mb-1">Assign to:</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => assignDispute("admin_001")}
                          className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs font-medium hover:bg-slate-200"
                        >
                          Sarah Kimani
                        </button>
                        <button
                          onClick={() => assignDispute("admin_002")}
                          className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs font-medium hover:bg-slate-200"
                        >
                          James Ochieng
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Resolve */}
                  <div className="space-y-2">
                    <select
                      value={resolveOutcome}
                      onChange={(e) => setResolveOutcome(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white"
                    >
                      <option value="">Select resolution outcome...</option>
                      <option value="upheld">Upheld — original value is correct</option>
                      <option value="overturned">Overturned — proposed value accepted</option>
                      <option value="compromise">Compromise — middle ground reached</option>
                      <option value="dismissed">Dismissed — no basis for dispute</option>
                    </select>
                    <textarea
                      value={resolveNotes}
                      onChange={(e) => setResolveNotes(e.target.value)}
                      placeholder="Resolution notes..."
                      rows={2}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                    />
                    <button
                      onClick={resolveDispute}
                      disabled={!resolveOutcome}
                      className="w-full py-2 px-4 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Resolve Dispute
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
