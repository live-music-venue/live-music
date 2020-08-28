import React from 'react'
import { render } from 'react-dom'
import io from 'socket.io-client'
import Peer from 'peerjs'
import _ from 'lodash'
import Webcam from 'react-webcam'
import ReactPlayer from 'react-player'

/* global data isAuthenticated MediaRecorder TextEncoder TextDecoder */

let PORT = 3000
const props = JSON.parse(_.unescape(data))
const container = document.querySelector('#react-event')

const encoder = new TextEncoder()
const decoder = new TextDecoder()

export default class Event extends React.Component {
  constructor () {
    super()
    const djangoPort = Number(props.port)
    if (djangoPort !== 8000) PORT = djangoPort
    this.state = {
      isOwner: props.ownerId === props.userId,
      streaming: false,
      recorder: null,
      recording: false,
      player: null,
      inProgress: props.inProgress,
      socket: null,
      peer: null,
      viewers: 0,
      chat: [],
      message: ''
    }
    this.joinStream = this.joinStream.bind(this)
    this.startStream = this.startStream.bind(this)
  }

  componentWillUnmount () {
    if (this.state.recorder) this.state.recorder.stop()
    this.state.socket.close()
  }

  async componentDidMount () {
    const secure = PORT !== 3000
    const hostname = secure ? 'rhappsody.herokuapp.com' : 'localhost'
    await this.setState({
      socket: io(`http${secure ? 's' : ''}://${hostname}${secure ? '' : `:${PORT}`}`),
      peer: new Peer({
        host: hostname,
        port: secure ? 443 : PORT,
        path: '/peer',
        secure: secure
      })
    })
    const { socket, peer, inProgress, isOwner } = this.state
    socket.emit('join_event', props.eventId, props.userId)
    socket.on('update-viewer-count', viewerCount => {
      this.setState({
        viewers: viewerCount
      })
    })
    socket.on('recieve-chat-message', (data) => {
      const chat = document.querySelector('#chat')
      this.setState({
        chat: this.state.chat.concat(data)
      })
      chat.scrollTop = chat.scrollHeight
    })
    if (!isOwner) {
      container.setAttribute('style', 'display: none;')
      peer.on('open', peerId => {
        if (inProgress) this.joinStream(peerId)
        socket.on('host-connected', () => {
          this.joinStream(peerId)
        })
        socket.on('host-disconnected', () => {
          this.setState({
            inProgress: false,
            player: null
          })
          document.getElementById('event-container').removeAttribute('style')
          document.getElementById('social-container').removeAttribute('style')
        })
      })
      peer.on('call', (call, id) => {
        call.answer()
        call.on('stream', stream => {
          this.setState({
            streaming: true,
            player: <ReactPlayer url={stream} playing muted controls width={640} height={480} onStart={e => { e.target.muted = false }} />
          })
          container.removeAttribute('style')
        })
        call.on('close', () => {
          if (this.state.recorder) this.state.recorder.stop()
          socket.close()
        })
      })
    }
    window.addEventListener('beforeunload', e => {
      if (this.state.recorder) this.state.recorder.stop()
      socket.close()
    })
  }

  joinStream (peerId) {
    document.getElementById('event-container').setAttribute('style', 'display: none;')
    document.getElementById('social-container').setAttribute('style', 'display: none;')
    this.setState({
      inProgress: true
    })
    const { socket } = this.state
    socket.emit('join_stream', encoder.encode(peerId))
  }

  startStream () {
    const { socket, peer } = this.state
    const peerId = peer.id
    navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    }).then(stream => {
      const peers = {}
      socket.on('user-connected', peerId => {
        const call = peer.call(peerId, stream)
        peers[peerId] = call
        socket.on('user-disconnected', peerId => {
          if (peers[peerId]) peers[peerId].close()
          delete peers[peerId]
        })
      })
      this.joinStream(peerId)
      if (props.shouldArchive) {
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'video/webm; codecs=vp8'
        })
        mediaRecorder.start(1000)
        mediaRecorder.onstart = e => {
          this.setState({ recorder: mediaRecorder })
          mediaRecorder.pause()
        }
        mediaRecorder.ondataavailable = e => {
          socket.emit('save_blob', e.data)
        }
      }
      this.setState({
        streaming: true,
        player: <Webcam audio='false' mirrored='true' />
      })
      container.removeAttribute('style')
    })
  }

  render () {
    const { isOwner, inProgress, recording, viewers, player, socket, chat, message } = this.state
    let view = null
    if (isOwner && !inProgress) {
      view = (
        <>
          <a
            href='#'
            onClick={e => {
              this.startStream()
            }}
          >
            Start Stream
          </a>
        </>
      )
    } else if (inProgress) {
      view = (
        <>
          <div className='flex center' style={{ marginTop: '10%', marginRight: '10%', marginLeft: '14%' }}>
            <div className='flex flex-column'>
              <div id='player-container'>
                {recording && <i id='recording-indicator' className='ml2 mt2 red fas fa-circle' />}
                {player}
              </div>
              <div>
                <span><i className='fas fa-eye' /> {viewers} </span>
                {isOwner && props.shouldArchive && (
                  <button
                    className='w4'
                    onClick={e => {
                      if (this.state.recording) {
                        this.state.recorder.pause()
                      } else {
                        this.state.recorder.resume()
                      }
                      this.setState({ recording: !recording })
                    }}
                  >
                    {`${recording ? 'Stop' : 'Start'}`} Recording
                  </button>
                )}
              </div>
            </div>
            <div>
              <div id='chat' className='pre bg-white pa2 bl bt br br0 bw1' style={{ whiteSpace: 'normal', width: 320, height: 452 }}>
                {chat.map((data, idx) => {
                  return (
                    <div key={idx} className={idx % 2 !== 0 ? 'bg-near-white' : 'bg-white'}>
                      <p style={{ overflowWrap: 'break-word' }}><span className={`b ${props.ownerId === data.userId ? 'blue' : 'black'}`}>{data.username}</span>{!!data.username && ':'} <span className={data.userId === 0 && 'red'}>{decoder.decode(data.message)}</span></p>
                    </div>
                  )
                })}
              </div>
              <input
                className='bl bb br0 bw1 outline-0'
                style={{ width: 271 }}
                type='text'
                value={message}
                onChange={e => {
                  if (e.target.value.length <= 255) this.setState({ message: e.target.value })
                }}
                onKeyPress={e => {
                  if (e.key === 'Enter') {
                    document.querySelector('#send-button').click()
                  }
                }}
              />
              <button
                id='send-button'
                className='br bb br0 bw1 outline-0'
                onClick={e => {
                  if (isAuthenticated) socket.emit('send_message', encoder.encode(message))
                  else this.setState({ chat: this.state.chat.concat({ userId: 0, username: null, message: 'You must be signed in to chat' }) })
                  this.setState({
                    message: ''
                  })
                }}
              >
                Send
              </button>
            </div>
          </div>
        </>
      )
    }
    return view
  }
}

if (props.isFinished && props.isArchived) {
  const imageContainer = document.querySelector('#event-image')
  imageContainer.firstChild.remove()
  render(<ReactPlayer url={props.archiveURL} playing controls width={640} height={480} />, imageContainer)
}
if (container) render(<Event />, container)
