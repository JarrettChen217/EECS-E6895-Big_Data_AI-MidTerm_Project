import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const INTRO_STORAGE_KEY = 'eecs6895_intro_seen'

const QUESTIONS = [
  { key: 'adInfo', label: 'Ad Info', prompt: 'Please enter your Ad Info (e.g. product, message, format).' },
  { key: 'budget', label: 'Budget', prompt: 'Please enter your Budget (e.g. $500/month).' },
  { key: 'targetAudience', label: 'Target Audience', prompt: 'Please enter your Target Audience (e.g. age, interests, region).' },
]

function IntroScreen({ onEnter }) {
  const [exiting, setExiting] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => {
      setExiting(true)
      setTimeout(() => {
        try {
          localStorage.setItem(INTRO_STORAGE_KEY, '1')
        } catch (_) {}
        onEnter()
      }, 400)
    }, 2800)
    return () => clearTimeout(t)
  }, [onEnter])

  const handleSkip = () => {
    setExiting(true)
    setTimeout(() => {
      try {
        localStorage.setItem(INTRO_STORAGE_KEY, '1')
      } catch (_) {}
      onEnter()
    }, 400)
  }

  return (
    <div className={`intro ${exiting ? 'intro--exit' : ''}`} role="presentation">
      <div className="intro__bg" />
      <div className="intro__content">
        <span className="intro__course">EECS 6895</span>
        <h1 className="intro__title">Advanced AI Project</h1>
        <p className="intro__subtitle">Ad Advice</p>
        <div className="intro__bar">
          <div className="intro__bar-fill" />
        </div>
      </div>
      <button
        type="button"
        className="intro__skip"
        onClick={handleSkip}
        aria-label="Skip intro"
      >
        Enter
      </button>
    </div>
  )
}

export default function App() {
  const [showIntro, setShowIntro] = useState(() => {
    try {
      return !localStorage.getItem(INTRO_STORAGE_KEY)
    } catch {
      return true
    }
  })
  const [step, setStep] = useState(0)
  const [adInfo, setAdInfo] = useState('')
  const [budget, setBudget] = useState('')
  const [targetAudience, setTargetAudience] = useState('')
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [reply, setReply] = useState(null)
  const threadEndRef = useRef(null)

  const currentQuestion = QUESTIONS[step]
  const isDone = step >= QUESTIONS.length
  const isSubmitting = step === QUESTIONS.length && loading
  const hasReply = reply !== null && reply !== ''

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [step, adInfo, budget, targetAudience, loading, reply])

  const sendInput = async () => {
    const text = input.trim()
    if (!text || (isDone && !isSubmitting && !hasReply)) return
    if (isSubmitting) return

    if (step === 0) {
      setAdInfo(text)
      setInput('')
      setStep(1)
      return
    }
    if (step === 1) {
      setBudget(text)
      setInput('')
      setStep(2)
      return
    }
    if (step === 2) {
      setTargetAudience(text)
      setInput('')
      setStep(3)
      setLoading(true)
      setError(null)
      setReply(null)

      const message = `Ad Info: ${adInfo}\nBudget: ${budget}\nTarget Audience: ${text}`

      try {
        const res = await fetch('/api/agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: message }),
        })
        const resText = await res.text()
        let data
        try {
          data = resText ? JSON.parse(resText) : {}
        } catch {
          throw new Error(
            res.ok
              ? 'Backend returned invalid JSON.'
              : `Request failed (${res.status}). Is the server running?`
          )
        }
        if (!res.ok) {
          throw new Error(data.error || `Request failed: ${res.status}`)
        }
        setReply(data.reply ?? '')
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendInput()
    }
  }

  const canSend = input.trim() !== '' && !(step === 2 && loading)

  return (
    <>
      {showIntro && (
        <IntroScreen onEnter={() => setShowIntro(false)} />
      )}
      <div className="app">
        <aside className="sidebar">
          <div className="sidebar__brand">
            <span className="sidebar__course">EECS 6895</span>
            <h1 className="sidebar__title">Advanced AI Project</h1>
          </div>
          <p className="sidebar__desc">
            Answer the three questions one by one in the chat below: Ad Info, Budget, and Target Audience.
          </p>
          <div className="sidebar__footer">
            <span className="sidebar__hint">Enter to send</span>
          </div>
        </aside>

        <main className="main">
          <div className="thread" role="log" aria-live="polite">
            {step >= 0 && (
              <div className="block block--assistant">
                <div className="block__label">Assistant</div>
                <div className="block__body">
                  <div className="block__content">{QUESTIONS[0].prompt}</div>
                </div>
              </div>
            )}
            {adInfo && (
              <>
                <div className="block block--user">
                  <div className="block__label">You (Ad Info)</div>
                  <div className="block__body">{adInfo}</div>
                </div>
                <div className="block block--assistant">
                  <div className="block__label">Assistant</div>
                  <div className="block__body">
                    <div className="block__content">{QUESTIONS[1].prompt}</div>
                  </div>
                </div>
              </>
            )}
            {budget && (
              <>
                <div className="block block--user">
                  <div className="block__label">You (Budget)</div>
                  <div className="block__body">{budget}</div>
                </div>
                <div className="block block--assistant">
                  <div className="block__label">Assistant</div>
                  <div className="block__body">
                    <div className="block__content">{QUESTIONS[2].prompt}</div>
                  </div>
                </div>
              </>
            )}
            {targetAudience && (
              <div className="block block--user">
                <div className="block__label">You (Target Audience)</div>
                <div className="block__body">{targetAudience}</div>
              </div>
            )}
            {loading && (
              <div className="block block--assistant">
                <div className="block__label">Assistant</div>
                <div className="block__body block__body--loading">
                  <span className="typing" aria-hidden>
                    <span></span><span></span><span></span>
                  </span>
                </div>
              </div>
            )}
            {hasReply && (
              <div className="block block--assistant">
                <div className="block__label">Response</div>
                <div className="block__body">
                  <div className="block__content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{reply ?? ''}</ReactMarkdown>
                  </div>
                </div>
              </div>
            )}
            <div ref={threadEndRef} />
          </div>

          <div className="composer">
            {error && (
              <div className="composer__error" role="alert">
                {error}
              </div>
            )}
            <div className="composer__bar">
              <textarea
                className="composer__input"
                placeholder={
                  isSubmitting || hasReply
                    ? 'Start over by refreshing the page.'
                    : currentQuestion
                      ? `Enter your ${currentQuestion.label}...`
                      : 'Enter your answer...'
                }
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={loading || hasReply}
                aria-label={currentQuestion ? currentQuestion.label : 'Message'}
              />
              <button
                type="button"
                className="composer__send"
                onClick={sendInput}
                disabled={!canSend || loading || hasReply}
                aria-label="Send"
              >
                Send
              </button>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
