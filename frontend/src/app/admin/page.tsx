"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ModerationStats {
  reviews_pending: number;
  reviews_in_review: number;
  reviews_approved_today: number;
  reviews_rejected_today: number;
  reviews_total: number;
  disputes_open: number;
  disputes_investigating: number;
  disputes_resolved_today: number;
  disputes_critical: number;
  disputes_total: number;
  blacklist_active: number;
  blacklist_pending_approval: number;
  blacklist_banned: number;
  blacklist_total: number;
  recent_activity: { type: string; id: string; description: string; timestamp: string }[];
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<ModerationStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/moderation/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-slate-400">Loading moderation dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Admin Moderation</h1>
        <p className="text-slate-500 mt-1">Review approvals, dispute resolution, and blacklist management</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Reviews Card */}
        <Link
          href="/admin/reviews"
          className="bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-400 hover:shadow-md transition-all group"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Reviews</h2>
            <span className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center group-hover:bg-blue-100">
              <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-2xl font-bold text-amber-600">{stats?.reviews_pending || 0}</p>
              <p className="text-xs text-slate-500">Pending</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">{stats?.reviews_in_review || 0}</p>
              <p className="text-xs text-slate-500">In Review</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{stats?.reviews_approved_today || 0}</p>
              <p className="text-xs text-slate-500">Approved Today</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{stats?.reviews_rejected_today || 0}</p>
              <p className="text-xs text-slate-500">Rejected Today</p>
            </div>
          </div>
          <p className="text-xs text-slate-400 mt-3">Total: {stats?.reviews_total || 0}</p>
        </Link>

        {/* Disputes Card */}
        <Link
          href="/admin/disputes"
          className="bg-white rounded-xl border border-slate-200 p-6 hover:border-orange-400 hover:shadow-md transition-all group"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Disputes</h2>
            <span className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center group-hover:bg-orange-100">
              <svg className="w-5 h-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-2xl font-bold text-amber-600">{stats?.disputes_open || 0}</p>
              <p className="text-xs text-slate-500">Open</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">{stats?.disputes_investigating || 0}</p>
              <p className="text-xs text-slate-500">Investigating</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{stats?.disputes_critical || 0}</p>
              <p className="text-xs text-slate-500">Critical</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{stats?.disputes_resolved_today || 0}</p>
              <p className="text-xs text-slate-500">Resolved Today</p>
            </div>
          </div>
          <p className="text-xs text-slate-400 mt-3">Total: {stats?.disputes_total || 0}</p>
        </Link>

        {/* Blacklist Card */}
        <Link
          href="/admin/blacklist"
          className="bg-white rounded-xl border border-slate-200 p-6 hover:border-red-400 hover:shadow-md transition-all group"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Blacklist</h2>
            <span className="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center group-hover:bg-red-100">
              <svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-2xl font-bold text-slate-900">{stats?.blacklist_active || 0}</p>
              <p className="text-xs text-slate-500">Active Entries</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{stats?.blacklist_banned || 0}</p>
              <p className="text-xs text-slate-500">Banned</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-600">{stats?.blacklist_pending_approval || 0}</p>
              <p className="text-xs text-slate-500">Pending Approval</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-400">{stats?.blacklist_total || 0}</p>
              <p className="text-xs text-slate-500">Total (incl. inactive)</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h2>
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          {stats?.recent_activity && stats.recent_activity.length > 0 ? (
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-slate-700">Type</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-700">Description</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-700">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stats.recent_activity.map((item, idx) => (
                  <tr key={idx}>
                    <td className="px-4 py-2">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        item.type === "review_action" ? "bg-blue-100 text-blue-800" : "bg-orange-100 text-orange-800"
                      }`}>
                        {item.type === "review_action" ? "Review" : "Dispute"}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-slate-600">{item.description}</td>
                    <td className="px-4 py-2 text-slate-400 text-xs">
                      {new Date(item.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-400">
              No recent activity. Actions will appear here as reviews and disputes are processed.
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/admin/reviews?status=pending"
            className="bg-white rounded-xl border border-slate-200 p-5 hover:border-amber-400 hover:shadow-md transition-all"
          >
            <h3 className="font-semibold text-slate-900">Pending Reviews</h3>
            <p className="text-sm text-slate-500 mt-1">View and approve pending design reviews</p>
          </Link>
          <Link
            href="/admin/disputes?status=open"
            className="bg-white rounded-xl border border-slate-200 p-5 hover:border-orange-400 hover:shadow-md transition-all"
          >
            <h3 className="font-semibold text-slate-900">Open Disputes</h3>
            <p className="text-sm text-slate-500 mt-1">Investigate and resolve open disputes</p>
          </Link>
          <Link
            href="/admin/blacklist"
            className="bg-white rounded-xl border border-slate-200 p-5 hover:border-red-400 hover:shadow-md transition-all"
          >
            <h3 className="font-semibold text-slate-900">Manage Blacklist</h3>
            <p className="text-sm text-slate-500 mt-1">Add, review, or remove blacklisted entities</p>
          </Link>
        </div>
      </div>
    </div>
  );
}
