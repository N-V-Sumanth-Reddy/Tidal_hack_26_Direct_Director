'use client';

import type { ProductionPack } from '@/lib/types';

interface ProductionStepProps {
  productionPack?: ProductionPack;
  onGenerateProduction?: () => void;
  onExport?: () => void;
  isGenerating?: boolean;
}

export function ProductionStep({
  productionPack,
  onGenerateProduction,
  onExport,
  isGenerating = false,
}: ProductionStepProps) {
  // If no production pack yet, show generate button
  if (!productionPack) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Generate Production Pack
              </h3>
              <p className="text-gray-600">
                Create comprehensive production documents including schedule, budget, crew, and locations
              </p>
            </div>
            <button
              onClick={onGenerateProduction}
              disabled={isGenerating}
              className="mt-4 px-6 py-3 bg-green-500 text-white font-medium rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors inline-flex items-center"
            >
              {isGenerating ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Generating...
                </>
              ) : (
                'Generate Production Pack'
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show production pack
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Production Pack</h2>
            <p className="text-gray-600 mt-1">
              Generated {new Date(productionPack.generatedAt).toLocaleDateString()}
            </p>
            {productionPack.error && (
              <p className="text-amber-600 text-sm mt-1">
                ⚠ Some data may be incomplete due to generation errors
              </p>
            )}
          </div>
          <button
            onClick={onExport}
            className="px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors inline-flex items-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Export All
          </button>
        </div>
      </div>

      {/* Scene Plan */}
      {productionPack.scenePlan && productionPack.scenePlan.scenes && productionPack.scenePlan.scenes.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Scene Breakdown ({productionPack.scenePlan.scenes.length} scenes, {productionPack.scenePlan.shots?.length || 0} shots)
          </h3>
          <div className="space-y-4">
            {productionPack.scenePlan.scenes.map((scene, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {scene.scene_id} - {scene.location_description}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {scene.location_type} • {scene.time_of_day} • {scene.duration_sec}s • {scene.cast_count} cast
                    </p>
                  </div>
                </div>
                {scene.props && scene.props.length > 0 && (
                  <div className="mt-2">
                    <span className="text-sm font-medium text-gray-700">Props: </span>
                    <span className="text-sm text-gray-600">{scene.props.join(', ')}</span>
                  </div>
                )}
                {scene.wardrobe && scene.wardrobe.length > 0 && (
                  <div className="mt-1">
                    <span className="text-sm font-medium text-gray-700">Wardrobe: </span>
                    <span className="text-sm text-gray-600">{scene.wardrobe.join(', ')}</span>
                  </div>
                )}
                {scene.dialogue_vo && (
                  <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-gray-700">
                    <span className="font-medium">Dialogue/VO: </span>{scene.dialogue_vo}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Locations */}
      {productionPack.locations && productionPack.locations.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Locations</h3>
          <div className="space-y-4">
            {productionPack.locations.map((location, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{location.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">{location.type}</span> - {location.requirements}
                    </p>
                    {location.alternates && location.alternates.length > 0 && (
                      <div className="mt-2">
                        <span className="text-sm font-medium text-gray-700">Alternates: </span>
                        <span className="text-sm text-gray-600">{location.alternates.join(', ')}</span>
                      </div>
                    )}
                    {location.permits_required && location.permits_required.length > 0 && (
                      <div className="mt-2 p-2 bg-amber-50 rounded">
                        <span className="text-sm font-medium text-gray-700">Permits Required: </span>
                        <span className="text-sm text-gray-600">{location.permits_required.join(', ')}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Crew */}
      {productionPack.crew && productionPack.crew.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Crew Requirements</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {productionPack.crew.map((member, index) => (
              <div key={index} className="flex items-start gap-3 p-4 border border-gray-200 rounded-lg">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {member.role}
                    {member.required && <span className="ml-2 text-xs text-red-600">*Required</span>}
                  </p>
                  <p className="text-sm text-gray-600">{member.responsibilities}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Legal & Clearances */}
      {productionPack.legal && productionPack.legal.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Legal & Clearances</h3>
          <div className="space-y-2">
            {productionPack.legal.map((item, index) => (
              <div 
                key={index} 
                className={`flex items-start gap-3 p-3 rounded-lg ${
                  item.high_risk ? 'bg-red-50 border border-red-200' : 'bg-gray-50'
                }`}
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {item.item}
                    {item.high_risk && <span className="ml-2 text-xs text-red-600">HIGH RISK</span>}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                  {item.quantity && (
                    <p className="text-xs text-gray-500 mt-1">Quantity: {item.quantity}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Register */}
      {productionPack.risks && productionPack.risks.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Register</h3>
          <div className="space-y-3">
            {productionPack.risks.map((risk, index) => {
              const getSeverityColor = (likelihood: string, impact: string) => {
                if (likelihood === 'HIGH' || impact === 'HIGH') return 'bg-red-50 border-red-200';
                if (likelihood === 'MEDIUM' || impact === 'MEDIUM') return 'bg-amber-50 border-amber-200';
                return 'bg-green-50 border-green-200';
              };

              return (
                <div key={index} className={`p-4 border rounded-lg ${getSeverityColor(risk.likelihood, risk.impact)}`}>
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{risk.risk}</h4>
                    <div className="flex gap-2">
                      <span className="text-xs px-2 py-1 bg-white rounded border border-gray-300">
                        L: {risk.likelihood}
                      </span>
                      <span className="text-xs px-2 py-1 bg-white rounded border border-gray-300">
                        I: {risk.impact}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Mitigation: </span>
                    {risk.mitigation}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
