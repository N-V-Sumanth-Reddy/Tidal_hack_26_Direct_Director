'use client';

import { useState } from 'react';

interface ExportStepProps {
  projectId: string;
  projectName: string;
}

export function ExportStep({ projectId, projectName }: ExportStepProps) {
  const [selectedFormats, setSelectedFormats] = useState<string[]>(['pdf']);
  const [isExporting, setIsExporting] = useState(false);
  const [exportComplete, setExportComplete] = useState(false);

  const formats = [
    { id: 'pdf', name: 'PDF Document', description: 'Complete production pack as PDF', icon: '📄' },
    { id: 'docx', name: 'Word Document', description: 'Editable Word format', icon: '📝' },
    { id: 'json', name: 'JSON Data', description: 'Raw data for integration', icon: '🔧' },
    { id: 'zip', name: 'ZIP Archive', description: 'All files in one archive', icon: '📦' },
  ];

  const handleFormatToggle = (formatId: string) => {
    setSelectedFormats(prev =>
      prev.includes(formatId)
        ? prev.filter(f => f !== formatId)
        : [...prev, formatId]
    );
  };

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      // Export each selected format
      for (const format of selectedFormats) {
        let url = '';
        
        switch (format) {
          case 'json':
            url = `/api/projects/${projectId}/export/json`;
            break;
          case 'pdf':
          case 'docx':
            // Use markdown for now (PDF/DOCX would need additional libraries)
            url = `/api/projects/${projectId}/export/markdown`;
            break;
          case 'zip':
            url = `/api/projects/${projectId}/export/zip`;
            break;
          default:
            continue;
        }
        
        // Fetch and download the file
        const response = await fetch(`http://localhost:2501${url}`);
        
        if (!response.ok) {
          throw new Error(`Export failed for ${format}`);
        }
        
        // Get filename from Content-Disposition header or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `${projectName}_${format}.${format}`;
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        // Download the file
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
        
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      setIsExporting(false);
      setExportComplete(true);
      
      // Reset after 3 seconds
      setTimeout(() => setExportComplete(false), 3000);
    } catch (error) {
      console.error('Export error:', error);
      setIsExporting(false);
      alert('Export failed. Please try again.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-purple-600"
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
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Export Project</h2>
          <p className="text-gray-600">
            Download your complete production package in multiple formats
          </p>
        </div>
      </div>

      {/* Format Selection */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Export Formats</h3>
        <div className="space-y-3">
          {formats.map(format => (
            <label
              key={format.id}
              className="flex items-start gap-4 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 transition-colors"
            >
              <input
                type="checkbox"
                checked={selectedFormats.includes(format.id)}
                onChange={() => handleFormatToggle(format.id)}
                className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{format.icon}</span>
                  <span className="font-medium text-gray-900">{format.name}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{format.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Export Contents */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">What's Included</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { name: 'Project Brief', icon: '📋' },
            { name: 'Creative Concept', icon: '💡' },
            { name: 'Selected Screenplay', icon: '🎬' },
            { name: 'Storyboard Frames', icon: '🎨' },
            { name: 'Production Schedule', icon: '📅' },
            { name: 'Budget Breakdown', icon: '💰' },
            { name: 'Crew Requirements', icon: '👥' },
            { name: 'Location Details', icon: '📍' },
            { name: 'Equipment List', icon: '🎥' },
            { name: 'Legal Documents', icon: '📜' },
          ].map((item, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <span className="text-xl">{item.icon}</span>
              <span className="text-gray-900">{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Export Button */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">
              {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Project: {projectName}
            </p>
          </div>
          <button
            onClick={handleExport}
            disabled={selectedFormats.length === 0 || isExporting}
            className="px-8 py-3 bg-purple-500 text-white font-medium rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors inline-flex items-center"
          >
            {isExporting ? (
              <>
                <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Exporting...
              </>
            ) : exportComplete ? (
              <>
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
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Exported!
              </>
            ) : (
              <>
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
                Export Now
              </>
            )}
          </button>
        </div>
      </div>

      {/* Success Message */}
      {exportComplete && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-green-600 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <p className="font-medium text-green-900">Export Successful!</p>
              <p className="text-sm text-green-700 mt-1">
                Your files have been downloaded. Check your downloads folder.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
