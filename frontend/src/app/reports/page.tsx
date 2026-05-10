export default function ReportsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Reports</h1>
        <p className="text-slate-500 mt-1">Generate and download engineering reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-2">Foundation Design Report</h3>
          <p className="text-sm text-slate-500 mb-4">Complete foundation design with bearing capacity analysis, foundation sizing, reinforcement details, and Bill of Quantities.</p>
          <p className="text-xs text-slate-400">Includes: Soil classification, bearing capacity (3 methods), foundation recommendation, detailed design, BOQ</p>
          <a href="/assessment" className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 transition-colors text-sm">
            Generate Report
          </a>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 opacity-60">
          <h3 className="font-semibold text-slate-900 mb-2">Structural Design Report</h3>
          <p className="text-sm text-slate-500 mb-4">Full structural design report with beam, column, and slab calculations.</p>
          <p className="text-xs text-slate-400">Available in Phase 3</p>
          <button disabled className="mt-4 px-4 py-2 bg-slate-200 text-slate-500 font-medium rounded-lg text-sm cursor-not-allowed">
            Coming Soon
          </button>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 opacity-60">
          <h3 className="font-semibold text-slate-900 mb-2">Site Investigation Report</h3>
          <p className="text-sm text-slate-500 mb-4">Comprehensive site investigation report from captured assessment data.</p>
          <p className="text-xs text-slate-400">Available in Phase 2 (next update)</p>
          <button disabled className="mt-4 px-4 py-2 bg-slate-200 text-slate-500 font-medium rounded-lg text-sm cursor-not-allowed">
            Coming Soon
          </button>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 opacity-60">
          <h3 className="font-semibold text-slate-900 mb-2">Tender Package</h3>
          <p className="text-sm text-slate-500 mb-4">Complete tender documentation with design reports, BOQ, and specifications.</p>
          <p className="text-xs text-slate-400">Available in Phase 5</p>
          <button disabled className="mt-4 px-4 py-2 bg-slate-200 text-slate-500 font-medium rounded-lg text-sm cursor-not-allowed">
            Coming Soon
          </button>
        </div>
      </div>
    </div>
  );
}
