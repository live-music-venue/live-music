import React from 'react'
import { render } from 'react-dom'
import io from 'socket.io-client'
import Peer from 'peerjs'
import _ from 'lodash'
import Webcam from 'react-webcam'
import ReactPlayer from 'react-player'
import { EyeOutlined } from '@ant-design/icons'

/* global data isAuthenticated */

let PORT = 3000
let props = {}
const container = document.querySelector('#react-event')

export default class Event extends React.Component {
  constructor () {
    super()
    props = JSON.parse(_.unescape(data))
    const djangoPort = Number(props.port)
    if (djangoPort !== 8000) PORT = djangoPort
    this.state = {
      isOwner: props.ownerId === props.userId,
      streaming: false,
      player: null,
      inProgress: props.in_progress,
      socket: null,
      peer: null,
      viewers: 0,
      chat: [],
      message: ''
    }
    this.startup = this.startup.bind(this)
  }

  componentWillUnmount () {
    this.state.socket.close()
  }

  async componentDidMount () {
    if (this.state.inProgress) this.startup()
    else container.removeAttribute('style')
  }

  async startup () {
    this.setState({
      inProgress: true
    })
    container.setAttribute('style', 'display: none;')
    document.getElementById('event-container').setAttribute('style', 'display: none;')
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
    const { socket, peer, isOwner } = this.state
    peer.on('open', peerId => {
      socket.emit('join_event', props.eventId, props.userId, peerId)
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
      if (isOwner) {
        const peers = {}
        navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        }).then(stream => {
          this.setState({
            viewers: 0,
            streaming: true,
            player: <Webcam audio='false' mirrored='true' />
          })
          container.removeAttribute('style')
          socket.on('user-connected', peerId => {
            const call = peer.call(peerId, stream)
            peers[peerId] = call
            socket.on('user-disconnected', peerId => {
              if (peers[peerId]) peers[peerId].close()
              delete peers[peerId]
            })
          })
        })
      } else {
        socket.on('host-connected', () => {
          document.getElementById('event-container').setAttribute('style', 'display: none;')
          this.setState({
            inProgress: true
          })
        })
        socket.on('host-disconnected', () => {
          this.setState({
            inProgress: false,
            player: null
          })
          document.getElementById('event-container').removeAttribute('style')
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
            socket.close()
          })
        })
      }
    })
    window.addEventListener('beforeunload', e => {
      socket.close()
    })
  }

  render () {
    const { isOwner, inProgress, viewers, player, socket, chat, message } = this.state
    let view = null
    if (isOwner && !inProgress) {
      view = (
        <>
          <button
            onClick={e => {
              this.startup()
            }}
          >
            Start Streaming
          </button>
        </>
      )
    } else if (inProgress) {
      view = (
        <>
          <div className='flex mt5 ml4'>
            <div className='flex flex-column'>
              {player}
              <p><EyeOutlined /> {viewers}</p>
            </div>
            <div>
              <div id='chat' className='pre bg-white pa2 bl bt br br0 bw1' style={{ whiteSpace: 'normal', width: 320, height: 452 }}>
                {chat.map((data, idx) => {
                  return (
                    <div key={idx} className={idx % 2 !== 0 ? 'bg-near-white' : 'bg-white'}>
                      <p style={{ overflowWrap: 'break-word' }}><span className={props.ownerId === data.userId ? 'blue' : 'black'}>{data.username}</span>{!!data.username && ':'} <span className={data.userId === 0 && 'red'}>{data.message}</span></p>
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
                  if (isAuthenticated) socket.emit('send_message', message)
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

if (container) render(<Event />, container)
