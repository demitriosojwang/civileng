import Link from "next/link";

export default function DashboardPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-500 mt-1">Foundation & Structural Design Platform</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-sm text-slate-500 font-medium">Active Projects</p>
          <p className="text-3xl font-bold text-slate-900 mt-1">0</p>
          <p className="text-xs text-slate-400 mt-1">Create your first project</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-sm text-slate-500 font-medium">Site Assessments</p>
          <p className="text-3xl font-bold text-slate-900 mt-1">0</p>
          <p className="text-xs text-slate-400 mt-1">Start a site assessment</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-sm text-slate-500 font-medium">Designs Completed</p>
          <p className="text-3xl font-bold text-slate-900 mt-1">0</p>
          <p className="text-xs text-slate-400 mt-1">Run foundation design</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-sm text-slate-500 font-medium">Reports Generated</p>
          <p className="text-3xl font-bold text-slate-900 mt-1">0</p>
          <p className="text-xs text-slate-400 mt-1">Generate PDF reports</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/assessment"
            className="bg-white rounded-xl border border-slate-200 p-6 hover:border-amber-400 hover:shadow-md transition-all group"
          >
            <div className="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center mb-3 group-hover:bg-amber-100">
              <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-900">New Site Assessment</h3>
            <p className="text-sm text-slate-500 mt-1">Capture site data and classify soil conditions</p>
          </Link>

          <Link
            href="/calculations"
            className="bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-400 hover:shadow-md transition-all group"
          >
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-100">
              <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-900">Run Calculations</h3>
            <p className="text-sm text-slate-500 mt-1">Bearing capacity, foundation design, structural analysis</p>
          </Link>

          <Link
            href="/reports"
            className="bg-white rounded-xl border border-slate-200 p-6 hover:border-green-400 hover:shadow-md transition-all group"
          >
            <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center mb-3 group-hover:bg-green-100">
              <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-900">Generate Reports</h3>
            <p className="text-sm text-slate-500 mt-1">PDF foundation design reports for tendering</p>
          </Link>
        </div>
      </div>

      {/* Supported Standards */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Supported Standards</h2>
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Code</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr><td className="px-4 py-2 font-mono text-xs">BS 8004</td><td className="px-4 py-2 text-slate-600">Code of practice for foundations</td></tr>
              <tr><td className="px-4 py-2 font-mono text-xs">BS 8110</td><td className="px-4 py-2 text-slate-600">Structural use of concrete</td></tr>
              <tr><td className="px-4 py-2 font-mono text-xs">BS 5930</td><td className="px-4 py-2 text-slate-600">Code of practice for ground investigations</td></tr>
              <tr><td className="px-4 py-2 font-mono text-xs">EN 1990</td><td className="px-4 py-2 text-slate-600">Eurocode 0 — Basis of structural design</td></tr>
              <tr><td className="px-4 py-2 font-mono text-xs">EN 1997</td><td className="px-4 py-2 text-slate-600">Eurocode 7 — Geotechnical design</td></tr>
              <tr><td className="px-4 py-2 font-mono text-xs">ISO 14688</td><td className="px-4 py-2 text-slate-600">Geotechnical identification and classification</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
