import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'

const ROLE_USER = 'user'

/** Wrap RAG citation patterns [doc_id] in spans for styling. Skips markdown links [text](url).
 *  Matches both exact doc_ids ([meta_policy_health]) and human-style refs ([Google CPC benchmark]). */
function wrapCitations(text) {
  return String(text).replace(
    /\[([a-zA-Z0-9_.\-][a-zA-Z0-9_.\- ]*)\](?!\s*\()/g,
    '<span class="citation" data-ref="$1" title="Cited source"><span class="citation__icon" aria-hidden="true"></span>[$1]</span>'
  )
}
const ROLE_ASSISTANT = 'assistant'
const INTRO_STORAGE_KEY = 'eecs6895_intro_seen'

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
        <p className="intro__subtitle">Ad Advice Chat</p>
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
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessageToChat = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMessage = { role: ROLE_USER, content: text }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError(null)

    const conversationSoFar = [...messages, userMessage].map((m) => ({
      role: m.role,
      content: m.content,
    }))

    try {
      const res = await fetch('/api/advice-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: conversationSoFar }),
      })
      const resText = await res.text()
      let data
      try {
        data = resText ? JSON.parse(resText) : {}
      } catch {
        throw new Error(
          res.ok
            ? 'Backend returned invalid JSON.'
            : `Request failed (${res.status}). Is the server running on port 5000?`
        )
      }

      if (!res.ok) {
        throw new Error(data.error || `Request failed: ${res.status}`)
      }

      const reply = data.reply ?? ''
      setMessages((prev) => [...prev, { role: ROLE_ASSISTANT, content: reply }])
    } catch (err) {
      setError(err.message)
      setMessages((prev) => [
        ...prev,
        { role: ROLE_ASSISTANT, content: `Error: ${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  const sendMessageToAgent = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMessage = { role: ROLE_USER, content: text }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError(null)

    const conversationSoFar = [...messages, userMessage].map((m) => ({
      role: m.role,
      content: m.content,
    }))

    try {
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, messages: conversationSoFar }),
      })
      const resText = await res.text()
      let data
      try {
        data = resText ? JSON.parse(resText) : {}
      } catch {
        throw new Error(
          res.ok
            ? 'Backend returned invalid JSON.'
            : `Request failed (${res.status}). Is the server running on port 5000?`
        )
      }

      if (!res.ok) {
        throw new Error(data.error || `Request failed: ${res.status}`)
      }

      const reply =
        data.reply ??
        data.final_answer ??
        (typeof data === 'string' ? data : '')
      const assistantMsg = { role: ROLE_ASSISTANT, content: reply }
      if (data.campaign_image_url) assistantMsg.campaign_image_url = data.campaign_image_url
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      setError(err.message)
      setMessages((prev) => [
        ...prev,
        { role: ROLE_ASSISTANT, content: `Error: ${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessageToChat()
    }
  }

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
          Ask about advertising, platform policies, budgets, and compliance.
        </p>
        <div className="sidebar__footer">
          <span className="sidebar__hint">Enter to send · Shift+Enter new line</span>
        </div>
      </aside>

      <main className="main">
        <div className="thread" role="log" aria-live="polite">
          {messages.length === 0 && (
            <div className="welcome">
              <div className="welcome__icon" aria-hidden>🧸</div>
              <p className="welcome__text">Start a conversation — type your question below.</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`block block--${msg.role}`}
              data-role={msg.role}
            >
              <div className="block__label">{msg.role === ROLE_USER ? 'You' : 'Assistant'}</div>
              <div className="block__body">
                <div className="block__content">
                  {msg.content != null && String(msg.content).trim() ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                      {wrapCitations(msg.content)}
                    </ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.campaign_image_url && (
                  <div className="block__campaign-image">
                    <img src={msg.campaign_image_url} alt="Ad campaign creative" />
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="block block--assistant" data-role="assistant">
              <div className="block__label">Assistant</div>
              <div className="block__body block__body--loading">
                <span className="typing" aria-hidden>
                  <span></span><span></span><span></span>
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="composer">
          {error && (
            <div className="composer__error" role="alert">
              {error}
            </div>
          )}
          <div className="composer__bar">
            <textarea
              ref={textareaRef}
              className="composer__input"
              placeholder="Ask about ad policies, budgets, or platforms..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
              aria-label="Message"
            />
            <button
              type="button"
              className="composer__send"
              onClick={sendMessageToChat}
              disabled={loading || !input.trim()}
              aria-label="Send"
            >
              Send
            </button>
            <button
              type="button"
              className="composer__send composer__send--agent"
              onClick={sendMessageToAgent}
              disabled={loading || !input.trim()}
              aria-label="Send to Agent"
            >
              Ask Agent
            </button>
          </div>
        </div>
      </main>
    </div>
    </>
  )
}
