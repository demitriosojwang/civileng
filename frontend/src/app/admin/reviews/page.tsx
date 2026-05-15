"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ReviewAction {
  id: string;
  admin_id: string;
  action: string;
  comment: string;
  old_status: string;
  new_status: string;
  created_at: string;
  admin_name?: string;
}

interface Review {
  id: string;
  project_id: string;
  submitted_by: string;
  submitted_by_email: string;
  title: string;
  description: string;
  review_type: string;
  priority: string;
  foundation_type: string;
  bearing_capacity_kPa: number | null;
  total_concrete_m3: number | null;
  total_rebar_kg: number | null;
  confidence_score: number | null;
  standards_used: string[];
  compliance_notes: string;
  has_warnings: boolean;
  warning_count: number;
  status: string;
  assigned_reviewer: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  actions: ReviewAction[];
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-amber-100 text-amber-800",
  in_review: "bg-blue-100 text-blue-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  revisions_needed: "bg-purple-100 text-purple-800",
};

const PRIORITY_COLORS: Record<string, string> = {
  urgent: "bg-red-100 text-red-800",
  high: "bg-orange-100 text-orange-800",
  normal: "bg-slate-100 text-slate-700",
  low: "bg-gray-100 text-gray-600",
};

export default function ReviewsPage() {
  const searchParams = useSearchParams();
  const initialStatus = searchParams.get("status") || "";

  const [reviews, setReviews] = useState<Review[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState(initialStatus);
  const [filterPriority, setFilterPriority] = useState("");
  const [filterType, setFilterType] = useState("");
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);
  const [actionComment, setActionComment] = useState("");
  const [actionType, setActionType] = useState("approved");

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.set("status", filterStatus);
      if (filterPriority) params.set("priority", filterPriority);
      if (filterType) params.set("review_type", filterType);
      const res = await fetch(`${API_BASE}/api/moderation/reviews?${params}`);
      const data = await res.json();
      setReviews(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, [filterStatus, filterPriority, filterType]);

  const handleAction = async (reviewId: string) => {
    try {
      await fetch(`${API_BASE}/api/moderation/reviews/${reviewId}/actions?admin_id=admin_001`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: actionType, comment: actionComment }),
      });
      setActionComment("");
      fetchReviews();
      if (selectedReview?.id === reviewId) {
        const res = await fetch(`${API_BASE}/api/moderation/reviews/${reviewId}`);
        setSelectedReview(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Review Approvals</h1>
        <p className="text-slate-500 mt-1">Approve or reject submitted designs, calculations, and reports</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="in_review">In Review</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="revisions_needed">Revisions Needed</option>
        </select>

        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Priorities</option>
          <option value="urgent">Urgent</option>
          <option value="high">High</option>
          <option value="normal">Normal</option>
          <option value="low">Low</option>
        </select>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Types</option>
          <option value="design_approval">Design Approval</option>
          <option value="calculation_check">Calculation Check</option>
          <option value="report_review">Report Review</option>
        </select>

        <span className="self-center text-sm text-slate-400">{total} reviews</span>
      </div>

      <div className="flex gap-6">
        {/* Review List */}
        <div className="flex-1">
          {loading ? (
            <div className="text-center py-12 text-slate-400">Loading reviews...</div>
          ) : reviews.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400">
              No reviews found. Submit a design for review to see it here.
            </div>
          ) : (
            <div className="space-y-3">
              {reviews.map((review) => (
                <div
                  key={review.id}
                  onClick={() => setSelectedReview(review)}
                  className={`bg-white rounded-xl border p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedReview?.id === review.id ? "border-blue-400 ring-1 ring-blue-200" : "border-slate-200"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[review.status] || "bg-slate-100 text-slate-700"}`}>
                          {review.status.replace("_", " ")}
                        </span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${PRIORITY_COLORS[review.priority] || ""}`}>
                          {review.priority}
                        </span>
                        {review.has_warnings && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
                            {review.warning_count} warning{review.warning_count !== 1 ? "s" : ""}
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-slate-900 truncate">
                        {review.title || `${review.review_type.replace(/_/g, " ")} — ${review.id}`}
                      </h3>
                      <p className="text-sm text-slate-500 mt-0.5">
                        Submitted by {review.submitted_by} &middot; {formatDate(review.created_at)}
                      </p>
                      {review.foundation_type && (
                        <p className="text-xs text-slate-400 mt-1">
                          Foundation: {review.foundation_type}
                          {review.bearing_capacity_kPa ? ` | q=${review.bearing_capacity_kPa} kPa` : ""}
                          {review.confidence_score ? ` | Confidence: ${(review.confidence_score * 100).toFixed(0)}%` : ""}
                        </p>
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
        {selectedReview && (
          <div className="w-[440px] flex-shrink-0">
            <div className="bg-white rounded-xl border border-slate-200 p-6 sticky top-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-slate-900">Review Detail</h2>
                <span className={`inline-flex items-center px-2.5 py-1 rounded text-xs font-medium ${STATUS_COLORS[selectedReview.status] || ""}`}>
                  {selectedReview.status.replace(/_/g, " ")}
                </span>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-slate-500">Title:</span>
                  <span className="ml-2 text-slate-900 font-medium">{selectedReview.title || "—"}</span>
                </div>
                <div>
                  <span className="text-slate-500">Submitted by:</span>
                  <span className="ml-2 text-slate-900">{selectedReview.submitted_by}</span>
                </div>
                <div>
                  <span className="text-slate-500">Type:</span>
                  <span className="ml-2 text-slate-900">{selectedReview.review_type.replace(/_/g, " ")}</span>
                </div>
                <div>
                  <span className="text-slate-500">Priority:</span>
                  <span className="ml-2 text-slate-900">{selectedReview.priority}</span>
                </div>

                {selectedReview.description && (
                  <div>
                    <span className="text-slate-500 block mb-1">Description:</span>
                    <p className="text-slate-700 bg-slate-50 rounded-lg p-3">{selectedReview.description}</p>
                  </div>
                )}

                {/* Design Summary */}
                {(selectedReview.foundation_type || selectedReview.bearing_capacity_kPa) && (
                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="font-medium text-blue-900 mb-1">Design Summary</p>
                    {selectedReview.foundation_type && <p>Foundation: <strong>{selectedReview.foundation_type}</strong></p>}
                    {selectedReview.bearing_capacity_kPa && <p>Bearing capacity: <strong>{selectedReview.bearing_capacity_kPa} kPa</strong></p>}
                    {selectedReview.total_concrete_m3 && <p>Concrete: <strong>{selectedReview.total_concrete_m3} m3</strong></p>}
                    {selectedReview.total_rebar_kg && <p>Rebar: <strong>{selectedReview.total_rebar_kg} kg</strong></p>}
                    {selectedReview.confidence_score && <p>Confidence: <strong>{(selectedReview.confidence_score * 100).toFixed(0)}%</strong></p>}
                  </div>
                )}

                {/* Standards */}
                {selectedReview.standards_used.length > 0 && (
                  <div>
                    <span className="text-slate-500 block mb-1">Standards Used:</span>
                    <div className="flex flex-wrap gap-1">
                      {selectedReview.standards_used.map((s) => (
                        <span key={s} className="inline-flex items-center px-2 py-0.5 rounded bg-slate-100 text-xs font-mono text-slate-700">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedReview.compliance_notes && (
                  <div>
                    <span className="text-slate-500 block mb-1">Compliance Notes:</span>
                    <p className="text-slate-700 bg-slate-50 rounded-lg p-3">{selectedReview.compliance_notes}</p>
                  </div>
                )}
              </div>

              {/* Action History */}
              {selectedReview.actions.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-200">
                  <p className="text-sm font-medium text-slate-700 mb-2">Action History</p>
                  <div className="space-y-2">
                    {selectedReview.actions.map((action) => (
                      <div key={action.id} className="text-xs bg-slate-50 rounded-lg p-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-slate-700">{action.action.replace(/_/g, " ")}</span>
                          <span className="text-slate-400">{formatDate(action.created_at)}</span>
                        </div>
                        {action.comment && <p className="text-slate-500 mt-0.5">{action.comment}</p>}
                        <p className="text-slate-400 mt-0.5">by {action.admin_name || action.admin_id}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Form */}
              {(selectedReview.status === "pending" || selectedReview.status === "in_review" || selectedReview.status === "revisions_needed") && (
                <div className="mt-4 pt-4 border-t border-slate-200">
                  <p className="text-sm font-medium text-slate-700 mb-2">Take Action</p>
                  <div className="space-y-3">
                    <select
                      value={actionType}
                      onChange={(e) => setActionType(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="approved">Approve</option>
                      <option value="rejected">Reject</option>
                      <option value="requested_revision">Request Revision</option>
                      <option value="escalated">Escalate</option>
                      <option value="commented">Comment Only</option>
                    </select>
                    <textarea
                      value={actionComment}
                      onChange={(e) => setActionComment(e.target.value)}
                      placeholder="Add a comment (optional)..."
                      rows={3}
                      className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={() => handleAction(selectedReview.id)}
                      className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                        actionType === "approved"
                          ? "bg-green-600 text-white hover:bg-green-700"
                          : actionType === "rejected"
                          ? "bg-red-600 text-white hover:bg-red-700"
                          : "bg-blue-600 text-white hover:bg-blue-700"
                      }`}
                    >
                      {actionType === "approved" ? "Approve" : actionType === "rejected" ? "Reject" : actionType === "requested_revision" ? "Request Revision" : actionType === "escalated" ? "Escalate" : "Submit Comment"}
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
