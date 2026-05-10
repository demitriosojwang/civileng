export default function CalculationsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Calculations</h1>
        <p className="text-slate-500 mt-1">Individual engineering calculation modules</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { title: "Bearing Capacity", desc: "Terzaghi, Meyerhof, and Vesic methods for shallow foundations", code: "BS 8004 / EN 1997", color: "amber" },
          { title: "Foundation Selection", desc: "Decision tree for pad, strip, raft, or pile foundation type", code: "BS 8004", color: "blue" },
          { title: "Pad Foundation Design", desc: "Sizing, bending, shear, and deflection checks", code: "BS 8110", color: "green" },
          { title: "Strip Foundation Design", desc: "Continuous footing design for wall loads", code: "BS 8110", color: "green" },
          { title: "Raft Foundation Design", desc: "Preliminary raft sizing and bearing check", code: "BS 8004", color: "green" },
          { title: "Pile Capacity", desc: "Shaft friction and end bearing calculations", code: "BS 8004 Sec.7", color: "purple" },
          { title: "Beam Design", desc: "Bending, shear, and deflection per BS 8110", code: "BS 8110", color: "teal" },
          { title: "Column Design", desc: "Short braced column design per BS 8110", code: "BS 8110", color: "teal" },
          { title: "Load Combinations", desc: "EN 1990 / BS 6399 load combination generator", code: "EN 1990", color: "slate" },
          { title: "Soil Classification", desc: "BS 5930 / ISO 14688 soil classification", code: "BS 5930", color: "orange" },
          { title: "Bill of Quantities", desc: "Concrete, reinforcement, and formwork estimation", code: "General", color: "indigo" },
        ].map((calc) => (
          <div key={calc.title} className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-slate-900">{calc.title}</h3>
            <p className="text-sm text-slate-500 mt-1">{calc.desc}</p>
            <span className="inline-block mt-3 text-xs font-mono px-2 py-0.5 bg-slate-100 text-slate-600 rounded">
              {calc.code}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
