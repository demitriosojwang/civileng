"use client";

import { useState } from "react";

const SOIL_TEXTURES = ["Sandy", "Clayey", "Silty", "Gravelly", "Sandy Clay", "Silty Clay", "Clayey Sand"];
const TERRAIN_TYPES = ["flat", "gentle_slope", "moderate_slope", "steep_slope"];
const GROUNDWATER = ["none_observed", "moist", "wet", "water_seepage", "standing_water"];
const BUILDING_TYPES = ["residential", "commercial", "industrial", "infrastructure", "civil_works"];

export default function AssessmentPage() {
  const [formData, setFormData] = useState({
    project_name: "",
    engineer_name: "",
    terrain_type: "flat",
    slope_angle_deg: 0,
    groundwater_condition: "none_observed",
    water_table_depth_m: "",
    soil_color: "",
    soil_texture: "Sandy",
    soil_moisture: "dry",
    pct_gravel: 0,
    pct_sand: 40,
    pct_silt: 30,
    pct_clay: 30,
    pct_organic: 0,
    cohesion_kPa: "",
    angle_of_shearing_resistance_deg: "",
    unit_weight_kN_m3: "",
    building_type: "residential",
    number_of_stories: 2,
    column_load_kN: 500,
    total_building_load_kN: 5000,
    footprint_area_m2: 200,
    concrete_grade: "C30",
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/reports/pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          project_id: `proj_${Date.now()}`,
          assessment_date: new Date().toISOString().split("T")[0],
          water_table_depth_m: formData.water_table_depth_m ? parseFloat(formData.water_table_depth_m) : null,
          cohesion_kPa: formData.cohesion_kPa ? parseFloat(formData.cohesion_kPa) : null,
          angle_of_shearing_resistance_deg: formData.angle_of_shearing_resistance_deg
            ? parseFloat(formData.angle_of_shearing_resistance_deg) : null,
          unit_weight_kN_m3: formData.unit_weight_kN_m3 ? parseFloat(formData.unit_weight_kN_m3) : null,
          location_description: "",
          drainage_description: "",
          soil_moisture: formData.soil_moisture,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Pipeline error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Site Assessment</h1>
        <p className="text-slate-500 mt-1">Capture site data and run the full design pipeline</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Project Info */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Project Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Project Name</label>
              <input type="text" name="project_name" value={formData.project_name} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-400 focus:border-transparent" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Engineer Name</label>
              <input type="text" name="engineer_name" value={formData.engineer_name} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-400 focus:border-transparent" required />
            </div>
          </div>
        </div>

        {/* Site Conditions */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Site Conditions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Terrain Type</label>
              <select name="terrain_type" value={formData.terrain_type} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                {TERRAIN_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Slope Angle (degrees)</label>
              <input type="number" name="slope_angle_deg" value={formData.slope_angle_deg} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" min="0" max="90" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Groundwater</label>
              <select name="groundwater_condition" value={formData.groundwater_condition} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                {GROUNDWATER.map((g) => <option key={g} value={g}>{g.replace("_", " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Water Table Depth (m)</label>
              <input type="number" name="water_table_depth_m" value={formData.water_table_depth_m} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" step="0.1" />
            </div>
          </div>
        </div>

        {/* Soil Data */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Soil Data</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Soil Color</label>
              <input type="text" name="soil_color" value={formData.soil_color} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" placeholder="e.g., brown, reddish" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Soil Texture</label>
              <select name="soil_texture" value={formData.soil_texture} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                {SOIL_TEXTURES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Moisture</label>
              <select name="soil_moisture" value={formData.soil_moisture} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                <option value="dry">Dry</option>
                <option value="moist">Moist</option>
                <option value="wet">Wet</option>
              </select>
            </div>
          </div>
          <p className="text-sm font-medium text-slate-700 mb-2">Particle Size Distribution (%) — must total 100%</p>
          <div className="grid grid-cols-5 gap-3">
            {["Gravel", "Sand", "Silt", "Clay", "Organic"].map((label) => {
              const key = `pct_${label.toLowerCase()}` as keyof typeof formData;
              return (
                <div key={key}>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{label}</label>
                  <input type="number" name={key} value={formData[key]} onChange={handleChange}
                    className="w-full px-2 py-1.5 border border-slate-300 rounded-lg text-sm" min="0" max="100" />
                </div>
              );
            })}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Cohesion cu (kPa)</label>
              <input type="number" name="cohesion_kPa" value={formData.cohesion_kPa} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" placeholder="Leave blank to estimate" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Angle of Shearing Resistance (deg)</label>
              <input type="number" name="angle_of_shearing_resistance_deg" value={formData.angle_of_shearing_resistance_deg}
                onChange={handleChange} className="w-full px-3 py-2 border border-slate-300 rounded-lg" placeholder="Leave blank to estimate" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Unit Weight (kN/m3)</label>
              <input type="number" name="unit_weight_kN_m3" value={formData.unit_weight_kN_m3} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" placeholder="Default: 18" />
            </div>
          </div>
        </div>

        {/* Building Parameters */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Building Parameters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Building Type</label>
              <select name="building_type" value={formData.building_type} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                {BUILDING_TYPES.map((b) => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Number of Stories</label>
              <input type="number" name="number_of_stories" value={formData.number_of_stories} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" min="1" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Column Load (kN)</label>
              <input type="number" name="column_load_kN" value={formData.column_load_kN} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Total Building Load (kN)</label>
              <input type="number" name="total_building_load_kN" value={formData.total_building_load_kN} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Footprint Area (m2)</label>
              <input type="number" name="footprint_area_m2" value={formData.footprint_area_m2} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Concrete Grade</label>
              <select name="concrete_grade" value={formData.concrete_grade} onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                {["C20", "C25", "C30", "C35", "C40", "C45", "C50"].map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full md:w-auto px-8 py-3 bg-amber-600 text-white font-semibold rounded-lg hover:bg-amber-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Running Pipeline..." : "Run Full Design Pipeline"}
        </button>
      </form>

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          <h2 className="text-xl font-bold text-slate-900">Pipeline Results</h2>

          {/* Soil Classification */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Soil Classification</h3>
            <p className="text-slate-600">{result.soil_classification?.bs5930_name}</p>
            <p className="text-sm text-slate-500 mt-1">
              Estimated bearing capacity: {result.soil_classification?.estimated_bearing_capacity_kPa} kPa
            </p>
          </div>

          {/* Bearing Capacity */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Bearing Capacity</h3>
            <p className="text-2xl font-bold text-amber-600">{result.recommended_bearing_capacity_kPa} kPa</p>
            <p className="text-sm text-slate-500">Recommended allowable bearing capacity (conservative)</p>
          </div>

          {/* Foundation Recommendation */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Foundation Recommendation</h3>
            <p className="text-2xl font-bold text-slate-900 uppercase">
              {result.foundation_recommendation?.recommended}
            </p>
            <p className="text-sm text-slate-500 mt-1">
              Confidence: {((result.foundation_recommendation?.confidence || 0) * 100).toFixed(0)}% |
              Cost: {result.foundation_recommendation?.cost_indicator} |
              Constructability: {result.foundation_recommendation?.constructability}
            </p>
            <p className="text-slate-600 mt-3">{result.foundation_recommendation?.justification}</p>
          </div>

          {/* Warnings */}
          {result.warnings?.length > 0 && (
            <div className="bg-amber-50 rounded-xl border border-amber-200 p-6">
              <h3 className="text-lg font-semibold text-amber-800 mb-3">Warnings</h3>
              <ul className="space-y-2">
                {result.warnings.map((w: string, i: number) => (
                  <li key={i} className="text-sm text-amber-700">- {w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
