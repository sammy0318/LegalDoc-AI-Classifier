import { useState, useRef, useCallback, useEffect } from "react";
import { useVoiceQuery } from "../../hooks/useVoiceQuery";
import { useDocumentStore } from "../../stores/document-store";
import { LoadingSpinner } from "../common/LoadingSpinner";

type ListeningState = "idle" | "listening" | "processing";

export function VoiceAssistant() {
  const language = useDocumentStore((s) => s.language);
  const { mutate, data, isPending, error, reset } = useVoiceQuery();
  const [transcript, setTranscript] = useState("");
  const [listeningState, setListeningState] = useState<ListeningState>("idle");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const isSupported = typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  const startListening = useCallback(() => {
    if (!isSupported) return;

    const SpeechRecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) return;

    const recognition = new SpeechRecognitionCtor();
    recognition.lang = language === "hi" ? "hi-IN" : "en-IN";
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onstart = () => setListeningState("listening");

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = "";
      for (let i = 0; i < event.results.length; i++) {
        finalTranscript += event.results[i][0].transcript;
      }
      setTranscript(finalTranscript);
    };

    recognition.onend = () => setListeningState("idle");
    recognition.onerror = () => setListeningState("idle");

    recognitionRef.current = recognition;
    recognition.start();
  }, [isSupported, language]);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setListeningState("idle");
  }, []);

  const handleSubmit = () => {
    if (!transcript.trim()) return;
    reset();
    mutate({ transcript: transcript.trim(), language });
  };

  const handleSpeak = useCallback((text: string) => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === "hi" ? "hi-IN" : "en-IN";
    utterance.rate = 0.9;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, [language]);

  const stopSpeaking = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
      window.speechSynthesis?.cancel();
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Voice Input Area */}
      <div className="parchment-card-elevated rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-lg bg-emerald-50 flex items-center justify-center">
            <svg className="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <div>
            <h3 className="section-title">Voice Legal Assistant</h3>
            <p className="text-xs font-body text-sepia-500">
              Speak your legal question or type it below
            </p>
          </div>
        </div>

        {!isSupported && (
          <div className="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-200">
            <p className="text-xs font-body text-amber-700">
              Speech recognition is not supported in your browser. You can still type your question below.
            </p>
          </div>
        )}

        {/* Mic Button */}
        <div className="flex flex-col items-center mb-5">
          <button
            onClick={listeningState === "listening" ? stopListening : startListening}
            disabled={!isSupported || isPending}
            className={`h-20 w-20 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg ${
              listeningState === "listening"
                ? "bg-red-500 text-white animate-pulse shadow-red-200"
                : "bg-legal-brown text-parchment-50 hover:bg-legal-darkbrown hover:shadow-xl"
            } disabled:opacity-40 disabled:cursor-not-allowed`}
          >
            {listeningState === "listening" ? (
              <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
            ) : (
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            )}
          </button>
          <p className="text-xs font-body text-sepia-400 mt-2">
            {listeningState === "listening" ? "Listening… tap to stop" : "Tap to speak"}
          </p>
        </div>

        {/* Transcript / Manual Input */}
        <div className="space-y-3">
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder={language === "hi" ? "अपना कानूनी सवाल यहाँ टाइप करें या बोलें…" : "Type or speak your legal question here…"}
            rows={3}
            className="input-field resize-none"
          />
          <button
            onClick={handleSubmit}
            disabled={!transcript.trim() || isPending}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {isPending ? (
              <>
                <LoadingSpinner size="sm" />
                Processing…
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Ask Legal AI
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="parchment-card rounded-xl p-4 border-red-200 bg-red-50">
          <p className="text-sm font-body text-red-700">
            Failed to process voice query. Please try again.
          </p>
        </div>
      )}

      {/* Result */}
      {data && (
        <div className="animate-fade-in space-y-4">
          {/* Transcript Echo */}
          <div className="parchment-card rounded-xl p-4">
            <p className="text-xs font-body text-sepia-400 mb-1">You asked:</p>
            <p className="text-sm font-body text-sepia-700 italic">"{data.transcript}"</p>
          </div>

          {/* Answer */}
          <div className="parchment-card-elevated rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-serif font-semibold text-legal-brown text-lg">Answer</h4>
              <div className="flex items-center gap-2">
                {data.confidence && (
                  <span className="badge badge-gold">{Math.round(data.confidence * 100)}%</span>
                )}
                <button
                  onClick={() => isSpeaking ? stopSpeaking() : handleSpeak(data.answer)}
                  className="btn-ghost p-1.5 rounded-lg"
                  title={isSpeaking ? "Stop speaking" : "Read aloud"}
                >
                  {isSpeaking ? (
                    <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-legal-brown" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            <p className="text-sm font-body text-sepia-700 leading-relaxed whitespace-pre-line">
              {data.answer}
            </p>
            {data.source && (
              <p className="mt-3 text-xs font-body text-sepia-400">
                Source: {data.source} &middot; Method: {data.method}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
