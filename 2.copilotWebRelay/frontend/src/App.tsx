import { useEffect, useRef, useState } from 'react'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import './App.css'

type ConnectionStatus = 'disconnected' | 'connected' | 'error'

function App() {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const [sessionActive, setSessionActive] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const terminalRef = useRef<HTMLDivElement>(null)
  const termRef = useRef<Terminal | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)

  // WebSocket接続
  useEffect(() => {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${location.host}/ws`)
    wsRef.current = ws

    ws.onopen = () => {
      if (wsRef.current === ws) {
        setStatus('connected')
      }
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'output') {
        termRef.current?.write(data.payload)
      } else if (data.type === 'status') {
        setSessionActive(data.state === 'running')
      }
    }

    ws.onclose = () => {
      if (wsRef.current === ws) {
        setStatus('disconnected')
        setSessionActive(false)
      }
    }

    ws.onerror = () => {
      if (wsRef.current === ws) {
        setStatus('error')
      }
    }

    return () => {
      wsRef.current = null
      ws.close()
    }
  }, [])

  // xterm.js初期化
  useEffect(() => {
    if (!terminalRef.current) return

    const terminal = new Terminal({
      cursorBlink: true,
      theme: { background: '#1e1e1e' },
      fontSize: 14,
    })
    const fitAddon = new FitAddon()
    terminal.loadAddon(fitAddon)
    terminal.open(terminalRef.current)
    fitAddon.fit()

    termRef.current = terminal
    fitAddonRef.current = fitAddon

    terminal.onData((data) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'input', payload: data }))
      }
    })

    const handleResize = () => {
      fitAddon.fit()
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'resize',
            cols: terminal.cols,
            rows: terminal.rows,
          })
        )
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      terminal.dispose()
    }
  }, [])

  const handleStartSession = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN && termRef.current) {
      wsRef.current.send(
        JSON.stringify({
          type: 'session',
          action: 'start',
          cols: termRef.current.cols,
          rows: termRef.current.rows,
        })
      )
    }
  }

  const handleStopSession = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'session', action: 'stop' }))
    }
  }

  return (
    <div className="app">
      <div className="toolbar">
        <span className="title">Copilot Web Relay</span>
        <span className={`indicator ${status}`} data-status={status} />
        <span className="status-text">{status}</span>
        <div className="spacer" />
        {sessionActive ? (
          <button
            className="btn btn-stop"
            onClick={handleStopSession}
            disabled={status !== 'connected'}
          >
            Stop Session
          </button>
        ) : (
          <button
            className="btn btn-start"
            onClick={handleStartSession}
            disabled={status !== 'connected'}
          >
            Start Session
          </button>
        )}
      </div>
      <div className="terminal-container" ref={terminalRef} />
    </div>
  )
}

export default App
