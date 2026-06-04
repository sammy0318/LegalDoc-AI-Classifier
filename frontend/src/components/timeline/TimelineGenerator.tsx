import { useEffect, useState } from "react";
import { useTimeline } from "../../hooks/useTimeline";
import { useDocumentStore } from "../../stores/document-store";
import { LoadingSpinner } from "../common/LoadingSpinner";

export function TimelineGenerator() {
  const language = useDocumentStore((s) => s.language);
  const results = useDocumentStore((s) => s.results);
  const { mutate, data, isPending, error, reset } = useTimeline();
  const [selectedDoc, setSelectedDoc] = useState<string>("");

  const completedDocs = results.filter(
    (r) => r.status === "completed" && r.raw_text
  );
  const activeDoc = completedDocs.find((doc) => doc.file_id === selectedDoc) ?? completedDocs[0] ?? null;

  useEffect(() => {
    if (completedDocs.length === 0) {
      setSelectedDoc("");
      return;
    }

    const firstDoc = completedDocs[0];
    if (!selectedDoc || !completedDocs.some((doc) => doc.file_id === selectedDoc)) {
      setSelectedDoc(firstDoc.file_id);
    }
  }, [completedDocs, selectedDoc]);

  useEffect(() => {
    if (!activeDoc?.raw_text) return;
    mutate({ documentText: activeDoc.raw_text, language });
  }, [activeDoc?.file_id, activeDoc?.raw_text, language, mutate]);

  const handleGenerate = () => {
    if (!activeDoc?.raw_text) return;
    mutate({ documentText: activeDoc.raw_text, language });
  };

  return (
    <div className="space-y-6">
      {/* Input Area */}
      <div className="parchment-card-elevated rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-lg bg-violet-50 flex items-center justify-center">
            <svg className="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 className="section-title">Legal Timeline</h3>
            <p className="text-xs font-body text-sepia-500">
              Extract dates, deadlines, and chronological events from your document
            </p>
          </div>
        </div>

        {completedDocs.length === 0 ? (
          <div className="text-center py-10 text-sepia-400 font-body text-sm">
            <svg className="h-10 w-10 mx-auto mb-3 text-sepia-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Upload and process documents first to generate timelines.
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              value={selectedDoc}
              onChange={(e) => { setSelectedDoc(e.target.value); reset(); }}
              className="input-field flex-1"
              title="Select a document for timeline"
            >
              <option value="">Select a document…</option>
              {completedDocs.map((doc, index) => (
                <option key={doc.file_id} value={doc.file_id}>
                  Document {index + 1}
                </option>
              ))}
            </select>
            <button
              onClick={handleGenerate}
              disabled={!selectedDoc || isPending}
              className="btn-primary whitespace-nowrap flex items-center gap-2"
            >
              {isPending ? (
                <>
                  <LoadingSpinner size="sm" />
                  Generating…
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Generate Timeline
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="parchment-card rounded-xl p-4 border-red-200 bg-red-50">
          <p className="text-sm font-body text-red-700">
            Failed to generate timeline. Please try again.
          </p>
        </div>
      )}

      {/* Results */}
      {data && (
        <div className="animate-fade-in">
          <div className="parchment-card-elevated rounded-xl p-5">
            <div className="flex items-center justify-between mb-5">
              <h4 className="font-serif font-semibold text-legal-brown text-lg">Document Timeline</h4>
              <span className="badge badge-gold">
                {data.event_count} event{data.event_count !== 1 ? "s" : ""}
              </span>
            </div>

            {/* Timeline Visual */}
            <div className="relative pl-8 space-y-6">
              {/* Vertical line */}
              <div className="absolute left-3 top-2 bottom-2 w-0.5 bg-gradient-to-b from-legal-gold via-legal-brown to-legal-gold/30" />

              {data.timeline.map((entry, index) => (
                <div key={index} className="relative group">
                  {/* Dot */}
                  <div className="absolute -left-5 top-1.5 h-3 w-3 rounded-full border-2 border-legal-brown bg-parchment-50 group-hover:bg-legal-gold transition-colors duration-200" />

                  <div className="parchment-card rounded-lg p-4 hover:shadow-parchment-md transition-shadow duration-200">
                    <div className="flex items-start gap-3">
                      <span className="flex-shrink-0 badge badge-gold text-xs">
                        {entry.date || `Event ${index + 1}`}
                      </span>
                      <p className="text-sm font-body text-sepia-700 leading-relaxed">
                        {entry.event}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
