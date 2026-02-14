import { useState, useRef, useEffect } from "react";
import { evaluateAnswerApi } from "../services/api";
import "../App.css";
import { FaMicrophone, FaStop } from "react-icons/fa";

interface Props {
  questions: string[];
  onFinish: (score: number) => void;
}

export default function Questions({ questions, onFinish }: Props) {
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [grade, setGrade] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<number[]>([]);
  const [finalScore, setFinalScore] = useState<number | null>(null);
  const [listening, setListening] = useState(false);

  const recognitionRef = useRef<any>(null);
  const manuallyStopped = useRef(false);

  // persistent text memory
  const finalTranscriptRef = useRef("");

  useEffect(() => {
    // stop recording if user goes next
    manuallyStopped.current = true;
    recognitionRef.current?.stop();
    setListening(false);

    // clear speech memory
    finalTranscriptRef.current = "";
  }, [current]);

  if (!questions.length) return null;

  // =====================
  // Evaluate answer
  // =====================
  const SpeechRecognition =
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition;

  const startListening = () => {
    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser");
      return;
    }

    manuallyStopped.current = false;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onresult = (event: any) => {
      let interim = "";
      let finalPart = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          finalPart += text;
        } else {
          interim += text;
        }
      }

      // append only finalized speech to memory
      if (finalPart) {
        finalTranscriptRef.current += finalPart + " ";
      }

      // show final + live
      const fullText = finalTranscriptRef.current + interim;
      updateAnswer(fullText);
    };

    // restart unless user pressed stop
    recognition.onend = () => {
      if (!manuallyStopped.current) {
        recognition.start();
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  };

  const stopListening = () => {
    manuallyStopped.current = true;
    recognitionRef.current?.stop();
    setListening(false);
  };


  const handleNext = async () => {
    const answer = answers[current];

    if (!answer) {
      alert("Please type an answer");
      return;
    }

    if (loading) return; // extra safety

    setLoading(true);

    try {
      const result = await evaluateAnswerApi(
        questions[current],
        answer
      );

      setGrade(result);

      const copy = [...results];
      copy[current] = result.score;
      setResults(copy);
    } catch (e) {
      alert("Failed to evaluate");
    }

    setLoading(false);
  };

  const updateAnswer = (value: string) => {
    const copy = [...answers];
    copy[current] = value;
    setAnswers(copy);
  };

  // =====================
  // If interview finished
  // =====================
  if (finalScore !== null) {
    return (
      <div>
        <h2>Interview Finished 🎉</h2>
        <p>
          Final Score: {finalScore} / {questions.length}
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* =====================
          QUESTION BLOCK
         ===================== */}
      <div key={current}>
        <h3>
          Question {current + 1} of {questions.length}
        </h3>

        <p>{questions[current]}</p>

        <textarea
          rows={6}
          placeholder="Type your answer here..."
          value={answers[current] || ""}
          onChange={(e) => updateAnswer(e.target.value)}
        />
        <div className="voiceRow">
          {!listening ? (
            <button type="button" onClick={startListening} className="micButton">
              <FaMicrophone />
            </button>
          ) : (
            <button type="button" onClick={stopListening} className="micButton recording">
              <FaStop />
            </button>
          )}

          <span className="muted">
            {listening ? "Recording... press stop when finished" : "Answer with your voice"}
          </span>
        </div>



      </div>

      {loading && <p>Evaluating...</p>}

      {/* =====================
           SHOW GRADE
         ===================== */}
      {grade && (
        <>
          <p>
            <b>Score:</b> {grade.score} / 1
          </p>

          <div>
            <p>{grade.correct ? "Correct" : "Needs improvement"}</p>
            <p>{grade.feedback}</p>
          </div>

          <button
            onClick={() => {
              setGrade(null);

              if (current < questions.length - 1) {
                setCurrent(current + 1);
              } else {
                const total = results.reduce((a, b) => a + b, 0);
                setFinalScore(total);
                onFinish(total);
              }
            }}
          >
            Continue
          </button>
        </>
      )}

      {/* =====================
           NEXT BUTTON
         ===================== */}
      {!grade && (
        <button
          onClick={handleNext}
          disabled={loading}
        >
          {loading
            ? "..."
            : current === questions.length - 1
            ? "Finish"
            : "Next"}
        </button>
      )}
    </div>
  );
}
