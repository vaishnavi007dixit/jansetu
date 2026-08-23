import { useRef, useState } from 'react'

// Records audio via MediaRecorder, hands the caller a base64 string on stop.
// Falls back gracefully (with a message) if mic access isn't available —
// this runs on a hackathon judge's laptop, not a controlled device.
export default function VoiceRecorder({ onRecorded, disabled }) {
  const [status, setStatus] = useState('idle') // idle | recording | recorded | error
  const [errorMsg, setErrorMsg] = useState('')
  const [durationSec, setDurationSec] = useState(0)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const timerRef = useRef(null)

  async function startRecording() {
    setErrorMsg('')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        const reader = new FileReader()
        reader.onloadend = () => {
          const base64 = reader.result.split(',')[1]
          onRecorded(base64)
        }
        reader.readAsDataURL(blob)
        clearInterval(timerRef.current)
        setStatus('recorded')
      }

      recorder.start()
      mediaRecorderRef.current = recorder
      setStatus('recording')
      setDurationSec(0)
      timerRef.current = setInterval(() => setDurationSec((d) => d + 1), 1000)
    } catch (err) {
      setStatus('error')
      setErrorMsg('Could not access microphone. You can use the text form instead.')
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop()
  }

  function reset() {
    setStatus('idle')
    setDurationSec(0)
    onRecorded(null)
  }

  const mm = String(Math.floor(durationSec / 60)).padStart(2, '0')
  const ss = String(durationSec % 60).padStart(2, '0')

  return (
    <div className="voice-recorder">
      {status !== 'recording' && status !== 'recorded' && (
        <button
          type="button"
          className="mic-button"
          onClick={startRecording}
          disabled={disabled}
          aria-label="Start voice recording"
        >
          <MicIcon />
        </button>
      )}

      {status === 'recording' && (
        <button
          type="button"
          className="mic-button mic-button--active"
          onClick={stopRecording}
          aria-label="Stop recording"
        >
          <span className="mic-pulse" />
          <StopIcon />
        </button>
      )}

      {status === 'recorded' && (
        <button
          type="button"
          className="mic-button mic-button--done"
          onClick={reset}
          aria-label="Re-record"
        >
          <CheckIcon />
        </button>
      )}

      <div className="voice-status">
        {status === 'idle' && <span>Tap to speak your report, in any language</span>}
        {status === 'recording' && <span className="voice-timer">{mm}:{ss} — tap to stop</span>}
        {status === 'recorded' && <span>Recorded — tap to re-record</span>}
        {status === 'error' && <span className="voice-error">{errorMsg}</span>}
      </div>
    </div>
  )
}

function MicIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path d="M12 15a3 3 0 003-3V6a3 3 0 10-6 0v6a3 3 0 003 3z" stroke="currentColor" strokeWidth="1.8" />
      <path d="M19 11a7 7 0 01-14 0M12 18v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}
function StopIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" />
    </svg>
  )
}
function CheckIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
