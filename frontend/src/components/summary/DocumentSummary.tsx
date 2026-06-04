import { useEffect, useState } from "react";
import { useDocumentSummary } from "../../hooks/useDocumentSummary";
import { useDocumentStore } from "../../stores/document-store";
import { LoadingSpinner } from "../common/LoadingSpinner";

export function DocumentSummary() {
  const language = useDocumentStore((s) => s.language);
  const results = useDocumentStore((s) => s.results);
  const { mutate, data, isPending, error, reset } = useDocumentSummary();
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
    mutate({ documentText: activeDoc.raw_text, language, detailLevel: "standard" });
  }, [activeDoc?.file_id, activeDoc?.raw_text, language, mutate]);

  const handleSummarize = () => {
    if (!activeDoc?.raw_text) return;
    mutate({ documentText: activeDoc.raw_text, language, detailLevel: "standard" });
  };

  return (
    <div className="space-y-6">
      {/* Input Area */}
      <div className="parchment-card-elevated rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center">
            <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h3 className="section-title">AI Document Summary</h3>
            <p className="text-xs font-body text-sepia-500">
              Generate an intelligent summary of your legal document
            </p>
          </div>
        </div>

        {completedDocs.length === 0 ? (
          <div className="text-center py-10 text-sepia-400 font-body text-sm">
            <svg className="h-10 w-10 mx-auto mb-3 text-sepia-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Upload and process documents first to generate summaries.
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <select
                value={selectedDoc}
                onChange={(e) => { setSelectedDoc(e.target.value); reset(); }}
                className="input-field flex-1"
                title="Select a document to summarize"
              >
                <option value="">Select a document…</option>
                  {completedDocs.map((doc, index) => (
                    <option key={doc.file_id} value={doc.file_id}>
                      Document {index + 1}
                    </option>
                  ))}
              </select>
            </div>

            <button
              onClick={handleSummarize}
              disabled={!selectedDoc || isPending}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isPending ? (
                <>
                  <LoadingSpinner size="sm" />
                  Summarizing…
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Generate Summary
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
            Failed to generate summary. Please try again.
          </p>
        </div>
      )}

      {/* Results */}
      {data && (
        <div className="space-y-4 animate-fade-in">
          {/* Summary */}
          <div className="parchment-card-elevated rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-serif font-semibold text-legal-brown text-lg">Summary</h4>
              <span className="badge badge-info">{data.word_count} words</span>
            </div>
            <p className="text-sm font-body text-sepia-700 leading-relaxed whitespace-pre-line">
              {data.summary}
            </p>
          </div>

          {/* Key Points */}
          {data.key_points.length > 0 && (
            <div className="parchment-card rounded-xl p-5">
              <h4 className="font-serif font-semibold text-legal-brown mb-4">Key Points</h4>
              <ul className="space-y-2">
                {data.key_points.map((point, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="flex-shrink-0 h-6 w-6 rounded-full bg-legal-gold/20 text-legal-brown flex items-center justify-center text-xs font-body font-bold">
                      {index + 1}
                    </span>
                    <span className="text-sm font-body text-sepia-700 leading-relaxed pt-0.5">{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
