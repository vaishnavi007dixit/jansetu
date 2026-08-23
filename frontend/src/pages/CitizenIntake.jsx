import { useState } from 'react'
import VoiceRecorder from '../components/VoiceRecorder.jsx'
import { submitRequest, pollRequestUntilDone } from '../api.js'

const MODES = [
  { id: 'voice', label: 'Speak' },
  { id: 'text', label: 'Type' },
  { id: 'chat', label: 'Chat' },
]

export default function CitizenIntake() {
  const [mode, setMode] = useState('voice')
  const [text, setText] = useState('')
  const [audioBase64, setAudioBase64] = useState(null)
  const [placeName, setPlaceName] = useState('')
  const [phase, setPhase] = useState('form') // form | submitting | processing | done | error
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')

  const canSubmit =
    (mode === 'text' || mode === 'chat' ? text.trim().length > 0 : !!audioBase64) &&
    phase === 'form'

  async function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return

    setPhase('submitting')
    setErrorMsg('')

    const payload = {
      source: mode === 'chat' ? 'chat' : mode,
      input_type: mode === 'voice' ? 'audio' : 'text',
      ...(mode === 'voice' ? { audio_base64: audioBase64 } : { text }),
      reported_location: placeName ? { place_name: placeName } : undefined,
    }

    try {
      const { request_id } = await submitRequest(payload)
      setPhase('processing')
      const finalResult = await pollRequestUntilDone(request_id)
      if (finalResult.status === 'done') {
        setResult(finalResult)
        setPhase('done')
      } else {
        setErrorMsg("Still processing — this can take a moment. Your report was received.")
        setPhase('error')
      }
    } catch (err) {
      setErrorMsg(err.message || 'Something went wrong. Please try again.')
      setPhase('error')
    }
  }

  function resetForm() {
    setPhase('form')
    setText('')
    setAudioBase64(null)
    setPlaceName('')
    setResult(null)
    setErrorMsg('')
  }

  if (phase === 'done' && result) {
    return <Confirmation result={result} onNewReport={resetForm} />
  }

  return (
    <div className="intake-page">
      <div className="intake-layout">
        <div className="intake-main">
          <div className="intake-hero">
            <span className="intake-eyebrow">Citizen reporting</span>
            <h1>Report an infrastructure problem</h1>
            <p>Bad road, no water, power cuts, blocked drains — tell us in your own words. Voice, text, or chat, whichever is easiest.</p>
          </div>

          <div className="mode-tabs" role="tablist">
            {MODES.map((m) => (
              <button
                key={m.id}
                role="tab"
                aria-selected={mode === m.id}
                className={mode === m.id ? 'mode-tab active' : 'mode-tab'}
                onClick={() => setMode(m.id)}
                disabled={phase !== 'form'}
              >
                {m.label}
              </button>
            ))}
          </div>

          <form className="intake-card" onSubmit={handleSubmit}>
            {mode === 'voice' && (
              <VoiceRecorder onRecorded={setAudioBase64} disabled={phase !== 'form'} />
            )}

            {mode === 'text' && (
              <textarea
                className="intake-textarea"
                placeholder="e.g. There has been no water supply on our street for five days"
                value={text}
                onChange={(e) => setText(e.target.value)}
                disabled={phase !== 'form'}
                rows={5}
              />
            )}

            {mode === 'chat' && (
              <ChatMock text={text} setText={setText} disabled={phase !== 'form'} />
            )}

            <label className="intake-field">
              <span>Location (optional)</span>
              <input
                type="text"
                placeholder="e.g. Sector 15, Rohini"
                value={placeName}
                onChange={(e) => setPlaceName(e.target.value)}
                disabled={phase !== 'form'}
              />
            </label>

            <button type="submit" className="btn-primary" disabled={!canSubmit}>
              {phase === 'form' && 'Submit report'}
              {phase === 'submitting' && 'Sending…'}
              {phase === 'processing' && 'Processing your report…'}
            </button>

            {phase === 'error' && (
              <p className="intake-error">{errorMsg}</p>
            )}
          </form>
        </div>

        <aside className="intake-side">
          <div className="side-panel">
            <h3>What happens next</h3>
            <ol className="side-steps">
              <li>
                <span className="side-step-num">1</span>
                <div>
                  <strong>Transcribed &amp; translated</strong>
                  <p>Voice reports are transcribed and translated automatically, in your language.</p>
                </div>
              </li>
              <li>
                <span className="side-step-num">2</span>
                <div>
                  <strong>Categorized &amp; located</strong>
                  <p>Your report is tagged by issue type and matched to a location.</p>
                </div>
              </li>
              <li>
                <span className="side-step-num">3</span>
                <div>
                  <strong>Clustered with others</strong>
                  <p>Grouped with nearby reports of the same problem to show real scale.</p>
                </div>
              </li>
              <li>
                <span className="side-step-num">4</span>
                <div>
                  <strong>Ranked for policymakers</strong>
                  <p>Surfaced on the priority dashboard, with the reasoning shown alongside it.</p>
                </div>
              </li>
            </ol>
          </div>

          <div className="side-panel side-panel--note">
            <p className="side-note-label">Why one shared pipeline</p>
            <p>Voice, text, and chat all reach the same backend. Any future channel — WhatsApp, IVR, SMS — can plug in without changing how reports get processed.</p>
          </div>
        </aside>
      </div>
    </div>
  )
}

function ChatMock({ text, setText, disabled }) {
  return (
    <div className="chat-mock">
      <div className="chat-bubble chat-bubble--system">
        Namaste 🙏 What problem would you like to report today?
      </div>
      <textarea
        className="chat-input"
        placeholder="Type your reply…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        rows={3}
      />
      <p className="chat-note">This mocks a WhatsApp-style conversation — same submission pipeline underneath.</p>
    </div>
  )
}

function Confirmation({ result, onNewReport }) {
  return (
    <div className="confirmation-card">
      <div className="confirmation-badge">✓</div>
      <h2>Your report has been logged</h2>
      <dl className="confirmation-details">
        <div>
          <dt>Category</dt>
          <dd className="mono-tag">{result.category}</dd>
        </div>
        <div>
          <dt>District</dt>
          <dd>{result.district}</dd>
        </div>
        <div>
          <dt>What we understood</dt>
          <dd>{result.translated_text}</dd>
        </div>
      </dl>
      {result.confirmation_audio_url && (
        <audio controls src={result.confirmation_audio_url} className="confirmation-audio" />
      )}
      <button className="btn-secondary" onClick={onNewReport}>Report another issue</button>
    </div>
  )
}
